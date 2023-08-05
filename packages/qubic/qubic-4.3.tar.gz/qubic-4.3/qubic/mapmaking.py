from __future__ import division

import healpy as hp
import numpy as np
from itertools import izip
from pyoperators import (
    asoperator, BlockColumnOperator, BlockDiagonalOperator, DiagonalOperator,
    MPIDistributionIdentityOperator, PackOperator, pcg, proxy_group,
    rule_manager)
from pysimulators.interfaces.healpy import HealpixLaplacianOperator
from .utils import progress_bar

__all__ = ['angular_distance_from_mask',
           'apodize_mask',
           'map2tod',
           'tod2map_all',
           'tod2map_each']


def angular_distance_from_mask(mask):
    """
    For each pixel of a Healpix map, return the smallest angular distance
    to a set of masked pixels (of value True), in degrees.

    Parameter
    ---------
    maskok : boolean Healpix map
        The Healpix mask that defines the set of masked pixels (of value True)
        whose smallest angular distance to each pixel of a Healpix map of same
        nside is computed.

    """
    nside = hp.npix2nside(len(mask))

    # get the list of pixels on the external border of the mask
    ip = np.arange(12*nside**2)[~mask]
    neigh = hp.get_all_neighbours(nside, ip)
    nn = np.unique(neigh.ravel())
    if nn[0] == -1:
        nn = nn[1:]
    nn = nn[mask[nn]]

    # get unit vectors for border and inner pixels
    vecpix_inner = np.array(hp.pix2vec(nside, ip))
    vecpix_outer = np.array(hp.pix2vec(nside, nn))

    # get angles between the border pixels and inner pixels
    cosang = np.dot(vecpix_inner.T, vecpix_outer)
    mapang = np.zeros(12*nside**2)
    mapang[~mask] = np.degrees(np.arccos(np.max(cosang, axis=1)))
    return mapang


def apodize_mask(maskok, fwhm_deg):
    """
    Apodize a mask.

    Parameters
    ----------
    maskok : boolean Healpix map
        The mask to be apodized (of value True).

    fwhm_deg : float
        The FWHM of the apodization function, counted from the mask edges,
        in degrees.

    """
    sigma_deg = fwhm_deg / np.sqrt(8 * np.log(2))
    mapang = angular_distance_from_mask(~maskok)
    return 1 - np.exp(-0.5 * mapang**2 / sigma_deg**2)


def _get_projection_restricted(acq, P, mask):
    #XXX HACK
    if len(acq.block) == 1:
        return P.restrict(mask, inplace=True)

    def callback(i):
        f = acq.instrument.get_projection_operator
        p = f(acq.sampling[acq.block[i]], acq.scene, verbose=False)
        return p.restrict(mask, inplace=True)
    shapeouts = [(len(acq.instrument), s.stop-s.start) +
                 acq.scene.shape[1:] for s in acq.block]
    proxies = proxy_group(len(acq.block), callback, shapeouts=shapeouts)
    return BlockColumnOperator(proxies, axisout=1)

#    nbytes = acq.get_projection_nbytes()
#    if max_nbytes is None or nbytes <= max_nbytes:
#        if acq.comm.size > 1:
#            P = P.operands[0]
#        if isinstance(P, BlockColumnOperator):
#            for _ in P.operands:
#                _.restrict(mask)
#        else:
#            P.restrict(mask)
#        return P
#    n = int(np.ceil(nbytes / max_nbytes))
#    samplings = acq.sampling.split(n)
#    acqs = [QubicAcquisition(acq.instrument, _, acq.scene, acq.block)
#            for _ in samplings]
#
#    def callback(i):
#        p = acqs[i].get_projection_operator(verbose=False)
#        p.restrict(mask)
#        return p
#    return BlockColumnOperator(proxy_group(n, callback), axisout=1)


