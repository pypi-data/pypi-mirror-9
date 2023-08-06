# coding=utf-8

# Copyright (C) 2013-2015 David R. MacIver (david@drmaciver.com)

# This file is part of Hypothesis (https://github.com/DRMacIver/hypothesis)

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

# END HEADER

from __future__ import division, print_function, absolute_import, \
    unicode_literals

from random import Random

import hypothesis.specifiers as specifiers
import hypothesis.internal.distributions as dist
from hypothesis.types import RandomWithSeed
from hypothesis.utils.show import show
from hypothesis.internal.compat import integer_types
from hypothesis.searchstrategy.strategies import BadData, SearchStrategy, \
    strategy, check_type, check_data_type


class BoolStrategy(SearchStrategy):

    """A strategy that produces Booleans with a Bernoulli conditional
    distribution."""
    size_lower_bound = 2
    size_upper_bound = 2

    def __repr__(self):
        return 'BoolStrategy()'

    def reify(self, value):
        return value

    def produce_parameter(self, random):
        return random.random()

    def produce_template(self, context, p):
        return dist.biased_coin(context.random, p)

    def to_basic(self, value):
        check_type(bool, value)
        return int(value)

    def from_basic(self, value):
        check_data_type(int, value)
        return bool(value)


class JustStrategy(SearchStrategy):

    """
    A strategy which simply returns a single fixed value with probability 1.
    """
    size_lower_bound = 1
    size_upper_bound = 1

    def __init__(self, value):
        SearchStrategy.__init__(self)
        self.value = value

    def __repr__(self):
        return 'JustStrategy(value=%r)' % (self.value,)

    def produce_parameter(self, random):
        return None

    def produce_template(self, context, pv):
        return None

    def reify(self, template):
        assert template is None
        return self.value

    def to_basic(self, template):
        return None

    def from_basic(self, data):
        if data is not None:
            raise BadData('Expected None but got %s' % (show(data,)))
        return None


class RandomStrategy(SearchStrategy):

    """A strategy which produces Random objects.

    The conditional distribution is simply a RandomWithSeed seeded with
    a 128 bits of data chosen uniformly at random.

    """

    def from_basic(self, data):
        check_data_type(integer_types, data)
        return data

    def to_basic(self, template):
        return template

    def produce_parameter(self, random):
        return None

    def produce_template(self, context, pv):
        return context.random.getrandbits(128)

    def reify(self, template):
        return RandomWithSeed(template)


class SampledFromStrategy(SearchStrategy):

    """A strategy which samples from a set of elements. This is essentially
    equivalent to using a OneOfStrategy over Just strategies but may be more
    efficient and convenient.

    The conditional distribution chooses uniformly at random from some
    non-empty subset of the elements.

    """

    def __init__(self, elements):
        SearchStrategy.__init__(self)
        self.elements = tuple(elements)
        if not self.elements:
            raise ValueError(
                'SampledFromStrategy requires at least one element')
        try:
            s = set(self.elements)
            self.size_lower_bound = len(s)
            self.size_upper_bound = len(s)
        except TypeError:
            self.size_lower_bound = len(self.elements)
            self.size_upper_bound = len(self.elements)

    def to_basic(self, template):
        return template

    def from_basic(self, data):
        check_data_type(integer_types, data)
        if data < 0:
            raise BadData('Index out of range: %d < 0' % (data,))
        elif data >= len(self.elements):
            raise BadData(
                'Index out of range: %d >= %d' % (data, len(self.elements)))

        return data

    def __repr__(self):
        return 'SampledFromStrategy(%r)' % (self.elements,)

    def produce_parameter(self, random):
        return dist.non_empty_subset(random, range(len(self.elements)))

    def produce_template(self, context, pv):
        return context.random.choice(pv)

    def reify(self, template):
        return self.elements[template]


@strategy.extend_static(bool)
def bool_strategy(cls, settings):
    return BoolStrategy()


@strategy.extend(specifiers.Just)
def define_just_strategy(specifier, settings):
    return JustStrategy(specifier.value)


@strategy.extend_static(Random)
def define_random_strategy(specifier, settings):
    return RandomStrategy()


@strategy.extend(specifiers.SampledFrom)
def define_sampled_strategy(specifier, settings):
    return SampledFromStrategy(specifier.elements)


@strategy.extend(type(None))
@strategy.extend_static(type(None))
def define_none_strategy(specifier, settings):
    return JustStrategy(None)
