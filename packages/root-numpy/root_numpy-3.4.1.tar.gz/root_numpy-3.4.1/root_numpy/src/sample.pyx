"""
Sampling T[F|H]1, T[F|H]2, and T[F|H]3
"""

def sample_f1(f1, unsigned int n_samples):
    cdef TF1* f1_ = <TF1*> PyCObject_AsVoidPtr(f1)
    cdef unsigned int i
    cdef np.ndarray[np.double_t, ndim=1] arr = np.empty(n_samples, dtype=np.double)
    for i from 0 <= i < n_samples:
        arr[i] = f1_.GetRandom()
    return arr


def sample_h1(h1, unsigned int n_samples):
    cdef TH1* h1_ = <TH1*> PyCObject_AsVoidPtr(h1)
    cdef unsigned int i
    cdef np.ndarray[np.double_t, ndim=1] arr = np.empty(n_samples, dtype=np.double)
    for i from 0 <= i < n_samples:
        arr[i] = h1_.GetRandom()
    return arr


def sample_f2(f2, unsigned int n_samples):
    cdef TF2* f2_ = <TF2*> PyCObject_AsVoidPtr(f2)
    cdef unsigned int i
    cdef double x = 0
    cdef double y = 0
    cdef np.ndarray[np.double_t, ndim=2] arr = np.empty((n_samples, 2), dtype=np.double)
    for i from 0 <= i < n_samples:
        f2_.GetRandom2(x, y)
        arr[i, 0] = x
        arr[i, 1] = y
    return arr


def sample_h2(h2, unsigned int n_samples):
    cdef TH2* h2_ = <TH2*> PyCObject_AsVoidPtr(h2)
    cdef unsigned int i
    cdef double x = 0
    cdef double y = 0
    cdef np.ndarray[np.double_t, ndim=2] arr = np.empty((n_samples, 2), dtype=np.double)
    for i from 0 <= i < n_samples:
        h2_.GetRandom2(x, y)
        arr[i, 0] = x
        arr[i, 1] = y
    return arr


def sample_f3(f3, unsigned int n_samples):
    cdef TF3* f3_ = <TF3*> PyCObject_AsVoidPtr(f3)
    cdef unsigned int i
    cdef double x = 0
    cdef double y = 0
    cdef double z = 0
    cdef np.ndarray[np.double_t, ndim=2] arr = np.empty((n_samples, 3), dtype=np.double)
    for i from 0 <= i < n_samples:
        f3_.GetRandom3(x, y, z)
        arr[i, 0] = x
        arr[i, 1] = y
        arr[i, 2] = z
    return arr


def sample_h3(h3, unsigned int n_samples):
    cdef TH3* h3_ = <TH3*> PyCObject_AsVoidPtr(h3)
    cdef unsigned int i
    cdef double x = 0
    cdef double y = 0
    cdef double z = 0
    cdef np.ndarray[np.double_t, ndim=2] arr = np.empty((n_samples, 3), dtype=np.double)
    for i from 0 <= i < n_samples:
        h3_.GetRandom3(x, y, z)
        arr[i, 0] = x
        arr[i, 1] = y
        arr[i, 2] = z
    return arr

