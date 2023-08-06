# coding=utf-8

# Copyright (C) 2013-2015 David R. MacIver (david@drmaciver.com)

# This file is part of Hypothesis (https://github.com/DRMacIver/hypothesis)

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

# END HEADER

"""This module provides the core primitives of Hypothesis, assume and given."""

from __future__ import division, print_function, absolute_import, \
    unicode_literals

import time
import inspect
import functools
from random import Random
from itertools import islice
from collections import namedtuple

from hypothesis.extra import load_entry_points
from hypothesis.errors import Flaky, Timeout, NoSuchExample, \
    Unsatisfiable, InvalidArgument, UnsatisfiedAssumption, \
    DefinitelyNoSuchExample
from hypothesis.control import assume
from hypothesis.settings import Settings
from hypothesis.executors import executor
from hypothesis.reporting import current_reporter
from hypothesis.specifiers import just
from hypothesis.internal.tracker import Tracker
from hypothesis.internal.reflection import arg_string, copy_argspec, \
    function_digest, get_pretty_function_description
from hypothesis.internal.examplesource import ParameterSource
from hypothesis.searchstrategy.strategies import BuildContext, strategy

[assume]


def time_to_call_it_a_day(settings, start_time):
    """Have we exceeded our timeout?"""
    if settings.timeout <= 0:
        return False
    return time.time() >= start_time + settings.timeout


def find_satisfying_template(
    search_strategy, random, condition, tracker, settings, storage=None
):
    """Attempt to find a template for search_strategy such that condition is
    truthy.

    Exceptions other than UnsatisfiedAssumption will be immediately propagated.
    UnsatisfiedAssumption will indicate that similar examples should be avoided
    in future.

    Returns such a template as soon as it is found, otherwise stops after
    settings.max_examples examples have been considered or settings.timeout
    seconds have passed (if settings.timeout > 0).

    May raise a variety of exceptions depending on exact circumstances, but
    these will all subclass either Unsatisfiable (to indicate not enough
    examples were found which did not raise UnsatisfiedAssumption to consider
    this a valid test) or NoSuchExample (to indicate that this probably means
    that condition is true with very high probability).

    """
    satisfying_examples = 0
    timed_out = False
    max_examples = settings.max_examples
    min_satisfying_examples = settings.min_satisfying_examples
    start_time = time.time()

    if storage:
        for example in storage.fetch():
            if time_to_call_it_a_day(settings, start_time):
                break
            tracker.track(example)
            try:
                if condition(example):
                    return example
                satisfying_examples += 1
            except UnsatisfiedAssumption:
                pass

    build_context = BuildContext(random)

    parameter_source = ParameterSource(
        context=build_context, strategy=search_strategy,
        min_parameters=max(2, int(float(max_examples) / 10))
    )

    for parameter in islice(
        parameter_source, max_examples - len(tracker)
    ):
        if len(tracker) >= search_strategy.size_upper_bound:
            break

        if time_to_call_it_a_day(settings, start_time):
            break

        example = search_strategy.produce_template(
            build_context, parameter
        )
        if tracker.track(example) > 1:
            parameter_source.mark_bad()
            continue
        try:
            if condition(example):
                return example
        except UnsatisfiedAssumption:
            parameter_source.mark_bad()
            continue
        satisfying_examples += 1
    run_time = time.time() - start_time
    timed_out = settings.timeout >= 0 and run_time >= settings.timeout
    if (
        satisfying_examples and
        len(tracker) >= search_strategy.size_lower_bound
    ):
        raise DefinitelyNoSuchExample(
            get_pretty_function_description(condition),
            satisfying_examples,
        )
    elif satisfying_examples < min_satisfying_examples:
        if timed_out:
            raise Timeout(condition, satisfying_examples, run_time)
        else:
            raise Unsatisfiable(
                condition, satisfying_examples, run_time)
    else:
        raise NoSuchExample(get_pretty_function_description(condition))


def simplify_template_such_that(search_strategy, random, t, f, tracker):
    """Perform a greedy search to produce a "simplest" version of a template
    that satisfies some predicate.

    Care is taken to avoid cycles in simplify.

    f should produce the same result deterministically. This function may
    raise an error given f such that f(t) returns False sometimes and True
    some other times.

    If f throws UnsatisfiedAssumption this will be treated the same as if
    it returned False.

    """
    assert isinstance(random, Random)

    yield t

    changed = True
    while changed:
        changed = False
        for simplify in search_strategy.simplifiers(t):
            while True:
                simpler = simplify(random, t)
                for s in simpler:
                    if tracker.track(s) > 1:
                        continue
                    try:
                        if f(s):
                            changed = True
                            yield s
                            t = s
                            break
                    except UnsatisfiedAssumption:
                        pass
                else:
                    break


