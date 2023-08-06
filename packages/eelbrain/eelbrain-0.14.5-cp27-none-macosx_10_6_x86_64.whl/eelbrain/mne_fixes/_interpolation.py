# Authors: Denis Engemann <denis.engemann@gmail.com>
#
# License: BSD (3-clause)

import numpy as np
from numpy.polynomial.legendre import legval
from scipy import linalg, optimize

from mne.utils import logger
from mne.io.pick import pick_types
from mne.surface import _normalize_vectors
# from mne.bem import _fit_sphere

# 0.8.6 not in mne.bem
def _fit_sphere(points, disp=True):
    """Aux function to fit points to a sphere"""
    # initial guess for center and radius
    xradius = (np.max(points[:, 0]) - np.min(points[:, 0])) / 2.
    yradius = (np.max(points[:, 1]) - np.min(points[:, 1])) / 2.

    radius_init = (xradius + yradius) / 2.
    center_init = np.array([0.0, 0.0, np.max(points[:, 2]) - radius_init])

    # optimization
    x0 = np.r_[center_init, radius_init]

    def cost_fun(x, points):
        return np.sum((np.sqrt(np.sum((points - x[:3]) ** 2, axis=1)) -
                      x[3]) ** 2)

    x_opt = optimize.fmin_powell(cost_fun, x0, args=(points,),
                                 disp=disp)

    origin = x_opt[:3]
    radius = x_opt[3]
    return radius, origin


# not in 0.8.6 (Epochs method)
def get_channel_positions(self, picks=None):
    """Gets channel locations from info

    Parameters
    ----------
    picks : array-like of int | None
        Indices of channels to include. If None (default), all meg and eeg
        channels that are available are returned (bad channels excluded).
    """
    if picks is None:
        picks = pick_types(self.info, meg=True, eeg=True)
    chs = self.info['chs']
    pos = np.array([chs[k]['loc'][:3] for k in picks])
    n_zero = np.sum(np.sum(np.abs(pos), axis=1) == 0)
    if n_zero > 1:  # XXX some systems have origin (0, 0, 0)
        raise ValueError('Could not extract channel positions for '
                         '{} channels'.format(n_zero))
    return pos


def _calc_g(cosang, stiffness=4, num_lterms=50):
    """Calculate spherical spline g function between points on a sphere.

    Parameters
    ----------
    cosang : array-like of float, shape(n_channels, n_channels)
        cosine of angles between pairs of points on a spherical surface. This
        is equivalent to the dot product of unit vectors.
    stiffness : float
        stiffness of the spline.
    num_lterms : int
        number of Legendre terms to evaluate.

    Returns
    -------
    G : np.ndrarray of float, shape(n_channels, n_channels)
        The G matrix.
    """
    factors = [(2 * n + 1) / (n ** stiffness * (n + 1) ** stiffness *
                              4 * np.pi) for n in range(1, num_lterms + 1)]
    return legval(cosang, [0] + factors)


def _calc_h(cosang, stiffness=4, num_lterms=50):
    """Calculate spherical spline h function between points on a sphere.

    Parameters
    ----------
    cosang : array-like of float, shape(n_channels, n_channels)
        cosine of angles between pairs of points on a spherical surface. This
        is equivalent to the dot product of unit vectors.
    stiffness : float
        stiffness of the spline. Also referred to as `m`.
    num_lterms : int
        number of Legendre terms to evaluate.
    H : np.ndrarray of float, shape(n_channels, n_channels)
        The H matrix.
    """
    factors = [(2 * n + 1) /
               (n ** (stiffness - 1) * (n + 1) ** (stiffness - 1) * 4 * np.pi)
               for n in range(1, num_lterms + 1)]
    return legval(cosang, [0] + factors)


