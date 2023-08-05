from __future__ import division

import healpy as hp
import matplotlib.pyplot as mp
import numpy as np
import os
import qubic
from qubic import (
    create_random_pointings, equ2gal, map2tod, QubicAcquisition,
    tod2map_all)

DATAPATH = os.path.join(os.path.dirname(qubic.__file__), 'data',
                        'syn256_pol.fits')

# acquisition parameters
nside = 256
racenter = 0.0      # deg
deccenter = -57.0   # deg
npointings = 100000
angular_radius = 10

# get the sampling model
np.random.seed(0)
sampling = create_random_pointings([racenter, deccenter], npointings,
                                   angular_radius)

# get the acquisition model
idetector = 0
acquisition = QubicAcquisition(150, sampling, nside=nside,
                               detector_sigma=1.)[idetector]

x0 = qubic.io.read_map(DATAPATH)
tod, x0_convolved = map2tod(acquisition, x0, convolution=True)
tod_noisy = tod + acquisition.get_noise()

#for hyper in (0, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1):
for hyper in (0.001,):
    output_map, coverage, pcg = tod2map_all(
        acquisition, tod_noisy, tol=1e-6, coverage_threshold=0, maxiter=100,
        full_output=True, criterion=True, hyper=hyper)

    # some display
    def display(input, msg, iplot=1):
        for i, (kind, lim) in enumerate(zip('IQU', [200, 10, 10])):
            map = input[..., i].copy()
            map[coverage == 0] = np.nan
            hp.gnomview(map, rot=center, reso=5, xsize=400, min=-lim, max=lim,
                        title=msg + ' ' + kind, sub=(3, 3, iplot + i))

    center = equ2gal(racenter, deccenter)

    mp.figure(1)
    mp.clf()
    display(x0_convolved, 'Original map', iplot=1)
    display(output_map, 'Reconstructed map', iplot=4)
    display(output_map-x0_convolved, 'Difference map', iplot=7)
    mp.savefig('maps_h{}.png'.format(hyper), dpi=300)

    mp.figure(2)
    mp.clf()
    criterion = np.array(pcg.history['criterion'])
    mp.semilogy(pcg.history['iteration'], criterion[..., 0], 'b')
    mp.semilogy(pcg.history['iteration'], criterion[..., 1], 'g')
    mp.semilogy(pcg.history['iteration'], np.sum(pcg.history['criterion'], axis=-1), 'r')
    criterion0 = pcg.f(x0_convolved)
    mp.axhline(criterion0[0], color='b')
    mp.axhline(criterion0[1], color='g')
    mp.axhline(np.sum(criterion0), color='r')
    mp.savefig('criterion_h{}.png'.format(hyper), dpi=300)
