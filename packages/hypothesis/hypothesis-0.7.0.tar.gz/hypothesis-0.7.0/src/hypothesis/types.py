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


class RandomWithSeed(Random):

    """A subclass of Random designed to expose the seed it was initially
    provided with.

    We consistently use this instead of Random objects because it makes
    examples much easier to recreate.

    """

    def __init__(self, seed):
        super(RandomWithSeed, self).__init__(seed)
        self.seed = seed

    def __repr__(self):
        return 'RandomWithSeed(%s)' % (self.seed,)
