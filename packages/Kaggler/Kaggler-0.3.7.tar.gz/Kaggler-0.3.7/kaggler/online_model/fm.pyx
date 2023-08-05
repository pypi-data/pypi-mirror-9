# cython: boundscheck=False
# cython: wraparound=False
# cython: cdivision=True
from __future__ import division
import numpy as np

cimport cython
from libc.math cimport sqrt, abs
from ..util cimport sigm
cimport numpy as np


np.import_array()


cdef class FM:
    """Factorization Machine online learner.

    Attributes:
        n (int): number of features after hashing trick
        k (int): size of factors for interactions
        a (double): initial learning rate
        w0 (double): weight for bias
        c0 (double): counters
        w (array of double): feature weights
        c (array of double): counters for weights
        V (array of double): feature weights for factors
    """

    cdef unsigned int n
    cdef unsigned int k
    cdef double a
    cdef double w0
    cdef double c0
    cdef double[:] w
    cdef double[:] c
    cdef double[:] V

    def __init__(self,
                 unsigned int n,
                 unsigned int dim=4,
                 double a=0.01,
                 seed=0):
        """Initialize the FM class object.

        Args:
            n (int): number of features after hashing trick
            dim (int): size of factors for interactions
            a (double): initial learning rate
            seed (unsigned int): random seed
        """
        cdef int i

        rng = np.random.RandomState(seed)

        self.n = n       # # of features
        self.k = dim
        self.a = a      # learning rate

        # initialize weights, factorized interactions, and counts
        self.w0 = 0.
        self.c0 = 0.
        self.w = np.zeros((self.n,), dtype=np.float64)
        self.c = np.zeros((self.n,), dtype=np.float64)
        self.V = (rng.rand(self.n * self.k) - .5) * 1e-6

    def read_sparse(self, path):
        """Apply hashing trick to the libsvm format sparse file.

        Args:
            path (str): a file path to the libsvm format sparse file

        Yields:
            idx (list of int): a list of index of non-zero features
            val (list of double): a list of values of non-zero features
            y (int): target value
        """
        for line in open(path):
            xs = line.rstrip().split(' ')

            y = int(xs[0])
            idx = []
            val = []
            for item in xs[1:]:
                i, v = item.split(':')
                idx.append(abs(hash(i)) % self.n)
                val.append(float(v))

            yield zip(idx, val), y

    def predict(self, list x):
        """Predict for features.

        Args:
            x (list of tuple): a list of (index, value) of non-zero features

        Returns:
            p (double): a prediction for input features
        """
        cdef int i
        cdef int k
        cdef double v
        cdef double p
        cdef double wx
        cdef double[:] vx
        cdef double[:] v2x2

        wx = 0.
        vx = np.zeros((self.k,), dtype=np.float64)
        v2x2 = np.zeros((self.k,), dtype=np.float64)
        for i, v in x:
            wx += self.w[i] * v
            for k in range(self.k):
                vx[k] += self.V[i * self.k + k] * v
                v2x2[k] += (self.V[i * self.k + k] ** 2) * (v ** 2)

        p = self.w0 + wx
        for k in range(self.k):
            p += .5 * (vx[k] ** 2 - v2x2[k])

        return sigm(p)

    def update(self, list x, double e):
        """Update the model.

        Args:
            idx (list of int): a list of index of non-zero features
            val (list of double): a list of values of non-zero features
            e (double): error between the prediction of the model and target

        Returns:
            updated model weights and counts
        """
        cdef int i
        cdef int k
        cdef int f
        cdef double v
        cdef double g2
        cdef double dl_dw
        cdef double[:] vx

        # calculate v_f * x in advance
        vx = np.zeros((self.k,), dtype=np.float64)
        for i, v in x:
            for k in range(self.k):
                vx[k] += self.V[i * self.k + k] * v

        # update w0, w, V, c0, and c
        g2 = e * e

        self.w0 -= self.a / (sqrt(self.c0) + 1) * e
        for i, v in x:
            dl_dw = self.a / (sqrt(self.c[i]) + 1) * e * v
            self.w[i] -= dl_dw
            for f in range(self.k):
                self.V[i * self.k + f] -= dl_dw * (vx[f] -
                                                   self.V[i * self.k + f] * v)

            self.c[i] += g2

        self.c0 += g2
