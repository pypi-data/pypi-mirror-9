from random import Random
from hypothesis.internal.compat import hrange


class ExampleSource(object):

    """An object that provides you with an a stream of examples to work with.

    Starts by fetching examples from storage if storage has been provided but
    if storage is None will happily continue without. Follows by generating new
    examples, but if the strategy is None then will stop there. Must have at
    least one of strategy and storage but does not have to have both.

    This does not handle deduplication or make decisions as to when to stop.
    That's up to the caller.

    """

    def __init__(self, random, strategy, storage, min_parameters=50):
        if not isinstance(random, Random):
            raise ValueError('A Random is required but got %r' % (random,))
        if strategy is None and storage is None:
            raise ValueError(
                'Cannot proceed without at least one way of getting examples'
            )
        self.strategy = strategy
        self.storage = storage
        self.random = random
        self.parameters = []
        self.last_parameter_index = -1
        self.min_parameters = min_parameters
        self.bad_counts = []
        self.counts = []
        self.is_new_parameter = True
        self.new_parameter_bad = 0
        self.mark_set = False
        self.started = False

    def mark_bad(self):
        """The last example was bad.

        If possible can we have less of that please?

        """
        if not self.started:
            raise ValueError('No examples have been generated yet')
        if self.mark_set:
            raise ValueError('This parameter has already been marked')
        self.mark_set = True
        if self.last_parameter_index < 0:
            return
        self.bad_counts[self.last_parameter_index] += 1
        if self.is_new_parameter:
            self.new_parameter_bad += 1

    def new_parameter(self):
        result = self.strategy.parameter.draw(self.random)
        self.parameters.append(result)
        self.bad_counts.append(0)
        self.counts.append(1)
        self.is_new_parameter = True
        return result

    def pick_a_parameter(self):
        self.mark_set = False
        if len(self.parameters) < self.min_parameters:
            return self.new_parameter()
        else:
            best_score = self.random.betavariate(
                len(self.parameters) - self.new_parameter_bad + 1,
                self.new_parameter_bad + 1,
            )
            best_index = -1

            for i in hrange(len(self.parameters)):
                beta = 1 + self.bad_counts[i]
                alpha = 1 + self.counts[i] - self.bad_counts[i]
                assert self.counts[i] > 0
                assert self.bad_counts[i] >= 0
                assert self.bad_counts[i] <= self.counts[i]

                score = self.random.betavariate(alpha, beta)
                if score > best_score:
                    best_score = score
                    best_index = i
            if best_index < 0:
                self.last_parameter_index = len(self.parameters)
                return self.new_parameter()
            self.is_new_parameter = False
            self.last_parameter_index = best_index
            self.counts[self.last_parameter_index] += 1
            return self.parameters[self.last_parameter_index]

    def __iter__(self):
        self.started = True
        if self.storage is not None:
            for example in self.storage.fetch():
                self.mark_set = False
                yield example

        if self.strategy is not None:
            while True:
                parameter = self.pick_a_parameter()
                yield self.strategy.produce(
                    self.random, parameter
                )