def map2tod(acq, map, convolution=False, max_nbytes=None):
    """
    tod = map2tod(acquisition, map)
    tod, convolved_map = map2tod(acquisition, map, convolution=True)

    Parameters
    ----------
    acq : QubicAcquisition
        The QUBIC acquisition.
    map : I, QU or IQU maps
        Temperature, QU or IQU maps of shapes npix, (npix, 2), (npix, 3)
        with npix = 12 * nside**2
    convolution : boolean, optional
        Set to True to convolve the input map by a gaussian and return it.
    max_nbytes : int
        Maximum number of bytes for the pointing matrix. If the actual size
        is greater than this number, the computation of the pointing matrix
        will be performed on the fly at each iteration.

    Returns
    -------
    tod : array
        The Time-Ordered-Data of shape (ndetectors, ntimes).
    convolved_map : array
        The convolved map, if the convolution keyword is set.

    """
    if convolution:
        convolution = acq.get_convolution_peak_operator()
        map = convolution(map)

    H = acq.get_operator()
    tod = H(map)

    if convolution:
        return tod, map

    return tod


def _tod2map(acq, tod, coverage_threshold, disp_pmatrix, max_nbytes, callback,
             disp_pcg, maxiter, tol, _factor, criterion, full_output, save_map, hyper):
    projection = acq.get_projection_operator(verbose=disp_pmatrix)
    distribution = acq.get_distribution_operator()
    P = projection * distribution

    shape = len(acq.instrument), len(acq.sampling)
    kind = acq.scene.kind
    if kind == 'I':
        ones = np.ones(shape)
    elif kind == 'IQU':
        ones = np.zeros(shape + (3,))
        ones[..., 0] = 1
    else:
        raise NotImplementedError()
    coverage = P.T(ones)
    if kind == 'IQU':
        coverage = coverage[..., 0]
    cov = coverage[coverage > 0]
    i = np.argsort(cov)
    cdf = np.cumsum(cov[i])
    j = np.argmax(cdf >= coverage_threshold * cdf[-1])
    threshold = cov[i[j]]
    mask = coverage >= threshold
    if acq.comm.rank == 0 and coverage_threshold > 0:
        print 'Total coverage:', cdf[-1]
        print 'Threshold coverage set to:', threshold
        print 'Fraction of rejected pixels:', 1 - np.sum(mask) / cov.size

    projection = _get_projection_restricted(acq, projection, mask)
    pack = PackOperator(mask, broadcast='rightward')
    hwp = acq.get_hwp_operator()
    polarizer = acq.get_polarizer_operator()
    response = acq.get_detector_response_operator()
    H = response * polarizer * (hwp * projection) * distribution
    if acq.scene.kind == 'QU':
        H = acq.get_subtract_grid_operator() * H

    if _factor is not None:
        coef = np.array([1, _factor, _factor])
        H = H * DiagonalOperator(1 / coef, broadcast='leftward')

    invNtt = acq.get_invntt_operator()
    preconditioner = DiagonalOperator(1/coverage[mask], broadcast='rightward')
    nsamplings = acq.comm.allreduce(len(acq.sampling))
    npixels = np.sum(mask)

    A = H.T * invNtt * H / nsamplings
    if hyper != 0:
        L = HealpixLaplacianOperator(acq.scene.nside)
        L = L.restrict(mask, inplace=True).corestrict(mask, inplace=True)
        A = A - hyper / npixels / 4e5 * L

    if criterion:
        def f(x):
            Hx_y = H(x)
            Hx_y -= tod
            out = [np.dot(Hx_y.ravel(), invNtt(Hx_y).ravel()) / nsamplings]
            if hyper != 0:
                out += [-np.dot(x.ravel(),
                                hyper / npixels / 4e5 * L(x).ravel())]
            else:
                out += [0.]
            return out

        def callback(self):
            criteria = f(self.x)
            if len(criteria) == 1:
                details = ''
            else:
                fmt = ', '.join(len(criteria) * ['{:e}'])
                details = ' (' + fmt.format(*criteria) + ')'
            print('{:4}: {:e} {:e}{}'.format(self.niterations, self.error,
                                             sum(criteria), details))
            if not hasattr(self, 'history'):
                self.history = {}
                self.history['criterion'] = []
                self.history['error'] = []
                self.history['iteration'] = []
            self.history['criterion'].append(criteria)
            self.history['error'].append(self.error)
            self.history['iteration'].append(self.niterations)
            if save_map is not None and self.niterations in save_map:
                if not hasattr(self, 'xs'):
                    self.xs = {}
                self.xs[self.niterations] = self.x.copy()

    solution = pcg(A, H.T(invNtt(tod)) / nsamplings, M=preconditioner,
                   callback=callback, disp=disp_pcg, maxiter=maxiter, tol=tol)
    if _factor is not None:
        solution['x'] *= coef
    output = pack.T(solution['x']), coverage
    if full_output:
        algo = solution['algorithm']
        algo.H = H
        algo.pack = pack
        if criterion:
            algo.f = asoperator(f, shapeout=2)(pack)
        output += (algo,)
    return output


