import numpy as np
from scipy import sparse
from _normalization_ import _update_normalization_csr
from .utils import is_symetric_or_tri


def ICE_normalization(X, SS=None, max_iter=3000, eps=1e-4, copy=True,
                      norm='l1', verbose=0, output_bias=False):
    """
    ICE normalization

    The imakaev normalization of Hi-C data consists of iteratively estimating
    the bias. The original algorithm used the l1 norm. It was adapted to allow
    the use of the l2 norm.

    Parameters
    ----------
    X : ndarray or sparse array (n, n)
        raw interaction frequency matrix

    max_iter : integer, optional, default: 3000
        Maximum number of iteration

    eps : float, optional, default: 1e-4
        the relative increment in the results before declaring convergence.

    copy : boolean, optional, default: True
        If copy is True, the original data is not modified.

    norm : string, optional, default: l1
        If set to "l1", will compute the ICE algorithm of the paper. Else, the
        algorithm is adapted to use the l2 norm, as suggested in the SCN
        paper.

    Returns
    -------
    X : ndarray
        Normalized IF matrix

    Example
    -------
    .. plot:: examples/normalization/plot_ICE_normalization.py
    """
    if copy:
        X = X.copy()

    if sparse.issparse(X):
        if not sparse.isspmatrix_csr(X):
            X = sparse.csr_matrix(sparse)
        X.sort_indices()
    else:
        X[np.isnan(X)] = 0
        X = X.astype('float')

    m = X.shape[0]
    is_symetric_or_tri(X)
    old_dbias = None
    bias = np.ones((m, 1))
    for it in xrange(max_iter):
        if norm == 'l1':
            sum_ds = X.sum(axis=0)
        elif norm == 'l2':
            sum_ds = np.sqrt((X ** 2).sum(axis=0))
        if SS is not None:
            raise NotImplementedError
        dbias = sum_ds.reshape((m, 1))
        dbias /= dbias[dbias != 0].mean()
        dbias[dbias == 0] = 1
        bias *= dbias
        # FIXME for sparse format, how can we do this ?
        if sparse.issparse(X):
            X = _update_normalization_csr(X, np.array(dbias).flatten())
        else:
            X /= dbias * dbias.T

        if old_dbias is not None and np.abs(old_dbias - dbias).sum() < eps:
            if verbose > 1:
                print "break at iteration %d" % (it,)
            break

        if verbose > 1 and old_dbias is not None:
            print ('ICE at iteration %d %s' %
                   (it, np.abs(old_dbias - dbias).sum()))
        old_dbias = dbias.copy()
    if output_bias:
        return X, bias
    else:
        return X


def SCN_normalization(X, max_iter=300, eps=1e-6, copy=True):
    """
    Sequential Component Normalization

    Parameters
    ----------
    X : ndarray (n, n)
        raw interaction frequency matrix

    max_iter : integer, optional, default: 300
        Maximum number of iteration

    eps : float, optional, default: 1e-6
        the relative increment in the results before declaring convergence.

    copy : boolean, optional, default: True
        If copy is True, the original data is not modified.

    Returns
    -------
    X : ndarray,
        Normalized IF
    """
    # X needs to be square, else it's gonna fail

    m, n = X.shape
    if m != n:
        raise ValueError

    if copy:
        X = X.copy()

    for it in xrange(max_iter):
        sum_X = np.sqrt((X ** 2).sum(0))
        sum_X[sum_X == 0] = 1
        X /= sum_X
        X = X.T
        sum_X = np.sqrt((X ** 2).sum(0))
        sum_X[sum_X == 0] = 1
        X /= sum_X
        X = X.T

        if np.abs(X - X.T).sum() < eps:
            print "break at iteration %d" % (it,)
            break

    return X
