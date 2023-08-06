# Author: Robert McGibbon <rmcgibbo@gmail.com>
# Contributors:
# Copyright (c) 2014, Stanford University and the Authors
# All rights reserved.

# -----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------
from __future__ import print_function, absolute_import, division

from glob import glob
from io import BytesIO
from os import makedirs
from os.path import exists
from os.path import join
from zipfile import ZipFile
from six.moves.urllib.request import urlopen

import mdtraj as md
from .base import Bunch, Dataset
from .base import get_data_home, retry

DATA_URL = "http://downloads.figshare.com/article/public/1026324"
TARGET_DIRECTORY = "met_enkephalin"


class MetEnkephalin(Dataset):
    """Loader for the met-enkephalin dataset

    Parameters
    ----------
    data_home : optional, default: None
        Specify another download and cache folder for the datasets. By default
        all MSMBuilder data is stored in '~/msmbuilder_data' subfolders.

    download_if_missing: optional, True by default
        If False, raise a IOError if the data is not locally available
        instead of trying to download the data from the source site.

    Notes
    -----
    The dataset consists of ten ~50 ns molecular dynamics (MD) simulation
    trajectories of the 5 residue Met-enkaphalin peptide. The aggregate
    sampling is 499.58 ns. Simulations were performed starting from the 1st
    model in the 1PLX PDB file, solvated with 832 TIP3P water molecules using
    OpenMM 6.0. The coordinates (protein only -- the water was stripped)
    are saved every 5 picoseconds. Each of the ten trajectories is roughly
    50 ns long and contains about 10,000 snapshots.

    Forcefield: amber99sb-ildn; water: tip3p; nonbonded method: PME; cutoffs:
    1nm; bonds to hydrogen were constrained; integrator: langevin dynamics;
    temperature: 300K; friction coefficient: 1.0/ps; pressure control: Monte
    Carlo barostat (interval of 25 steps); timestep 2 fs.

    The dataset is available on figshare at

    http://dx.doi.org/10.6084/m9.figshare.1026324
    """

    def __init__(self, data_home=None):
        self.data_home = get_data_home(data_home)
        self.data_dir = join(self.data_home, TARGET_DIRECTORY)
        self.cached = False

    @retry(3)
    def cache(self):
        if not exists(self.data_home):
            makedirs(self.data_home)

        if not exists(self.data_dir):
            print('downloading met-enk from %s to %s' %
                  (DATA_URL, self.data_dir))
            fhandle = urlopen(DATA_URL)
            buf = BytesIO(fhandle.read())
            zip_file = ZipFile(buf)
            makedirs(self.data_dir)
            for name in zip_file.namelist():
                zip_file.extract(name, path=self.data_dir)

        self.cached = True

    def get(self):
        if not self.cached:
            self.cache()

        top = md.load(join(self.data_dir, '1plx.pdb'))
        trajectories = []
        for fn in glob(join(self.data_dir, 'trajectory*.dcd')):
            trajectories.append(md.load(fn, top=top))

        return Bunch(trajectories=trajectories, DESCR=self.description())


def fetch_met_enkephalin(data_home=None):
    return MetEnkephalin(data_home).get()


fetch_met_enkephalin.__doc__ = MetEnkephalin.__doc__
