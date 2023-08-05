# cython: experimental_cpp_class_def=True

TYPES = {
    TypeName[bool]().name:               ('bool',               np.dtype(np.bool),      np.NPY_BOOL),
    TypeName[char]().name:               ('char',               np.dtype(np.int8),      np.NPY_INT8),
    TypeName[unsigned_char]().name:      ('unsigned char',      np.dtype(np.uint8),     np.NPY_UINT8),
    TypeName[short]().name:              ('short',              np.dtype(np.int16),     np.NPY_INT16),
    TypeName[unsigned_short]().name:     ('unsigned short',     np.dtype(np.uint16),    np.NPY_UINT16),
    TypeName[int]().name:                ('int',                np.dtype(np.int32),     np.NPY_INT32),
    TypeName[unsigned_int]().name:       ('unsigned int',       np.dtype(np.uint32),    np.NPY_UINT32),
    TypeName[long]().name:               ('long',               np.dtype(np.int64),     np.NPY_INT64),
    TypeName[unsigned_long]().name:      ('unsigned long',      np.dtype(np.uint64),    np.NPY_UINT64),
    TypeName[long_long]().name:          ('long long',          np.dtype(np.longlong),  np.NPY_LONGLONG),
    TypeName[unsigned_long_long]().name: ('unsigned long long', np.dtype(np.ulonglong), np.NPY_ULONGLONG),
    TypeName[float]().name:              ('float',              np.dtype(np.float32),   np.NPY_FLOAT32),
    TypeName[double]().name:             ('double',             np.dtype(np.float64),   np.NPY_FLOAT64),
}

TYPES_NUMPY2ROOT = {
    np.dtype(np.bool):      (1, 'O'),
    np.dtype(np.int8):      (1, 'B'),
    np.dtype(np.int16):     (2, 'S'),
    np.dtype(np.int32):     (4, 'I'),
    np.dtype(np.int64):     (8, 'L'),
    np.dtype(np.uint8):     (1, 'b'),
    np.dtype(np.uint16):    (2, 's'),
    np.dtype(np.uint32):    (4, 'i'),
    np.dtype(np.uint64):    (8, 'l'),
    np.dtype(np.float):     (8, 'D'),
    np.dtype(np.float32):   (4, 'F'),
    np.dtype(np.float64):   (8, 'D'),
}


def list_trees(fname):
    cdef TFile* f = Open(fname, 'read')
    if f is NULL:
        raise IOError("cannot read {0}".format(fname))
    cdef TList* keys = f.GetListOfKeys()
    if keys is NULL:
        raise IOError("unable to get keys in {0}".format(fname))
    ret = dict()
    cdef int n = keys.GetEntries()
    cdef TKey* key
    for i in range(n):
        key = <TKey*> keys.At(i)
        clsname = str(key.GetClassName())
        if clsname == 'TTree' or clsname == 'TNtuple':
            ret[str(key.GetName())] = None
    return ret.keys()


def list_structures(fname, tree=None):
    if tree is None:
        # automatically select single tree
        tree = list_trees(fname)
        if len(tree) != 1:
            raise ValueError("multiple trees found: {0}".format(', '.join(tree)))
        else:
            tree = tree[0]
    cdef TFile* f = Open(fname, 'read')
    if f is NULL:
        raise IOError("cannot read {0}".format(fname))
    cdef TTree* t = <TTree*> f.Get(tree)
    if t is NULL:
        raise IOError("tree {0} not found in {1}".format(tree, fname))
    return parse_tree_structure(t)


def list_branches(fname, tree=None):
    return list_structures(fname, tree).keys()