def best_satisfying_template(
    search_strategy, random, condition, settings, storage, tracker=None
):
    """Find and then minimize a satisfying template.

    First look in storage if it is not None, then attempt to generate
    one. May throw all the exceptions of find_satisfying_template. Once
    an example has been found it will be further minimized.

    """
    if tracker is None:
        tracker = Tracker()
    start_time = time.time()

    satisfying_example = find_satisfying_template(
        search_strategy, random, condition, tracker, settings, storage
    )

    for simpler in simplify_template_such_that(
        search_strategy, random, satisfying_example, condition, tracker
    ):
        satisfying_example = simpler
        if time_to_call_it_a_day(settings, start_time):
            # It's very hard to reliably hit this line even though we have
            # tests for it. No cover prevents this from causing a flaky build.
            break  # pragma: no cover

    if storage is not None:
        storage.save(satisfying_example)

    return satisfying_example


def test_must_fail(test):
    @functools.wraps(test)
    def test_or_flaky(*args, **kwargs):
        test(*args, **kwargs)
        raise Flaky(test, (args, kwargs))
    return test_or_flaky


HypothesisProvided = namedtuple('HypothesisProvided', ('value,'))

Example = namedtuple('Example', ('args', 'kwargs'))


def example(*args, **kwargs):
    """Add an explicit example called with these args and kwargs to the
    test."""
    if args and kwargs:
        raise InvalidArgument(
            'Cannot mix positional and keyword arguments for examples'
        )
    if not (args or kwargs):
        raise InvalidArgument(
            'An example must provide at least one argument'
        )

    def accept(test):
        if not hasattr(test, 'hypothesis_explicit_examples'):
            test.hypothesis_explicit_examples = []
        test.hypothesis_explicit_examples.append(Example(tuple(args), kwargs))
        return test
    return accept


def reify_and_execute(search_strategy, template, test, print_example=False):
    def run():
        args, kwargs = search_strategy.reify(template)
        if print_example:
            current_reporter()(
                'Falsifying example: %s(%s)' % (
                    test.__name__,
                    arg_string(
                        test, args, kwargs
                    )
                )
            )
        return test(*args, **kwargs)
    return run


