#! /usr/bin/env python

from __future__ import absolute_import, division, print_function
import nose
from nose.tools import *
import numpy as np

from sknano.core.math import Point, Vector, rotate, scale, translate, \
    Rx, Ry, Rz, reflection_matrix, rotation_matrix, transformation_matrix, \
    axis_angle_from_rotation_matrix

from six.moves import zip


def test_rotation_matrix():
    assert_true(np.allclose(rotation_matrix(angle=np.pi/2),
                            np.array([[0.0, -1.0], [1.0, 0.0]])))

    sqrt2 = np.sqrt(2)
    assert_true(np.allclose(rotation_matrix(angle=np.pi/4),
                            np.array([[1 / sqrt2, -1 / sqrt2],
                                      [1 / sqrt2, 1 / sqrt2]])))

    sqrt3 = np.sqrt(3)
    assert_true(np.allclose(
        rotation_matrix(angle=np.pi/2, rot_axis=Vector(np.ones(3))),
        np.array([[1 / 3, 1 / 3 - 1 / sqrt3, 1 / 3 + 1 / sqrt3],
                  [1 / 3 + 1 / sqrt3, 1 / 3, 1 / 3 - 1 / sqrt3],
                  [1 / 3 - 1 / sqrt3, 1 / 3 + 1 / sqrt3, 1 / 3]])))

    [[assert_true(np.allclose(
        Rmat(angle=angle), rotation_matrix(angle=angle, rot_axis=axis)))
        for angle in np.linspace(0.0, 2 * np.pi, np.pi / 4)]
        for Rmat, axis in zip((Rx, Ry, Rz), ('x', 'y', 'z'))]

    assert_true(np.allclose(rotation_matrix(angle=np.pi / 2),
                            rotation_matrix(from_vector=[1, 0],
                                            to_vector=[0, 1])))

    assert_true(np.allclose(rotation_matrix(angle=-np.pi / 2),
                            rotation_matrix(from_vector=[0, 1],
                                            to_vector=[1, 0])))

    assert_true(np.allclose(
        rotation_matrix(angle=np.pi / 2, rot_axis=[0, 0, 1]),
        rotation_matrix(from_vector=[1, 0, 0], to_vector=[0, 1, 0])))

    assert_true(np.allclose(
        rotation_matrix(angle=-np.pi / 2, rot_axis=[0, 0, 1]),
        rotation_matrix(from_vector=[0, 1, 0], to_vector=[1, 0, 0])))


def test_transformation_matrix():
    [[assert_true(np.allclose(
        Rz(angle=angle), transformation_matrix(angle=angle, rot_axis=axis)))
        for angle in np.linspace(0.0, 2 * np.pi, np.pi / 4)]
        for Rmat, axis in zip((Rx, Ry, Rz), ('x', 'y', 'z'))]
    assert_true(np.allclose(
        transformation_matrix(angle=np.pi/2, rot_point=Point([1.0, 1.0])),
        np.array([[0.0, -1.0, 2.0], [1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])))


def test_point_rotation():
    assert_true(np.allclose(
        rotate(Point([1.0, 0.0]), np.pi / 2),
        np.array([0.0, 1.0])))

    with assert_raises(TypeError):
        np.allclose(rotate(
            Point([1.0, 0.0, 0.0]), angle=np.pi/2),
            np.array([0.0, 1.0, 0.0]))

    assert_true(np.allclose(
        rotate(Point([1.0, 0.0, 0.0]), angle=np.pi/2,
               rot_axis=Vector([1.0, 0.0, 0.0])),
        np.array([1.0, 0.0, 0.0])))

    assert_true(np.allclose(
        rotate(Point([0.0, 1.0, 0.0]), angle=np.pi / 2,
               rot_axis=Vector([1.0, 0.0, 0.0])),
        np.array([0.0, 0.0, 1.0])))


def test_axis_angle_from_rotation_matrix():
    for angle in np.linspace(0.0, 2 * np.pi, np.pi / 4):
        for rmatrix in (Rx, Ry, Rz):
            rot_axis, rot_angle = \
                axis_angle_from_rotation_matrix(rmatrix(angle))
            assert_true(np.allclose(rotation_matrix(angle=rot_angle,
                                                    axis=rot_axis),
                                    rmatrix(angle)))


if __name__ == '__main__':
    nose.runmodule()