cdef parse_branch_structure(TBranch* branch):
    cdef TObjArray* leaves
    cdef TLeaf* leaf
    cdef int ileaf
    leaves = branch.GetListOfLeaves()
    if leaves is NULL:
        raise RuntimeError("branch {0} has no leaves".format(branch.GetName()))
    leaflist = []
    for ileaf in range(leaves.GetEntries()):
        leaf = <TLeaf*>leaves.At(ileaf)
        lname = leaf.GetName()
        # resolve Float_t -> float, vector<Float_t> -> vector<float>, ..
        ltype = <bytes>ResolveTypedef(leaf.GetTypeName(), True).c_str()
        leaflist.append((lname, ltype))
    if not leaflist:
        raise RuntimeError(
            "leaf list for branch {0} is empty".format(
                branch.GetName()))
    return leaflist


cdef parse_tree_structure(TTree* tree, branches=None):
    cdef int ibranch
    cdef TBranch* branch
    ret = OrderedDict()
    if branches is not None:
        for branch_name in branches:
            branch = tree.GetBranch(branch_name)            
            if branch is NULL:
                continue
            ret[branch.GetName()] = parse_branch_structure(branch)
        return ret
    # all branches
    cdef TObjArray* all_branches = tree.GetListOfBranches()
    if all_branches is NULL:
        return ret
    for ibranch in range(all_branches.GetEntries()):
        branch = <TBranch*>(all_branches.At(ibranch))
        ret[branch.GetName()] = parse_branch_structure(branch)
    return ret


# create numpy array of given type code with
# given numelement and size of each element
# and write it to buffer
cdef inline int create_numpyarray(void* buffer, void* src, int typecode,
                                  unsigned long numele, int elesize):
    cdef np.npy_intp dims[1]
    dims[0] = numele;
    cdef np.ndarray tmp = np.PyArray_EMPTY(1, dims, typecode, 0)
    cdef PyObject* tmpobj = <PyObject*> tmp # borrow ref
    # increase one since we are putting in buffer directly
    Py_INCREF(tmp)
    # copy to tmp.data
    cdef unsigned long nbytes = numele * elesize
    memcpy(tmp.data, src, nbytes)
    # now write PyObject* to buffer
    memcpy(buffer, &tmpobj, sizeof(PyObject*))
    return sizeof(tmpobj)


# special treatment for vector<bool>
cdef inline int create_numpyarray_vectorbool(void* buffer, vector[bool]* src):
    cdef unsigned long numele = src.size()
    cdef np.npy_intp dims[1]
    dims[0] = numele;
    cdef np.ndarray tmp = np.PyArray_EMPTY(1, dims, np.NPY_BOOL, 0)
    cdef PyObject* tmpobj = <PyObject*> tmp # borrow ref
    # increase one since we are putting in buffer directly
    Py_INCREF(tmp)
    # can't use memcpy here...
    cdef unsigned long i
    for i in range(numele):
        tmp[i] = src.at(i)
    # now write PyObject* to buffer
    memcpy(buffer, &tmpobj, sizeof(PyObject*))
    return sizeof(tmpobj)


cdef inline int create_numpyarray_vectorstring(void* buffer, vector[string]* src):
    cdef unsigned long numele = src.size()
    cdef np.npy_intp dims[1]
    dims[0] = numele;
    cdef int objsize = np.dtype('O').itemsize
    cdef np.ndarray tmp = np.PyArray_EMPTY(1, dims, np.NPY_OBJECT, 0)
    cdef PyObject* tmpobj = <PyObject*> tmp # borrow ref
    # increase one since we are putting in buffer directly
    Py_INCREF(tmp)
    cdef PyObject* tmpstrobj
    cdef char* dataptr = <char*> tmp.data
    # can't use memcpy here...
    cdef unsigned long i
    for i in range(numele):
        py_bytes = str(src.at(i))
        Py_INCREF(py_bytes)
        tmpstrobj = <PyObject*> py_bytes
        memcpy(&dataptr[i*objsize], &tmpstrobj, sizeof(PyObject*))
    # now write PyObject* to buffer
    memcpy(buffer, &tmpobj, sizeof(PyObject*))
    return sizeof(tmpobj)


cdef cppclass Converter:
    __init__():
        pass

    __dealloc__():
        pass

    int write(Column* col, void* buffer):
        pass

    object get_nptype():
        pass


