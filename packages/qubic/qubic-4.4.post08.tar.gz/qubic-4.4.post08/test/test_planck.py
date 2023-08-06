from __future__ import division
from qubic import PlanckAcquisition
import numpy as np
import qubic

SKY = qubic.io.read_map(qubic.data.PATH + 'syn256_pol.fits')


def test():
    np.random.seed(0)
    acq = PlanckAcquisition(SKY)
    obs = acq.get_observation()
    invNtt = acq.get_invntt_operator()
    chi2_red = np.sum((obs - SKY) * invNtt(obs - SKY) / SKY.size)
    assert abs(chi2_red - 1) <= 0.001
