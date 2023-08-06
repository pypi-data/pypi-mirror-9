from __future__ import print_function, absolute_import
import os
import warnings

import numpy as np
import mdtraj as md

from ..utils.progressbar import ProgressBar, Percentage, Bar, ETA
from ..cmdline import NumpydocClassCommand, argument, exttype, stripquotestype
from ..dataset import dataset, MDTrajDataset
from ..featurizer import (AtomPairsFeaturizer, SuperposeFeaturizer,
                          DRIDFeaturizer, DihedralFeaturizer,
                          ContactFeaturizer, GaussianSolventFeaturizer)


class FeaturizerCommand(NumpydocClassCommand):
    _group = '1-Featurizer'
    trjs = argument(
        '--trjs', help='Glob pattern for trajectories',
        default='', required=True, type=stripquotestype)
    top = argument(
        '--top', help='Path to topology file matching the trajectories', default='')
    chunk = argument(
        '--chunk',
        help='''Chunk size for loading trajectories using mdtraj.iterload''',
        default=10000, type=int)
    out = argument(
        '--out',
        help='DEPRECATED: Output path. Please use --transformed',
        type=exttype('/'))
    transformed = argument(
        '--transformed',
        help="Output path for transformed data",
        type=exttype('/'))
    stride = argument(
        '--stride', default=1, type=int,
        help='Load only every stride-th frame')

    def _deprecation_logic(self):
        """Control deprecation of --out"""
        if self.out is None and self.transformed is None:
            self.error("Please specify --transformed")
        if self.transformed is None:
            warnings.warn("--out is deprecated. Please use --transformed")
            self.transformed = self.out

    def start(self):
        self._deprecation_logic()

        if os.path.exists(self.transformed):
            self.error('File exists: %s' % self.transformed)

        print(self.instance)
        if os.path.exists(os.path.expanduser(self.top)):
            top = os.path.expanduser(self.top)
        else:
            top = None

        input_dataset = MDTrajDataset(self.trjs, topology=top, stride=self.stride, verbose=False)
        out_dataset = input_dataset.create_derived(self.transformed, fmt='dir-npy')

        pbar = ProgressBar(widgets=[Percentage(), Bar(), ETA()],
                           maxval=len(input_dataset)).start()
        for key in pbar(input_dataset.keys()):
            trajectory = []
            for i, chunk in enumerate(input_dataset.iterload(key, chunk=self.chunk)):
                trajectory.append(self.instance.partial_transform(chunk))
            out_dataset[key] = np.concatenate(trajectory)
            out_dataset.close()

        print("\nSaving transformed dataset to '%s'" % self.transformed)
        print("To load this dataset interactive inside an IPython")
        print("shell or notebook, run\n")
        print("  $ ipython")
        print("  >>> from msmbuilder.dataset import dataset")
        print("  >>> ds = dataset('%s')\n" % self.transformed)


class DihedralFeaturizerCommand(FeaturizerCommand):
    _concrete = True
    klass = DihedralFeaturizer
    example = '''
    $ msmb DihedralFeaturizer --trjs './trajectories/*.h5' \\
        --transformed dihedrals-withchi --types phi psi chi1
    '''


class AtomPairsFeaturizerCommand(FeaturizerCommand):
    klass = AtomPairsFeaturizer
    _concrete = True

    def _pair_indices_type(self, fn):
        if fn is None:
            return None
        return np.loadtxt(fn, dtype=int, ndmin=2)


class SuperposeFeaturizerCommand(FeaturizerCommand):
    klass = SuperposeFeaturizer
    _concrete = True

    def _reference_traj_type(self, fn):
        return md.load(fn)

    def _atom_indices_type(self, fn):
        if fn is None:
            return None
        return np.loadtxt(fn, dtype=int, ndmin=1)


class DRIDFeaturizerCommand(FeaturizerCommand):
    klass = DRIDFeaturizer
    _concrete = True

    def _atom_indices_type(self, fn):
        if fn is None:
            return None
        return np.loadtxt(fn, dtype=int, ndmin=1)


class ContactFeaturizerCommand(FeaturizerCommand):
    _concrete = True
    klass = ContactFeaturizer

    def _contacts_type(self, val):
        if val is 'all':
            return val
        else:
            return np.loadtxt(val, dtype=int, ndmin=2)

class GaussianSolventFeaturizerCommand(FeaturizerCommand):
    _concrete = True
    klass = GaussianSolventFeaturizer

    def _solvent_indices_type(self, fn):
        return np.loadtxt(fn, dtype=int, ndmin=1)

    def _solute_indices_type(self, fn):
        return np.loadtxt(fn, dtype=int, ndmin=1)