def given(*generator_arguments, **generator_kwargs):
    """A decorator for turning a test function that accepts arguments into a
    randomized test.

    This is the main entry point to Hypothesis. See the full tutorial
    for details of its behaviour.

    """

    # Keyword only arguments but actually supported in the full range of
    # pythons Hypothesis handles. pop so we don't later pick these up as
    # if they were keyword specifiers for data to pass to the test.
    provided_random = generator_kwargs.pop('random', None)
    settings = generator_kwargs.pop('settings', None) or Settings.default

    if (provided_random is not None) and settings.derandomize:
        raise InvalidArgument(
            'Cannot both be derandomized and provide an explicit random')

    if not (generator_arguments or generator_kwargs):
        raise InvalidArgument(
            'given must be called with at least one argument')

    def run_test_with_generator(test):
        if settings.derandomize:
            assert provided_random is None
            random = Random(
                function_digest(test)
            )
        else:
            random = provided_random or Random()

        original_argspec = inspect.getargspec(test)
        if original_argspec.varargs:
            raise InvalidArgument(
                'varargs are not supported with @given'
            )
        extra_kwargs = [
            k for k in generator_kwargs if k not in original_argspec.args]
        if extra_kwargs and not original_argspec.keywords:
            raise InvalidArgument(
                '%s() got an unexpected keyword argument %r' % (
                    test.__name__,
                    extra_kwargs[0]
                ))
        if (
            len(generator_arguments) > len(original_argspec.args)
        ):
            raise InvalidArgument((
                'Too many positional arguments for %s() (got %d but'
                ' expected at most %d') % (
                    test.__name__, len(generator_arguments),
                    len(original_argspec.args)))
        arguments = original_argspec.args + sorted(extra_kwargs)
        specifiers = list(generator_arguments)
        seen_kwarg = None
        for a in arguments:
            if a in generator_kwargs:
                seen_kwarg = seen_kwarg or a
                specifiers.append(generator_kwargs[a])
            else:
                if seen_kwarg is not None:
                    raise InvalidArgument((
                        'Argument %s comes after keyword %s which has been '
                        'specified, but does not itself have a '
                        'specification') % (
                        a, seen_kwarg
                    ))

        argspec = inspect.ArgSpec(
            args=arguments,
            keywords=original_argspec.keywords,
            varargs=original_argspec.varargs,
            defaults=tuple(map(HypothesisProvided, specifiers))
        )

        @copy_argspec(
            test.__name__, argspec
        )
        def wrapped_test(*arguments, **kwargs):
            selfy = None
            # Because we converted all kwargs to given into real args and
            # error if we have neither args nor kwargs, this should always
            # be valid
            assert argspec.args
            selfy = kwargs.get(argspec.args[0])
            if isinstance(selfy, HypothesisProvided):
                selfy = None
            test_runner = executor(selfy)

            for example in getattr(
                wrapped_test, 'hypothesis_explicit_examples', ()
            ):
                if example.args:
                    example_kwargs = dict(zip(
                        argspec.args[-len(example.args):], example.args
                    ))
                else:
                    example_kwargs = dict(example.kwargs)

                for k, v in kwargs.items():
                    if not isinstance(v, HypothesisProvided):
                        example_kwargs[k] = v

                test_runner(
                    lambda: test(*arguments, **example_kwargs)
                )

            if not any(
                isinstance(x, HypothesisProvided)
                for xs in (arguments, kwargs.values())
                for x in xs
            ):
                # All arguments have been satisfied without needing to invoke
                # hypothesis
                test_runner(lambda: test(*arguments, **kwargs))
                return

            def convert_to_specifier(v):
                if isinstance(v, HypothesisProvided):
                    return v.value
                else:
                    return just(v)

            given_specifier = (
                tuple(map(convert_to_specifier, arguments)),
                {k: convert_to_specifier(v) for k, v in kwargs.items()}
            )
            if settings.database:
                storage = settings.database.storage_for(given_specifier)
            else:
                storage = None

            search_strategy = strategy(given_specifier, settings)

            def is_template_example(xs):
                try:
                    test_runner(reify_and_execute(search_strategy, xs, test))
                    return False
                except UnsatisfiedAssumption as e:
                    raise e
                except Exception:
                    return True

            is_template_example.__name__ = test.__name__
            is_template_example.__qualname__ = getattr(
                test, '__qualname__', test.__name__)

            falsifying_template = None
            try:
                falsifying_template = best_satisfying_template(
                    search_strategy, random, is_template_example,
                    settings, storage
                )
            except NoSuchExample:
                return

            try:
                # We run this one final time so we get good errors
                # Otherwise we would have swallowed all the reports of it
                # actually having gone wrong.
                test_runner(reify_and_execute(
                    search_strategy, falsifying_template, test_must_fail(test),
                    print_example=True
                ))

            finally:
                # Some strategies use a weakref cache keyed off templates.
                # By cleaning up this template now we make it easier for python
                # to clear the cache early in some circumstances.
                del falsifying_template
        wrapped_test.__name__ = test.__name__
        wrapped_test.__doc__ = test.__doc__
        wrapped_test.is_hypothesis_test = True
        wrapped_test.hypothesis_explicit_examples = getattr(
            test, 'hypothesis_explicit_examples', []
        )
        return wrapped_test
    return run_test_with_generator


def find(specifier, condition, settings=None, random=None):
    settings = settings or Settings(
        max_examples=2000,
        min_satisfying_examples=0,
    )

    search = strategy(specifier, settings)
    random = random or Random()

    def template_condition(template):
        return assume(condition(search.reify(template)))

    template_condition.__name__ = condition.__name__
    tracker = Tracker()

    try:
        return search.reify(best_satisfying_template(
            search, random, template_condition, settings, None,
            tracker=tracker,
        ))
    except NoSuchExample:
        if search.size_upper_bound <= len(tracker):
            raise DefinitelyNoSuchExample(
                get_pretty_function_description(condition),
                search.size_upper_bound,
            )
        raise NoSuchExample(get_pretty_function_description(condition))


load_entry_points()