cdef cppclass BasicConverter(Converter):
    # cdef string rtype
    int size
    int nptypecode
    string nptype

    __init__(int size, string nptype, int nptypecode):
        this.size = size
        this.nptypecode = nptypecode
        this.nptype = nptype

    int write(Column* col, void* buffer):
        cdef void* src = col.GetValuePointer()
        memcpy(buffer, src, this.size)
        return this.size

    object get_nptype():
        return np.dtype(this.nptype)

    int get_nptypecode():
        return this.nptypecode


cdef cppclass ObjectConverterBase(Converter):
    object get_nptype():
        return np.object

    object get_nptypecode():
        return np.NPY_OBJECT


cdef cppclass VaryArrayConverter(ObjectConverterBase):
    BasicConverter* conv # converter for single element
    int typecode
    int elesize

    __init__(BasicConverter* conv):
        this.conv = conv
        this.typecode = conv.get_nptypecode()
        this.elesize = conv.size

    int write(Column* col, void* buffer):
        cdef int numele = col.GetLen()
        cdef void* src = col.GetValuePointer()
        return create_numpyarray(buffer, src, this.typecode, numele, this.elesize)


cdef cppclass FixedArrayConverter(Converter):
    BasicConverter* conv # converter for single element
    int L # numele

    __init__(BasicConverter* conv, int L):
        this.conv = conv
        this.L = L

    int write(Column* col, void* buffer):
        cdef void* src = col.GetValuePointer()
        cdef int nbytes = col.GetSize()
        memcpy(buffer, src, nbytes)
        return nbytes

    object get_nptype():
        return (np.dtype(this.conv.nptype), this.L)

    int get_nptypecode():
        return this.conv.nptypecode


cdef cppclass VectorConverter[T](ObjectConverterBase):
    int elesize
    int nptypecode
    Vector2Array[T] v2a

    __init__():
        cdef TypeName[T] ast = TypeName[T]()
        info = TYPES[ast.name]
        this.elesize = info[1].itemsize
        this.nptypecode = info[2]

    int write(Column* col, void* buffer):
        cdef vector[T]* tmp = <vector[T]*> col.GetValuePointer()
        cdef unsigned long numele = tmp.size()
        # check cython auto-generated code
        # if it really does &((*tmp)[0])
        cdef T* fa = this.v2a.convert(tmp)
        return create_numpyarray(buffer, fa, this.nptypecode, numele, this.elesize)


cdef cppclass VectorVectorConverter[T](ObjectConverterBase):
    int elesize
    int nptypecode
    Vector2Array[T] v2a

    __init__():
        cdef TypeName[T] ast = TypeName[T]()
        info = TYPES[ast.name]
        this.elesize = info[1].itemsize
        this.nptypecode = info[2]

    int write(Column* col, void* buffer):
        cdef vector[vector[T]]* tmp = <vector[vector[T]]*> col.GetValuePointer()
        # this will hold number of subvectors
        cdef unsigned long numele
        cdef T* fa
        # these are defined solely for the outer array wrapper
        cdef int objsize = np.dtype('O').itemsize
        cdef int objtypecode = np.NPY_OBJECT
        numele = tmp[0].size()
        # create an outer array container that dataptr points to,
        # containing pointers from create_numpyarray().
        # define an (numele)-dimensional outer array to hold our subvectors fa
        cdef np.npy_intp dims[1]
        dims[0] = numele
        cdef np.ndarray outer = np.PyArray_EMPTY(1, dims, objtypecode, 0)
        cdef PyObject* outerobj = <PyObject*> outer # borrow ref
        # increase one since we are putting in buffer directly
        Py_INCREF(outer)
        # now write PyObject* to buffer
        memcpy(buffer, &outerobj, sizeof(PyObject*))
        # build a dataptr pointing to outer, so we can shift and write each
        # of the subvectors
        cdef char* dataptr = <char*> outer.data
        # loop through all subvectors
        cdef unsigned long i
        for i in range(numele):
            fa = this.v2a.convert(&tmp[0][i])
            create_numpyarray(&dataptr[i*objsize], fa, this.nptypecode,
                              tmp[0][i].size(), this.elesize)
        return sizeof(outerobj)


