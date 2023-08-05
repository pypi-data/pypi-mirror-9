# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

import nose
from nose.tools import *
from sknano.structures import filter_Ch, filter_Ch_list, generate_Ch_list, \
    generate_Ch_property_grid


def test_filter_Ch_list():
    Ch_list = generate_Ch_list(ni=5, nf=20, mi=0, mf=20, handedness='right')
    Ch_list = filter_Ch_list(Ch_list)
    assert_equal(len(Ch_list), 216)
    Ch_list = filter_Ch_list(Ch_list, property_filters=[('n', '<=', 10)])
    assert_equal(Ch_list, generate_Ch_list(ni=5, nf=10, mi=0, mf=20,
                                           handedness='right'))


def test_generate_Ch_list():
    Ch_list = generate_Ch_list(ni=5, nf=20, mi=0, mf=20, handedness='right')
    assert_equal(len(Ch_list), 216)

    Ch_list = generate_Ch_list(ni=5, imax=20, handedness='right')
    assert_equal(len(Ch_list), 216)


def test_generate_Ch_property_grid():
    Ch_grid = generate_Ch_property_grid(compute='compute_dt', imax=20)
    assert_equal(Ch_grid.shape, (21,21))


if __name__ == '__main__':
    nose.runmodule()
