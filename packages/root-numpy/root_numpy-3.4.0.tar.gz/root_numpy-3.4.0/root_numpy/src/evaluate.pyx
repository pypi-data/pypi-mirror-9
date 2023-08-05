def evaluate_h1(hist,
                np.ndarray[np.double_t, ndim=1] array):
    # perform type checking on python side
    cdef TH1* _hist = <TH1*> PyCObject_AsVoidPtr(hist)
    cdef long size = array.shape[0]
    cdef np.ndarray[np.double_t, ndim=1] values = np.empty(size, dtype=np.double)
    cdef long i
    for i from 0 <= i < size:
        values[i] = _hist.GetBinContent(_hist.FindBin(array[i]))
    return values

def evaluate_h2(hist,
                np.ndarray[np.double_t, ndim=2] array):
    # perform type checking on python side
    cdef TH2* _hist = <TH2*> PyCObject_AsVoidPtr(hist)
    cdef long size = array.shape[0]
    cdef np.ndarray[np.double_t, ndim=1] values = np.empty(size, dtype=np.double)
    cdef long i
    for i from 0 <= i < size:
        values[i] = _hist.GetBinContent(_hist.FindBin(array[i][0], array[i][1]))
    return values

def evaluate_h3(hist,
                np.ndarray[np.double_t, ndim=2] array):
    # perform type checking on python side
    cdef TH3* _hist = <TH3*> PyCObject_AsVoidPtr(hist)
    cdef long size = array.shape[0]
    cdef np.ndarray[np.double_t, ndim=1] values = np.empty(size, dtype=np.double)
    cdef long i
    for i from 0 <= i < size:
        values[i] = _hist.GetBinContent(_hist.FindBin(array[i][0], array[i][1], array[i][2]))
    return values

def evaluate_f1(func,
                np.ndarray[np.double_t, ndim=1] array):
    # perform type checking on python side
    cdef TFormula* _func = <TFormula*> PyCObject_AsVoidPtr(func)
    cdef long size = array.shape[0]
    cdef np.ndarray[np.double_t, ndim=1] values = np.empty(size, dtype=np.double)
    cdef long i
    for i from 0 <= i < size:
        values[i] = _func.Eval(array[i])
    return values

def evaluate_f2(func,
                np.ndarray[np.double_t, ndim=2] array):
    # perform type checking on python side
    cdef TFormula* _func = <TFormula*> PyCObject_AsVoidPtr(func)
    cdef long size = array.shape[0]
    cdef np.ndarray[np.double_t, ndim=1] values = np.empty(size, dtype=np.double)
    cdef long i
    for i from 0 <= i < size:
        values[i] = _func.Eval(array[i][0], array[i][1])
    return values

def evaluate_f3(func,
                np.ndarray[np.double_t, ndim=2] array):
    # perform type checking on python side
    cdef TFormula* _func = <TFormula*> PyCObject_AsVoidPtr(func)
    cdef long size = array.shape[0]
    cdef np.ndarray[np.double_t, ndim=1] values = np.empty(size, dtype=np.double)
    cdef long i
    for i from 0 <= i < size:
        values[i] = _func.Eval(array[i][0], array[i][1], array[i][2])
    return values

def evaluate_f4(func,
                np.ndarray[np.double_t, ndim=2] array):
    # perform type checking on python side
    cdef TFormula* _func = <TFormula*> PyCObject_AsVoidPtr(func)
    cdef long size = array.shape[0]
    cdef np.ndarray[np.double_t, ndim=1] values = np.empty(size, dtype=np.double)
    cdef long i
    for i from 0 <= i < size:
        values[i] = _func.Eval(array[i][0], array[i][1], array[i][2], array[i][3])
    return values

def evaluate_graph(graph,
                   np.ndarray[np.double_t, ndim=1] array):
    # perform type checking on python side
    cdef TGraph* _graph = <TGraph*> PyCObject_AsVoidPtr(graph)
    cdef long size = array.shape[0]
    cdef np.ndarray[np.double_t, ndim=1] values = np.empty(size, dtype=np.double)
    cdef long i
    for i from 0 <= i < size:
        values[i] = _graph.Eval(array[i])
    return values

def evaluate_spline(spline,
                    np.ndarray[np.double_t, ndim=1] array):
    # perform type checking on python side
    cdef TSpline* _spline = <TSpline*> PyCObject_AsVoidPtr(spline)
    cdef long size = array.shape[0]
    cdef np.ndarray[np.double_t, ndim=1] values = np.empty(size, dtype=np.double)
    cdef long i
    for i from 0 <= i < size:
        values[i] = _spline.Eval(array[i])
    return values