cdef cppclass VectorBoolConverter(ObjectConverterBase):
    # Requires special treament since vector<bool> stores contents as bits...
    int write(Column* col, void* buffer):
        cdef vector[bool]* tmp = <vector[bool]*> col.GetValuePointer()
        return create_numpyarray_vectorbool(buffer, tmp)


cdef cppclass VectorVectorBoolConverter(ObjectConverterBase):
    # Requires special treament since vector<bool> stores contents as bits...
    int write(Column* col, void* buffer):
        cdef vector[vector[bool]]* tmp = <vector[vector[bool]]*> col.GetValuePointer()
        # this will hold number of subvectors
        cdef unsigned long numele
        # these are defined solely for the outer array wrapper
        cdef int objsize = np.dtype('O').itemsize
        cdef int objtypecode = np.NPY_OBJECT
        numele = tmp[0].size()
        # create an outer array container that dataptr points to,
        # containing pointers from create_numpyarray().
        # define an (numele)-dimensional outer array to hold our subvectors fa
        cdef np.npy_intp dims[1]
        dims[0] = numele
        cdef np.ndarray outer = np.PyArray_EMPTY(1, dims, objtypecode, 0)
        cdef PyObject* outerobj = <PyObject*> outer # borrow ref
        # increase one since we are putting in buffer directly
        Py_INCREF(outer)
        # now write PyObject* to buffer
        memcpy(buffer, &outerobj, sizeof(PyObject*))
        # build a dataptr pointing to outer, so we can shift and write each
        # of the subvectors
        cdef char* dataptr = <char*> outer.data
        # loop through all subvectors
        cdef unsigned long i
        for i in range(numele):
            create_numpyarray_vectorbool(&dataptr[i*objsize], &tmp[0][i])
        return sizeof(outerobj)


cdef cppclass StringConverter(ObjectConverterBase):
    int write(Column* col, void* buffer):
        cdef string* s = <string*> col.GetValuePointer()
        py_bytes = str(s[0])
        cdef PyObject* tmpobj = <PyObject*> py_bytes # borrow ref
        # increase one since we are putting in buffer directly
        Py_INCREF(py_bytes)
        # now write PyObject* to buffer
        memcpy(buffer, &tmpobj, sizeof(PyObject*))
        return sizeof(tmpobj)


cdef cppclass VectorStringConverter(ObjectConverterBase):
    int write(Column* col, void* buffer):
        cdef vector[string]* tmp = <vector[string]*> col.GetValuePointer()
        return create_numpyarray_vectorstring(buffer, tmp)


cdef cppclass VectorVectorStringConverter(ObjectConverterBase):
    int write(Column* col, void* buffer):
        cdef vector[vector[string]]* tmp = <vector[vector[string]]*> col.GetValuePointer()
        # this will hold number of subvectors
        cdef unsigned long numele
        # these are defined solely for the outer array wrapper
        cdef int objsize = np.dtype('O').itemsize
        cdef int objtypecode = np.NPY_OBJECT
        numele = tmp[0].size()
        # create an outer array container that dataptr points to,
        # containing pointers from create_numpyarray().
        # define an (numele)-dimensional outer array to hold our subvectors fa
        cdef np.npy_intp dims[1]
        dims[0] = numele
        cdef np.ndarray outer = np.PyArray_EMPTY(1, dims, objtypecode, 0)
        cdef PyObject* outerobj = <PyObject*> outer # borrow ref
        # increase one since we are putting in buffer directly
        Py_INCREF(outer)
        # now write PyObject* to buffer
        memcpy(buffer, &outerobj, sizeof(PyObject*))
        # build a dataptr pointing to outer, so we can shift and write each
        # of the subvectors
        cdef char* dataptr = <char*> outer.data
        # loop through all subvectors
        cdef unsigned long i
        for i in range(numele):
            create_numpyarray_vectorstring(&dataptr[i*objsize], &tmp[0][i])
        return sizeof(outerobj)