def _make_interpolation_matrix(pos_from, pos_to, alpha=1e-5):
    """Compute interpolation matrix based on spherical splines

    Implementation based on [1]

    Parameters
    ----------
    pos_from : np.ndarray of float, shape(n_good_sensors, 3)
        The positions to interpoloate from.
    pos_to : np.ndarray of float, shape(n_bad_sensors, 3)
        The positions to interpoloate.
    alpha : float
        Regularization parameter. Defaults to 1e-5.

    Returns
    -------
    interpolation : np.ndarray of float, shape(len(pos_from), len(pos_to))
        The interpolation matrix that maps good signals to the location
        of bad signals.

    References
    ----------
    [1] Perrin, F., Pernier, J., Bertrand, O. and Echallier, JF. (1989).
        Spherical splines for scalp potential and current density mapping.
        Electroencephalography Clinical Neurophysiology, Feb; 72(2):184-7.
    """

    pos_from = pos_from.copy()
    pos_to = pos_to.copy()

    # normalize sensor positions to sphere
    _normalize_vectors(pos_from)
    _normalize_vectors(pos_to)

    # cosine angles between source positions
    cosang_from = pos_from.dot(pos_from.T)
    cosang_to_from = pos_to.dot(pos_from.T)
    G_from = _calc_g(cosang_from)
    G_to_from, H_to_from = (f(cosang_to_from) for f in (_calc_g, _calc_h))

    if alpha is not None:
        G_from.flat[::len(G_from) + 1] += alpha

    C_inv = linalg.pinv(G_from)
    interpolation = G_to_from.dot(C_inv)
    return interpolation


def _make_interpolator(inst, bad_channels):
    """Find indexes and interpolation matrix to interpolate bad channels

    Parameters
    ----------
    inst : mne.io.Raw, mne.Epochs or mne.Evoked
        The data to interpolate. Must be preloaded.
    """
    bads_idx = np.zeros(len(inst.ch_names), dtype=np.bool)
    goods_idx = np.zeros(len(inst.ch_names), dtype=np.bool)

    picks = pick_types(inst.info, meg=False, eeg=True, exclude=[])
    bads_idx[picks] = [inst.ch_names[ch] in bad_channels for ch in picks]
    goods_idx[picks] = True
    goods_idx[bads_idx] = False

    if bads_idx.sum() != len(bad_channels):
        logger.warning('Channel interpolation is currently only implemented '
                       'for EEG. The MEG channels marked as bad will remain '
                       'untouched.')

    pos = get_channel_positions(inst, picks)

    # Make sure only EEG are used
    bads_idx_pos = bads_idx[picks]
    goods_idx_pos = goods_idx[picks]

    pos_good = pos[goods_idx_pos]
    pos_bad = pos[bads_idx_pos]

    # test spherical fit
    radius, center = _fit_sphere(pos_good)
    distance = np.sqrt(np.sum((pos_good - center) ** 2, 1))
    distance = np.mean(distance / radius)
    if np.abs(1. - distance) > 0.1:
        logger.warning('Your spherical fit is poor, interpolation results are '
                       'likely to be inaccurate.')

    logger.info('Computing interpolation matrix from {0} sensor '
                'positions'.format(len(pos_good)))

    interpolation = _make_interpolation_matrix(pos_good, pos_bad)

    return goods_idx, bads_idx, interpolation


def _interpolate_bads_eeg_epochs(epochs, bad_channels_by_epoch=None):
    """Interpolate bad channels per epoch

    Parameters
    ----------
    inst : mne.io.Raw, mne.Epochs or mne.Evoked
        The data to interpolate. Must be preloaded.
    bad_channels_by_epoch : list of list of str
        Bad channel names specified for each epoch. For example, for an Epochs
        instance containing 3 epochs: ``[['F1'], [], ['F3', 'FZ']]``
    """
    if len(bad_channels_by_epoch) != len(epochs):
        raise ValueError("Unequal length of epochs (%i) and "
                         "bad_channels_by_epoch (%i)"
                         % (len(epochs), len(bad_channels_by_epoch)))

    interp_cache = {}
    for i, bad_channels in enumerate(bad_channels_by_epoch):
        if not bad_channels:
            continue

        # find interpolation matrix
        key = tuple(sorted(bad_channels))
        if key in interp_cache:
            goods_idx, bads_idx, interpolation = interp_cache[key]
        else:
            goods_idx, bads_idx, interpolation = interp_cache[key] \
                                = _make_interpolator(epochs, key)

        # apply interpolation
        logger.info('Interpolating %i sensors on epoch %i', bads_idx.sum(), i)
        epochs._data[i, bads_idx, :] = np.dot(interpolation,
                                              epochs._data[i, goods_idx, :])
