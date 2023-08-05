# Copyright (c) 2014, Salesforce.com, Inc.  All rights reserved.
# Copyright (c) 2015, Gamelan Labs, Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# - Neither the name of Salesforce.com nor the names of its contributors
#   may be used to endorse or promote products derived from this
#   software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import numpy
from numpy import pi
from nose.tools import assert_almost_equal
from nose.tools import assert_equal
from nose.tools import assert_greater
from nose.tools import assert_less
from goftests import multinomial_goodness_of_fit
from goftests import split_discrete_continuous
from goftests import volume_of_sphere


def test_multinomial_goodness_of_fit():
    for dim in range(2, 20):
        yield _test_multinomial_goodness_of_fit, dim


def _test_multinomial_goodness_of_fit(dim):
    numpy.random.seed(0)
    thresh = 1e-3
    sample_count = int(1e5)
    probs = numpy.random.dirichlet([1] * dim)

    counts = numpy.random.multinomial(sample_count, probs)
    p_good = multinomial_goodness_of_fit(probs, counts, sample_count)
    assert_greater(p_good, thresh)

    unif_counts = numpy.random.multinomial(sample_count, [1. / dim] * dim)
    p_bad = multinomial_goodness_of_fit(probs, unif_counts, sample_count)
    assert_less(p_bad, thresh)


def test_volume_of_sphere():
    for r in [0.1, 1.0, 10.0]:
        assert_almost_equal(volume_of_sphere(1, r), 2.0 * r)
        assert_almost_equal(volume_of_sphere(2, r), pi * r ** 2)
        assert_almost_equal(volume_of_sphere(3, r), 4 / 3.0 * pi * r ** 3)


split_examples = [
    {'mixed': False, 'discrete': False, 'continuous': []},
    {'mixed': 0, 'discrete': 0, 'continuous': []},
    {'mixed': 'abc', 'discrete': 'abc', 'continuous': []},
    {'mixed': 0.0, 'discrete': None, 'continuous': [0.0]},
    {'mixed': (), 'discrete': (), 'continuous': []},
    {'mixed': [], 'discrete': (), 'continuous': []},
    {'mixed': (0,), 'discrete': (0, ), 'continuous': []},
    {'mixed': [0, ], 'discrete': (0, ), 'continuous': []},
    {'mixed': (0.0, ), 'discrete': (None, ), 'continuous': [0.0]},
    {'mixed': [0.0, ], 'discrete': (None, ), 'continuous': [0.0]},
    {
        'mixed': [True, 1, 'xyz', 3.14, [None, (), ([2.71],)]],
        'discrete': (True, 1, 'xyz', None, (None, (), ((None,),))),
        'continuous': [3.14, 2.71],
    },
    {
        'mixed': numpy.zeros(3),
        'discrete': (None, None, None),
        'continuous': [0.0, 0.0, 0.0],
    },
]


def split_example(i):
    example = split_examples[i]
    discrete, continuous = split_discrete_continuous(example['mixed'])
    assert_equal(discrete, example['discrete'])
    assert_almost_equal(continuous, example['continuous'])


def test_split_continuous_discrete():
    for i in xrange(len(split_examples)):
        yield split_example, i