cdef cpp_map[string, Converter*] CONVERTERS
ctypedef pair[string, Converter*] CONVERTERS_ITEM

# basic type converters
for ctypename, (ctype, dtype, dtypecode) in TYPES.items():
    CONVERTERS.insert(CONVERTERS_ITEM(
        ctype, new BasicConverter(
            dtype.itemsize, dtype.name, dtypecode)))


# vector<> converters
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<bool>', new VectorBoolConverter()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<char>', new VectorConverter[char]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<unsigned char>', new VectorConverter[unsigned_char]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<short>', new VectorConverter[short]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<unsigned short>', new VectorConverter[unsigned_short]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<int>', new VectorConverter[int]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<unsigned int>', new VectorConverter[unsigned_int]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<long>', new VectorConverter[long]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<unsigned long>', new VectorConverter[unsigned_long]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<long long>', new VectorConverter[long_long]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<unsigned long long>', new VectorConverter[unsigned_long_long]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<float>', new VectorConverter[float]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<double>', new VectorConverter[double]()))
# vector<vector<> > converters
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<vector<bool> >', new VectorVectorBoolConverter()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<vector<char> >', new VectorVectorConverter[char]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<vector<unsigned char> >', new VectorVectorConverter[unsigned_char]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<vector<short> >', new VectorVectorConverter[short]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<vector<unsigned short> >', new VectorVectorConverter[unsigned_short]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<vector<int> >', new VectorVectorConverter[int]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<vector<unsigned int> >', new VectorVectorConverter[unsigned_int]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<vector<long> >', new VectorVectorConverter[long]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<vector<unsigned long> >', new VectorVectorConverter[unsigned_long]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<vector<long long> >', new VectorVectorConverter[long_long]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<vector<unsigned long long> >', new VectorVectorConverter[unsigned_long_long]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<vector<float> >', new VectorVectorConverter[float]()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<vector<double> >', new VectorVectorConverter[double]()))
# string converters
CONVERTERS.insert(CONVERTERS_ITEM(
    'string', new StringConverter()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<string>', new VectorStringConverter()))
CONVERTERS.insert(CONVERTERS_ITEM(
    'vector<vector<string> >', new VectorVectorStringConverter()))


cdef Converter* find_converter(Column* col):
    cdef ColumnType ct = col.coltype
    cdef string typename = string(col.GetTypeName())
    cdef Converter* conv
    cdef Converter* basic_conv
    if ct == SINGLE:
        return find_converter_by_typename(typename)
    elif ct == FIXED:
        conv = find_converter_by_typename(typename + '[fixed]')
        if conv == NULL:
            basic_conv = find_converter_by_typename(typename)
            if basic_conv == NULL:
                return NULL
            conv = new FixedArrayConverter(
                    <BasicConverter*>basic_conv,
                    col.countval)
            CONVERTERS.insert(CONVERTERS_ITEM(
                typename + '[fixed]', conv))
        return conv
    elif ct == VARY:
        conv = find_converter_by_typename(typename + '[vary]')
        if conv == NULL:
            basic_conv = find_converter_by_typename(typename)
            if basic_conv == NULL:
                return NULL
            conv = new VaryArrayConverter(
                    <BasicConverter*>basic_conv)
            CONVERTERS.insert(CONVERTERS_ITEM(
                typename + '[vary]', conv))
        return conv
    return NULL


cdef Converter* find_converter_by_typename(string typename):
    it = CONVERTERS.find(ResolveTypedef(typename.c_str(), True))
    if it == CONVERTERS.end():
        return NULL
    return deref(it).second


cdef np.ndarray init_array(vector[Column*]& columns,
                           vector[Converter*]& cv,
                           unsigned long entries,
                           include_weight,
                           weight_name):
    cdef Column* this_col
    cdef Converter* this_conv
    cdef unsigned int i
    nst = []
    for i in range(columns.size()):
        this_col = columns[i]
        this_conv = find_converter(this_col)
        if this_conv == NULL:
            raise ValueError("no converter for {0}".format(this_col.GetTypeName()))
        nst.append((this_col.colname, this_conv.get_nptype()))
        cv.push_back(this_conv)
    if include_weight:
        nst.append((weight_name, np.dtype('d')))
    return np.empty(entries, dtype=nst)


cdef handle_load(int load, bool ignore_index=False):
    if load >= 0:
        return
    if load == -1:
        raise ValueError("chain is empty")
    elif load == -2:
        if ignore_index:
            return
        raise IndexError("tree index in chain is out of bounds")
    elif load == -3:
        raise IOError("cannot open current file")
    elif load == -4:
        raise IOError("cannot access tree in current file")
    raise RuntimeError("the chain is not initialized")


cdef object tree2array(TTree* tree, branches, selection,
                       start, stop, step,
                       include_weight, weight_name):

    if tree.GetNbranches() == 0:
        raise ValueError("tree has no branches")

    cdef vector[Column*] columns
    cdef Column* col

    # Make a "better" chain so we can register all columns
    cdef BetterChain* bc = new BetterChain(tree)
    handle_load(bc.Prepare(), True)

    cdef TTreeFormula* selection_formula = NULL
    cdef TTreeFormula* formula = NULL
    cdef int num_entries = bc.GetEntries()
    cdef int num_entries_selected = 0
    cdef int ientry

    cdef Converter* conv
    cdef unsigned long numcol
    cdef void* dataptr
    cdef np.ndarray arr
    cdef int nb
    cdef int entry_size
    cdef vector[Converter*] conv_array
    cdef bytes py_string
    cdef char* c_string

    try:
        # Set up the selection if we have one
        if selection:
            py_string = str(selection)
            c_string = py_string
            selection_formula = new TTreeFormula("selection", c_string, bc.fChain)
            if selection_formula == NULL or selection_formula.GetNdim() == 0:
                del selection_formula
                raise ValueError("could not compile selection formula")
            # The chain will take care of updating the formula leaves when
            # rolling over to the next tree.
            bc.AddFormula(selection_formula)
        
        # Parse the tree structure to determine branches and leaves
        structure = parse_tree_structure(tree, branches=branches)
        user_branches = False
        if branches is None:
            branches = structure.keys()
        elif len(branches) == 0:
            raise ValueError("branches is an empty list")
        elif len(branches) != len(set(branches)):
            raise ValueError("duplicate branches requested")
        else:
            user_branches = True

        for branch in branches:
            if branch in structure:
                leaves = structure[branch]
                shortname = len(leaves) == 1
                for leaf, ltype in leaves:
                    if CONVERTERS.find(ltype) != CONVERTERS.end():
                        colname = branch if shortname else '{0}_{1}'.format(branch, leaf)
                        col = bc.MakeColumn(branch, leaf, colname)
                        columns.push_back(col)
                    elif user_branches:
                        raise TypeError(
                            "cannot convert leaf {0} of branch {1} "
                            "with type {2} (skipping)".format(branch, leaf, ltype))
                    else:
                        warnings.warn(
                            "cannot convert leaf {0} of branch {1} "
                            "with type {2} (skipping)".format(branch, leaf, ltype),
                            RootNumpyUnconvertibleWarning)
            else:
                # Attempt to interpret as an expression
                py_string = str(branch)
                c_string = py_string
                formula = new TTreeFormula(c_string, c_string, bc.fChain)
                if formula == NULL or formula.GetNdim() == 0:
                    del formula
                    raise ValueError(
                        "the branch or expression {0} "
                        "is not present or valid".format(branch))
                # The chain will take care of updating the formula leaves when
                # rolling over to the next tree.
                bc.AddFormula(formula)
                col = new FormulaColumn(branch, formula)
                columns.push_back(col)
        
        if columns.size() == 0:
            raise RuntimeError("unable to convert any branches in this tree")
        
        # Activate branches used by formulae and columns
        # and deactivate all others
        bc.InitBranches()

        # Now that we have all the columns we can
        # make an appropriate array structure
        arr = init_array(columns, conv_array, num_entries,
                         include_weight, weight_name)
        # Exclude weight column
        numcol = columns.size()
        
        indices = slice(start, stop, step).indices(num_entries)
        for ientry in xrange(*indices):
            entry_size = bc.GetEntry(ientry)
            handle_load(entry_size)
            if entry_size == 0:
                raise IOError("read failure in current tree")

            # Determine if this entry passes the selection,
            # similar to the code in ROOT's tree/treeplayer/src/TTreePlayer.cxx
            if selection_formula != NULL:
                selection_formula.GetNdata() # required, as in TTreePlayer
                if selection_formula.EvalInstance(0) == 0:
                    continue

            # Copy the values into the array
            dataptr = np.PyArray_GETPTR1(arr, num_entries_selected)
            for icol in xrange(numcol):
                col = columns[icol]
                conv = conv_array[icol]
                nb = conv.write(col, dataptr)
                # poorman pointer magic
                dataptr = shift(dataptr, nb)
            if include_weight:
                (<double*> dataptr)[0] = bc.GetWeight() 

            # Increment number of selected entries last
            num_entries_selected += 1
    finally:
        del bc
    
    # If we selected fewer than num_entries entries then shrink the array
    if num_entries_selected < num_entries:
        arr.resize(num_entries_selected)

    return arr


def root2array_fromFname(fnames, treename, branches,
                         selection, start, stop, step,
                         include_weight, weight_name):
    cdef TChain* ttree = NULL
    try:
        ttree = new TChain(treename)
        for fn in fnames:
            if ttree.Add(fn, -1) == 0:
                raise IOError("unable to access tree '{0}' in {1}".format(
                    treename, fn))
        ret = tree2array(
            <TTree*> ttree, branches,
            selection, start, stop, step,
            include_weight, weight_name)
    finally:
        del ttree
    return ret


def root2array_fromCObj(tree, branches, selection,
                        start, stop, step,
                        include_weight, weight_name):
    # this is not a safe method
    # provided here for convenience only
    # typecheck should be implemented by the wrapper
    if not PyCObject_Check(tree):
        raise ValueError("tree must be PyCObject")
    cdef TTree* chain = <TTree*> PyCObject_AsVoidPtr(tree)
    return tree2array(
            chain, branches, selection,
            start, stop, step,
            include_weight, weight_name)


####################################
# array -> TTree conversion follows:
####################################

cdef cppclass NP2CConverter:
    void fill_from(void* source):
        pass
    __dealloc__():
        pass


cdef cppclass ScalarNP2CConverter(NP2CConverter):
    int nbytes
    string roottype
    string name
    void* value
    TBranch* branch
    # don't use copy constructor of this one since it will screw up
    # tree binding and/or ownership of value
    __init__(TTree* tree, string name, string roottype, int nbytes):
        cdef string leaflist
        this.nbytes = nbytes
        this.roottype = roottype
        this.name = name
        this.value = malloc(nbytes)
        this.branch = tree.GetBranch(this.name.c_str())
        if this.branch == NULL:
            leaflist = this.name + '/' + this.roottype
            this.branch = tree.Branch(this.name.c_str(), this.value, leaflist.c_str())
        else:
            # check type compatibility of existing branch
            existing_type = this.branch.GetTitle().rpartition('/')[-1]
            if str(roottype) != existing_type:
                raise TypeError(
                    "field `{0}` of type `{1}` is not compatible "
                    "with existing branch of type `{2}`".format(
                        name, roottype, existing_type))
            this.branch.SetAddress(this.value)
        this.branch.SetStatus(1)

    __del__(self): # does this do what I want?
        free(this.value)

    void fill_from(void* source):
        memcpy(this.value, source, this.nbytes)
        this.branch.Fill()


cdef NP2CConverter* find_np2c_converter(TTree* tree, name, dtype, peekvalue=None):
    # TODO:
    # np.float16: #this needs special treatment root doesn't have 16 bit float?
    # np.object #this too should detect basic numpy array
    # How to detect fixed length array?
    if dtype in TYPES_NUMPY2ROOT:
        nbytes, roottype = TYPES_NUMPY2ROOT[dtype]
        return new ScalarNP2CConverter(tree, name, roottype, nbytes)
    elif dtype == np.dtype(np.object):
        warnings.warn("converter for %r not implemented yet (skipping)" % dtype)
        return NULL
        # let's peek
        """
        if type(peekvalue) == type(np.array([])):
            ndim = peekvalue.ndim
            dtype = peekvalue.dtype
            #TODO finish this
        """
    else:
        warnings.warn("converter for %r not implemented yet (skipping)" % dtype)
    return NULL


cdef TTree* array2tree(np.ndarray arr, name='tree', TTree* tree=NULL) except *:
    # hmm how do I catch all python exception
    # and clean up before throwing ?
    cdef vector[NP2CConverter*] conv_array
    cdef vector[int] posarray
    cdef vector[int] roffsetarray
    cdef auto_ptr[NP2CConverter] tmp
    cdef unsigned int icv
    cdef int icol
    cdef long arr_len = arr.shape[0]
    cdef long idata
    cdef unsigned long pos_len
    cdef unsigned long ipos
    cdef void* source = NULL
    cdef void* thisrow = NULL
    cdef NP2CConverter* tmpcv
    
    try: 
        if tree == NULL:
            tree = new TTree(name, name)
        
        fieldnames = arr.dtype.names
        fields = arr.dtype.fields
        
        # figure out the structure
        for icol in range(len(fieldnames)):
            fieldname = fieldnames[icol]
            # roffset is an offset of particular field in each record
            dtype, roffset = fields[fieldname] 
            cvt = find_np2c_converter(tree, fieldname, dtype, arr[0][fieldname])
            if cvt is not NULL:
                roffsetarray.push_back(roffset)
                conv_array.push_back(cvt)
                posarray.push_back(icol)

        # fill in data
        pos_len = posarray.size()
        for idata in range(arr_len):
            thisrow = np.PyArray_GETPTR1(arr, idata)
            for ipos in range(pos_len):
                roffset = roffsetarray[ipos]
                source = shift(thisrow, roffset)
                conv_array[ipos].fill_from(source)
        
        # need to update the number of entries in the tree to match
        # the number in the branches since each branch is filled separately.
        tree.SetEntries(-1)
    
    except:
        raise
    
    finally:
        # how do I clean up TTree?
        # root has some global funny memory management...
        # need to make sure no double free
        for icv in range(conv_array.size()):
            tmpcv = conv_array[icv]
            del tmpcv

    return tree


def array2tree_toCObj(arr, name='tree', tree=None):
    cdef TTree* intree = NULL
    cdef TTree* outtree = NULL
    if tree is not None:
        # this is not a safe method
        # provided here for convenience only
        # typecheck should be implemented by the wrapper
        if not PyCObject_Check(tree):
            raise ValueError("tree must be PyCObject")
        intree = <TTree*> PyCObject_AsVoidPtr(tree)
    outtree = array2tree(arr, name=name, tree=intree)
    return PyCObject_FromVoidPtr(outtree, NULL)


def array2root(arr, filename, treename='tree', mode='update'):
    cdef TFile* file = Open(filename, mode)
    if file is NULL:
        raise IOError("cannot open file {0}".format(filename))
    if not file.IsWritable():
        raise IOError("file {0} is not writable".format(filename))

    # If a tree with that name exists, we want to update it
    cdef TTree* tree = <TTree*> file.Get(treename)
    tree = array2tree(arr, name=treename, tree=tree)
    tree.Write(treename, 2) # TObject::kOverwrite
    file.Close()
    # how to clean up TTree? Same question as above.
    del file


@atexit.register
def cleanup():
    # delete all allocated converters 
    it = CONVERTERS.begin()
    while it != CONVERTERS.end():
        del deref(it).second
        inc(it)
