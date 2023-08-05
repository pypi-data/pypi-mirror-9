from hypothesis.internal.specmapper import SpecificationMapper
import hypothesis.searchstrategy as strat
from hypothesis.internal.compat import text_type, binary_type
import hypothesis.descriptors as descriptors
from random import Random


def convert_strategy(fn):
    if isinstance(fn, strat.SearchStrategy):
        return lambda strategies, descriptor: fn
    return fn


def strategy_for(typ):
    def accept_function(fn):
        StrategyTable.default().define_specification_for(
            typ, convert_strategy(fn))
        return fn
    return accept_function


def strategy_for_instances(typ):
    def accept_function(fn):
        StrategyTable.default().define_specification_for_instances(
            typ, convert_strategy(fn))
        return fn
    return accept_function


class StrategyTable(SpecificationMapper):

    def strategy(self, descriptor):
        return self.specification_for(descriptor)

strategy_for(int)(
    strat.RandomGeometricIntStrategy())
strategy_for(bool)(strat.BoolStrategy())


@strategy_for(text_type)
def define_text_type_strategy(strategies, descriptor):
    child = strategies.new_child_mapper()
    c = strat.OneCharStringStrategy()
    child.define_specification_for(
        text_type, lambda x, y: c)
    list_of_strings = child.strategy([text_type])
    return strat.StringStrategy(list_of_strings)


@strategy_for(float)
def define_float_strategy(strategies, descriptor):
    return (
        strat.GaussianFloatStrategy() |
        strat.BoundedFloatStrategy() |
        strat.ExponentialFloatStrategy())


@strategy_for(binary_type)
def define_binary_strategy(strategies, descriptor):
    return strat.BinaryStringStrategy(
        strategy=strategies.strategy([descriptors.integers_in_range(0, 255)]),
        descriptor=binary_type,
    )


@strategy_for_instances(set)
def define_set_strategy(strategies, descriptor):
    return strat.SetStrategy(strategies.strategy(list(descriptor)))


@strategy_for_instances(frozenset)
def define_frozen_set_strategy(strategies, descriptor):
    return strat.FrozenSetStrategy(strategies.strategy(list(descriptor)))


@strategy_for(complex)
def define_complex_strategy(strategies, descriptor):
    return strat.ComplexStrategy(strategies.strategy(float))


@strategy_for_instances(descriptors.Just)
def define_just_strategy(strategies, descriptor):
    return strat.JustStrategy(descriptor.value)


@strategy_for_instances(list)
def define_list_strategy(strategies, descriptor):
    return strat.ListStrategy(list(map(strategies.strategy, descriptor)))


@strategy_for_instances(tuple)
def define_tuple_strategy(strategies, descriptor):
    return strat.TupleStrategy(
        tuple(map(strategies.strategy, descriptor)),
        tuple_type=type(descriptor)
    )


@strategy_for_instances(dict)
def define_dict_strategy(strategies, descriptor):
    strategy_dict = {}
    for k, v in descriptor.items():
        strategy_dict[k] = strategies.strategy(v)
    return strat.FixedKeysDictStrategy(strategy_dict)


@strategy_for_instances(descriptors.OneOf)
def define_one_of_strategy(strategies, descriptor):
    return strat.OneOfStrategy(map(strategies.strategy, descriptor.elements))


@strategy_for_instances(strat.SearchStrategy)
def define_strategy_strategy(strategies, descriptor):
    return descriptor


@strategy_for_instances(descriptors.IntegerRange)
def define_stragy_for_integer_Range(strategies, descriptor):
    return strat.BoundedIntStrategy(descriptor.start, descriptor.end)


@strategy_for_instances(descriptors.FloatRange)
def define_strategy_for_float_Range(strategies, descriptor):
    return strat.FixedBoundedFloatStrategy(descriptor.start, descriptor.end)


@strategy_for(Random)
def define_random_strategy(strategies, descriptor):
    return strat.RandomStrategy()


@strategy_for_instances(descriptors.SampledFrom)
def define_sampled_strategy(strategies, descriptor):
    return strat.SampledFromStrategy(descriptor.elements)
