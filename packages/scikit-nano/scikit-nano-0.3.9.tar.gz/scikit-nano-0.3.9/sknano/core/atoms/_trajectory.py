# -*- coding: utf-8 -*-
"""
===============================================================================
Trajectory class for MD simulations (:mod:`sknano.core.atoms._trajectory`)
===============================================================================

Classes for analyzing the atom trajectories of molecular dynamics simulations.

.. currentmodule:: sknano.core.atoms._trajectory

"""
from __future__ import absolute_import, division, print_function
from six.moves import range
from six.moves import zip
__docformat__ = 'restructuredtext en'

#import numbers

import numpy as np

from operator import attrgetter

from sknano.core import UserList
from ._md_atom import MDAtom as Atom
from ._md_atoms import MDAtoms as Atoms

__all__ = ['Snapshot', 'Trajectory']


class aselect:
    def __init__(self, traj):
        self.traj = traj

    def all(self, *args):
        if len(args) == 0:
            for snapshot in self.traj:
                if not snapshot.tselect:
                    continue
                for i in range(snapshot.Natoms):
                    snapshot.aselect[i] = 1
                snapshot.nselect = snapshot.Natoms
        else:
            snapshot = self.traj[self.traj.findtimestep(args[0])]
            for i in range(snapshot.Natoms):
                snapshot.aselect[i] = 1
            snapshot.nselect = snapshot.Natoms


class tselect:
    def __init__(self, traj):
        self.traj = traj

    def all(self):
        traj = self.traj
        for snapshot in traj:
            snapshot.tselect = 1
        traj.nselect = len(traj)
        traj.aselect.all()
        print('{}/{} snapshots selected'.format(traj.nselect, traj.Nsnaps))

    def one(self, n):
        traj = self.traj
        for snapshot in traj:
            snapshot.tselect = 0
        i = traj.findtimestep(n)
        traj.snapshots[i].tselect = 1
        traj.nselect = 1
        traj.aselect.all()
        print('{}/{} snapshots selected'.format(traj.nselect, traj.Nsnaps))

    def none(self):
        traj = self.traj
        for snapshot in traj:
            snapshot.tselect = 0
        traj.nselect = 0
        print('{}/{} snapshots selected'.format(traj.nselect, traj.Nsnaps))

    def skip(self, n):
        traj = self.traj
        count = n - 1
        for snapshot in traj:
            if not snapshot.tselect:
                continue
            count += 1
            if count == n:
                count = 0
                continue
            snapshot.tselect = 0
            traj.nselect -= 1
        traj.aselect.all()
        print('{}/{} snapshots selected'.format(traj.nselect, traj.Nsnaps))


class Snapshot:
    """Container class for MD data at single timestep"""
    def __init__(self, trajectory=None):

        self.trajectory = trajectory

        self.atomattrs = None
        self.attr_dtypes = None
        self.timestep = None

        self._atoms = None

    @property
    def atoms(self):
        atoms = Atoms()
        for atom in self._atoms:
            try:
                reference_atom = \
                    self.trajectory.reference_atoms.get_atom(
                        int(atom[self.atomattrs.index('id')]))
            except AttributeError:
                reference_atom = None

            attrs = [dtype(value) for dtype, value in
                     zip(self.attr_dtypes, atom)]
            atoms.append(Atom(reference_atom=reference_atom,
                              **dict(list(zip(self.atomattrs, attrs)))))
        return atoms

    @atoms.setter
    def atoms(self, value):
        self._atoms = value

    def get_atoms(self, asarray=False):
        if asarray:
            return self._atoms
        return self.atoms


class Trajectory(UserList):
    """Base class for trajectory analysis."""

    def __init__(self, snapshots=None, copylist=True, deepcopy=False):
        super().__init__(initlist=snapshots, copylist=copylist,
                         deepcopy=deepcopy)
        self.tselect = tselect(self)
        self.aselect = aselect(self)
        self.nselect = 0
        self.reference_atoms = None
        self._reference_snapshot = None

    @property
    def Nsnaps(self):
        return len(self.data)

    def sort(self, key=None, reverse=False):
        if key is None:
            self.data.sort(key=attrgetter('timestep'), reverse=reverse)
        else:
            self.data.sort(key=key, reverse=reverse)

    def cull(self):
        i = 1
        while i < len(self.data):
            if self.data[i].timestep == self.data[i-1].timestep:
                del self.data[i]
            else:
                i += 1

    @property
    def reference_snapshot(self):
        return self._reference_snapshot

    @reference_snapshot.setter
    def reference_snapshot(self, value):
        if not isinstance(value, Snapshot):
            raise TypeError('Expected a `Snapshot` instance.')
        self._reference_snapshot = value
        self.reference_atoms = self.reference_snapshot.atoms
        self.reference_atoms.update_attrs()

    @property
    def timesteps(self):
        v = np.zeros(self.nselect, dtype=int)
        for i, snapshot in enumerate(self.data):
            if snapshot.tselect:
                v[i] = snapshot.timestep
        return v