def tod2map_all(acquisition, tod, coverage_threshold=0.01, max_nbytes=None,
                callback=None, disp=True, maxiter=300, tol=1e-4, _factor=None,
                criterion=False, full_output=False, save_map=None, hyper=0):
    """
    Compute map using all detectors.

    map, coverage = tod2map_all(acquisition, tod, [coverage_threshold,
                                max_nbytes, callback, disp, tol])

    map, coverage, pcg = tod2map_all(acquisition, tod, [...], full_output=True)

    Parameters
    ----------
    acquisition : QubicAcquisition
        The QUBIC acquisition.
    tod : array-like
        The Time-Ordered-Data of shape (ndetectors, ntimes).
    coverage_threshold : float, optional
        The low-coverage sky pixels whose cumulative coverage is below a
        fraction of the total coverage are rejected. This keyword speficies
        this fraction (between 0 and 1]).
    max_nbytes : int
        Maximum number of bytes for the pointing matrix. If the actual size
        is greater than this number, the computation of the pointing matrix
        will be performed on the fly at each iteration.
    callback : function, optional
        User-supplied function to call after each iteration.  It is called
        as callback(solver), where solver is an Algorithm instance.
    disp : boolean, optional
        Display of solver's iterations.
    maxiter : integer, optional
        Maximum number of iterations.  Iteration will stop after maxiter
        steps even if the specified tolerance has not been achieved.
    tol : float, optional
        Solver tolerance.
    criterion : boolean, optional
        If True, also display the criterion at each iteration. It slows down
        the solving process.

    Returns
    -------
    map : I, QU or IQU maps
        Temperature, QU or IQU maps of shapes npix, (npix, 2), (npix, 3)
        with npix = 12 * nside**2
    """
    return _tod2map(acquisition, tod, coverage_threshold, True, max_nbytes,
                    callback, disp, maxiter, tol, _factor, criterion, full_output,
                    save_map, hyper)


def tod2map_each(acquisition, tod, coverage_threshold=0, max_nbytes=None,
                 callback=None, disp=True, maxiter=300, tol=1e-4, _factor=None):
    """
    Compute average map from each detector.

    map, coverage = tod2map_each(acquisition, tod, [coverage_threshold,
                                 max_nbytes, callback, disp, tol])

    Parameters
    ----------
    acquisition : QubicAcquisition
        The QUBIC acquisition.
    tod : array-like
        The Time-Ordered-Data of shape (ndetectors, ntimes).
    coverage_threshold : float, optional
        The coverage threshold used to reject map pixels from
        the reconstruction.
    max_nbytes : int
        Maximum number of bytes for the pointing matrix. If the actual size
        is greater than this number, the computation of the pointing matrix
        will be performed on the fly at each iteration.
    callback : function, optional
        User-supplied function to call after each iteration.  It is called
        as callback(solver), where solver is an Algorithm instance.
    disp : boolean, optional
        Display of solver's iterations.
    maxiter : integer, optional
        Maximum number of iterations.  Iteration will stop after maxiter
        steps even if the specified tolerance has not been achieved.
    tol : float, optional
        Solver tolerance.

    Returns
    -------
    map : I, QU or IQU maps
        Temperature, QU or IQU maps of shapes npix, (npix, 2), (npix, 3)
        with npix = 12 * nside**2

    """
    instrument = acquisition.instrument
    x = np.zeros(acquisition.scene.shape)
    n = np.zeros(acquisition.scene.shape[0])
    if disp:
        bar = progress_bar(len(instrument), 'TOD2MAP_EACH')
    for i, t in izip(instrument, tod):
        acq = type(acquisition)(i, acquisition.sampling, acquisition.scene)
        x_, n_ = _tod2map(acq, t[None, :], coverage_threshold, False,
                          max_nbytes, callback, False, maxiter, tol, _factor,
                          False)
        x += x_
        n += n_
        if disp:
            bar.update()

    if acquisition.scene.kind == 'I':
        return np.nan_to_num(x / n), n
    return np.nan_to_num(x / n[:, None]), n
