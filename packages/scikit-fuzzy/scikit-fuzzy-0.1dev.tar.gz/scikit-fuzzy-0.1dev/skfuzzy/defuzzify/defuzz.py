"""
defuzz.py : Various methods for defuzzification and lambda-cuts, to convert
            'fuzzy' systems back into 'crisp' values for decisions.

"""
import numpy as np


def arglcut(ms, lambdacut):
    """
    Determines the subset of indices `mi` of the elements in an N-point
    resultant fuzzy membership sequence `ms` that have a grade of membership
    >= lambdacut.

    Parameters
    ----------
    ms : 1d array
        Fuzzy membership sequence.
    lambdacut : float
        Value used for lambda cutting.

    Returns
    -------
    lidx : 1d array
        Indices corresponding to the lambda-cut subset of `ms`.

    Note
    ----
    This is a convenience function for `np.nonzero(lambdacut <= ms)` and only
    half of the indexing operation that can be more concisely accomplished via
        ms[lambdacut <= ms]

    """
    return np.nonzero(lambdacut <= ms)


def centroid(x, mfx):
    """
    Defuzzification using centroid (`center of gravity`) method.

    Parameters
    ----------
    x : 1d array, length M
        Independent variable
    mfx : 1d array, length M
        Fuzzy membership function

    Returns
    -------
    u : 1d array, length M
        Defuzzified result

    See also
    --------
    DCENTROID, DEFUZZ

    """
    return (x * mfx).sum() / np.fmax(mfx.sum(),
                                     np.finfo(float).eps).astype(float)


def dcentroid(x, mfx, x0):
    """
    Defuzzification using a differential centroidal method about `x0`.

    Parameters
    ----------
    x : 1d array or iterable
        Independent variable.
    mfx : 1d array or iterable
        Fuzzy membership function.
    x0 : float
        Central value to calculate differential centroid about.

    Returns
    -------
    u : 1d array
        Defuzzified result.

    See also
    --------
    CENTROID, DEFUZZ

    """
    x = x - x0
    u = (x * mfx).sum(axis=0).astype(float) / np.fmax(mfx.sum(axis=0),
                                                      np.finfo(float).eps)
    return x0 + u


def defuzz(x, mfx, mode):
    """
    Defuzzification of a membership function, returning a defuzzified value
    of the function at x, using various defuzzification methods.

    Parameters
    ----------
    x : 1d array or iterable, length N
        Independent variable.
    mfx : 1d array of iterable, length N
        Fuzzy membership function.
    mode : string
        Controls which defuzzification method will be used.
        * 'centroid': Centroid of area
        * 'bisector': bisector of area
        * 'mom'        : mean of maximum
        * 'som'        : min of maximum
        * 'lom'        : max of maximum

    Returns
    -------
    u : float or int
        Defuzzified result.

    See also
    --------
    CENTROID, DCENTROID

    """
    mode = mode.lower()
    x = x.ravel()
    mfx = mfx.ravel()
    n = len(x)
    assert n == len(mfx), 'Length of x and fuzzy membership function must be \
                          identical.'

    if 'centroid' in mode or 'bisector' in mode:
        tot_area = mfx.sum()
        assert tot_area != 0, 'Total area is zero in defuzzification!'

        if 'centroid' in mode:
            return centroid(x, mfx)

        elif 'bisector' in mode:
            tmp = 0
            for k in range(n):
                tmp += mfx[k]
                if tmp >= tot_area / 2.:
                    return x[k]

    elif 'mom' in mode:
        return np.mean(x[mfx == mfx.max()])

    elif 'som' in mode:
        tmp = x[mfx == mfx.max()]
        return tmp[tmp == np.abs(tmp).min()][0]

    elif 'lom' in mode:
        tmp = x[mfx == mfx.max()]
        return tmp[tmp == np.abs(tmp).max()][0]

    else:
        raise ValueError('The input for `mode`, %s, was incorrect.' % (mode))


def lambda_cut_series(x, mfx, N):
    """
    Determines a series of lambda-cuts in a sweep from 0+ to 1.0 in N steps.

    Parameters
    ----------
    x : 1d array
        Universe function for fuzzy membership function mfx.
    mfx : 1d array
        Fuzzy membership function for x.
    N : int
        Number of steps.

    Returns
    -------
    z : 2d array, (N, 3)
        Lambda cut intevals.

    """
    x = np.asarray(x)
    mfx = np.asarray(mfx)

    step = (mfx.max() - mfx.min()) / float(N - 1)
    lambda_cuts = np.arange(mfx.min(), mfx.max() + np.finfo(float).eps, step)
    z = np.zeros((N, 3))
    z[:, 0] = lambda_cuts.T
    z[0, [1, 2]] = _support(x, mfx)

    for ii in range(1, N):
        xx = _lcutinterval(x, mfx, lambda_cuts[ii])
        z[ii, [1, 2]] = xx

    return z


def _lcutinterval(x, mfx, lambdacut):
    """
    Determines upper & lower interval limits of the lambda-cut for membership
    function u(x) [here mfx].

    Parameters
    ----------
    x : 1d array
        Independent variable.
    mfx : 1d array
        Fuzzy membership function for x.
    lambdacut : float
        Value used for lambda-cut.

    Returns
    -------
    z : 1d array
        Lambda-cut output.

    Note
    ----
    Membership function mfx must be convex and monotonic in rise or fall.

    """
    z = x[lambdacut - 1e-6 <= mfx]
    return np.hstack((z.min(), z.max()))


def lambda_cut(ms, lcut):
    """
    Returns the crisp (binary) lambda-cut set of the membership sequence `ms`
    with membership >= `lcut`.

    Parameters
    ----------
    ms : 1d array
        Fuzzy membership set.
    lcut : float
        Value used for lambda-cut, on range [0, 1.0].

    Returns
    -------
    mlambda : 1d array
        Lambda-cut set of `ms`: ones if ms[i] >= lcut, zeros otherwise.

    """
    return (ms > lcut) * 1


def _support(x, mfx):
    """
    Determines the lower & upper limits of the support interval.

    Parameters
    ----------
    x : 1d array
        Independent variable.
    mfx : 1d array
        Fuzzy membership function for x; must be convex, continuous,
        and monotonic (rise XOR fall).

    Returns
    -------
    z : 1d array, length 2
        Interval representing lower & upper limits of the support interval.

    """
    apex = mfx.max()
    m = np.nonzero(mfx == apex)[0][0]
    n = len(x)
    xx = x[0:m + 1]
    mfxx = mfx[0:m + 1]
    z = xx[mfxx == mfxx.min()].max()
    xx = x[m:n]
    mfxx = mfx[m:n]
    return np.r_[z, xx[mfxx == mfxx.min()].min()]
