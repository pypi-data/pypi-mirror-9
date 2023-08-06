import os
from os.path import dirname, join
import tempfile
import warnings

import numpy as np
from numpy.lib import recfunctions
from numpy.testing import assert_array_equal

import ROOT
from ROOT import (
    TChain, TFile, TTree,
    TH1D, TH2D, TH3D,
    TProfile, TProfile2D, TProfile3D,
    TGraph, TGraph2D,
    TF1, TF2, TF3, TFormula,
    TLorentzVector)

import root_numpy as rnp
from root_numpy.testdata import get_filepath, get_file

try:
    from collections import OrderedDict
except ImportError:
    from root_numpy.extern.ordereddict import OrderedDict

from nose.tools import (raises, assert_raises, assert_true,
                        assert_equal, assert_almost_equal)


ROOT.gErrorIgnoreLevel = ROOT.kFatal
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=rnp.RootNumpyUnconvertibleWarning)


def load(data):
    if isinstance(data, list):
        return [get_filepath(x) for x in data]
    else:
        return get_filepath(data)


def check_single(single, n=100, offset=1):
    assert_equal(
        single.dtype,
        [('n_int', '<i4'), ('f_float', '<f4'), ('d_double', '<f8')])
    assert_equal(len(single), n)
    for i in range(len(single)):
        offset = (i // 100) + 1
        assert_equal(single[i][0], i % 100 + offset)
        assert_almost_equal(single[i][1], i % 100 * 2.0 + offset)
        assert_almost_equal(single[i][2], i % 100 * 3.0 + offset)


def test_list_trees():
    # TTree
    trees = rnp.list_trees(load('vary1.root'))
    assert_equal(trees, ['tree'])
    # TNtuple
    trees = rnp.list_trees(load('ntuple.root'))
    assert_equal(trees, ['ntuple'])


def test_list_branches():
    branches = rnp.list_branches(load('single1.root'))
    assert_equal(branches, ['n_int', 'f_float', 'd_double'])


def test_list_structures():
    structure = rnp.list_structures(load('single1.root'))
    expected = OrderedDict([
        ('n_int', [('n_int', 'int')]),
        ('f_float', [('f_float', 'float')]),
        ('d_double', [('d_double', 'double')])])
    assert_equal(structure, expected)


def test_ntuple():
    f = load('ntuple.root')
    a = rnp.root2array(f)
    assert_equal(len(a), 10)
    assert_equal(len(a.dtype.names), 3)


def test_single():
    f = load('single1.root')
    a = rnp.root2array(f)
    check_single(a)
    # specify tree name
    a = rnp.root2array(f, treename='tree')
    check_single(a)


@raises(IOError)
def test_single_pattern_not_exist():
    f = load(['single1.root','does_not_exist.root'])
    a = rnp.root2array(f)


@raises(ValueError)
def test_no_filename():
    rnp.root2array([])


def test_no_trees_in_file():
    f = ROOT.TFile.Open('temp_file.root', 'recreate')
    f.Close()
    assert_raises(IOError, rnp.root2array, ['temp_file.root'], treename=None)
    os.remove('temp_file.root')


@raises(IOError)
def test_single_filename_not_exist():
    f = load('does_not_exist.root')
    a = rnp.root2array(f)


@raises(ValueError)
def test_double_tree_name_not_specified():
    f = load('doubletree1.root')
    a = rnp.root2array(f)


def test_single_chain():
    f = load(['single1.root', 'single2.root'])
    a = rnp.root2array(f)
    check_single(a, 200)


def test_tree_without_branches():
    tree = TTree('test', 'test')
    assert_raises(ValueError, rnp.tree2rec, tree)


def test_empty_branches():
    f = load('single1.root')
    assert_raises(ValueError, rnp.root2array, f, branches=[])


def test_empty_tree():
    from array import array
    tree = TTree('tree', 'tree')
    d = array('d', [0.])
    tree.Branch('double', d, 'double/D')
    rnp.tree2array(tree)


def test_unsupported_branch_in_branches():
    tree = TTree('test', 'test')
    vect = TLorentzVector()
    double = np.array([0], dtype=float)
    tree.Branch('vector', vect)
    tree.Branch('double', double, 'double/D')
    rnp.tree2array(tree)
    assert_raises(TypeError, rnp.tree2array, tree, branches=['vector'])


def test_no_supported_branches():
    tree = TTree('test', 'test')
    vect = TLorentzVector()
    tree.Branch('vector', vect)
    assert_raises(RuntimeError, rnp.tree2array, tree)


def test_fixed():
    f = load(['fixed1.root', 'fixed2.root'])
    a = rnp.root2array(f)
    assert_equal(
        a.dtype,
        [('n_int', '<i4', (5,)),
            ('f_float', '<f4', (7,)),
            ('d_double', '<f8', (10,))])
    #TODO: Write a proper check method
    assert_equal(a[0][0][0], 1)
    assert_equal(a[0][0][1], 2)
    assert_almost_equal(a[-1][2][-1], 1514.5)


def test_vary():
    f = load(['vary1.root', 'vary2.root'])
    a = rnp.root2rec(f)
    assert_equal(
        a.dtype,
        [('len_n', '<i4'), ('len_f', '<i4'), ('len_d', '<i4'),
         ('n_char', 'O'), ('n_uchar', 'O'),
         ('n_short', 'O'), ('n_ushort', 'O'),
         ('n_int', 'O'), ('n_uint', 'O'),
         ('n_long', 'O'), ('n_ulong', 'O'),
         ('f_float', 'O'), ('d_double', 'O')])

    #check length
    for i in range(len(a)):
        assert_equal(a.len_n[i], len(a.n_int[i]))
        assert_equal(a.len_f[i], len(a.f_float[i]))
        assert_equal(a.len_d[i], len(a.d_double[i]))
    #couple element check
    assert_equal(a.len_n[0], 0)
    assert_equal(a.len_f[0], 1)
    assert_equal(a.len_d[0], 2)
    assert_equal(a.n_int[-1][-1], 417)
    assert_equal(a.f_float[-1][0], 380.5)
    assert_equal(a.f_float[-1][-1], 456.5)
    assert_equal(a.d_double[-1][0], 380.25)
    assert_equal(a.d_double[-1][-1], 497.25)


def test_tree2array():
    chain = TChain('tree')
    chain.Add(load('single1.root'))
    check_single(rnp.tree2array(chain))

    f = get_file('single1.root')
    tree = f.Get('tree')
    check_single(rnp.tree2array(tree))

    assert_raises(ValueError, get_file, 'file_does_not_exist.root')


def test_tree2rec():
    chain = TChain('tree')
    chain.Add(load('single1.root'))
    check_single(rnp.tree2array(chain))


def test_selection():
    chain = TChain('tree')
    chain.Add(load('single1.root'))
    chain.Add(load('single2.root'))
    a = rnp.tree2rec(chain, selection="d_double > 100")
    assert_equal((a['d_double'] <= 100).any(), False)

    # selection with differing variables in branches and expression
    a = rnp.tree2array(chain,
        branches=['d_double'],
        selection="f_float < 100 && n_int%2 == 1")

    # selection with TMath
    a = rnp.tree2rec(chain,
        selection="TMath::Erf(d_double) < 0.5")


def test_expression():
    rec = rnp.root2rec(load('single*.root'))
    rec2 = rnp.root2rec(load('single*.root'), branches=['f_float*2'])
    assert_array_equal(rec['f_float'] * 2, rec2['f_float*2'])


def test_selection_and_expression():
    ref = len(rnp.root2rec(
        load('test.root'), branches=['x', 'y'], selection='z>0'))
    assert_equal(ref,
        len(rnp.root2rec(
            load('test.root'), branches=['x', 'y', 'z'], selection='z>0')))
    assert_equal(ref,
        len(rnp.root2rec(
            load('test.root'), branches=['x', 'x*y'], selection='z>0')))
    assert_equal(ref,
        len(rnp.root2rec(
            load('test.root'), branches=['x', 'x*z'], selection='z>0')))


def test_branch_status():
    # test that original branch status is preserved
    chain = TChain('tree')
    chain.Add(load('single1.root'))
    chain.Add(load('single2.root'))
    chain.SetBranchStatus('d_double', False)
    a = rnp.tree2rec(chain, selection="d_double > 100")
    assert_equal(chain.GetBranchStatus('d_double'), False)


@raises(ValueError)
def test_branch_DNE():
    chain = TChain('tree')
    chain.Add(load('single1.root'))
    rnp.tree2array(chain, branches=['my_net_worth'])


@raises(TypeError)
def test_tree2array_wrong_type():
    rnp.tree2array(list())


def test_specific_branch():
    a = rnp.root2rec(load('single1.root'), branches=['f_float'])
    assert_equal(a.dtype, [('f_float', '<f4')])


def test_vector():
    a = rnp.root2rec(load('vector.root'))
    types = [
        ('v_i', 'O'),
        ('v_f', 'O'),
        ('v_F', 'O'),
        ('v_d', 'O'),
        ('v_l', 'O'),
        ('v_c', 'O'),
        ('v_b', 'O'),
        ('vv_i', 'O'),
        ('vv_f', 'O'),
        ('vv_F', 'O'),
        ('vv_d', 'O'),
        ('vv_l', 'O'),
        ('vv_c', 'O'),
        ('vv_b', 'O'),
    ]
    assert_equal(a.dtype, types)

    assert_equal(a.v_i[0].dtype, np.int32)
    assert_equal(a.v_f[0].dtype, np.float32)
    assert_equal(a.v_F[0].dtype, np.float32)
    assert_equal(a.v_d[0].dtype, np.float64)
    assert_equal(a.v_l[0].dtype, np.int64)
    assert_equal(a.v_c[0].dtype, np.int8)
    assert_equal(a.v_b[0].dtype, np.bool)

    # assert that wrapper array is np.object
    assert_equal(a.vv_i[0].dtype, np.object)
    assert_equal(a.vv_f[0].dtype, np.object)
    assert_equal(a.vv_F[0].dtype, np.object)
    assert_equal(a.vv_d[0].dtype, np.object)
    assert_equal(a.vv_l[0].dtype, np.object)
    assert_equal(a.vv_c[0].dtype, np.object)
    assert_equal(a.vv_b[0].dtype, np.object)

    assert_equal(a.vv_i[0][0].dtype, np.int32)
    assert_equal(a.vv_f[0][0].dtype, np.float32)
    assert_equal(a.vv_F[0][0].dtype, np.float32)
    assert_equal(a.vv_d[0][0].dtype, np.float64)
    assert_equal(a.vv_l[0][0].dtype, np.int64)
    assert_equal(a.vv_c[0][0].dtype, np.int8)
    assert_equal(a.vv_b[0][0].dtype, np.bool)

    # check a few values
    assert_equal(a.v_i[0][0], 1)
    assert_equal(a.v_i[1][1], 3)
    assert_equal(a.v_i[-2][0], 9)
    assert_equal(a.v_i[-2][-1], 17)

    assert_equal(a.v_f[0][0], 2.0)
    assert_equal(a.v_f[1][1], 5.0)
    assert_equal(a.v_f[-2][0], 18.0)
    assert_equal(a.v_f[-2][-1], 26.0)

    assert_equal(a.v_F[0][0], 2.0)
    assert_equal(a.v_F[1][1], 5.0)
    assert_equal(a.v_F[-2][0], 18.0)
    assert_equal(a.v_F[-2][-1], 26.0)

    # more strict conditioning for numpy arrays
    def assert_equal_array(arr1, arr2):
        return assert_equal((arr1 == arr2).all(), True,
            "array mismatch: {0} != {1}".format(arr1, arr2))

    assert_equal_array(a.vv_i[0][0], np.array([1], dtype=np.int32) )
    assert_equal_array(a.vv_i[1][1], np.array([2, 3], dtype=np.int32) )
    assert_equal_array(a.vv_i[-2][0], np.array([9], dtype=np.int32) )
    assert_equal_array(a.vv_i[-2][-1],
                       np.array([ 9, 10, 11, 12, 13, 14, 15, 16, 17],
                                dtype=np.int32))

    assert_equal_array(a.vv_f[0][0], np.array([ 2.], dtype=np.float32) )
    assert_equal_array(a.vv_f[1][1], np.array([ 4.,  5.], dtype=np.float32) )
    assert_equal_array(a.vv_f[-2][0], np.array([ 18.], dtype=np.float32) )
    assert_equal_array(a.vv_f[-2][-1],
                       np.array([ 18.,  19.,  20.,  21.,  22.,
                                  23.,  24.,  25.,  26.],
                                dtype=np.float32))

    assert_equal_array(a.vv_F[0][0], np.array([ 2.], dtype=np.float32) )
    assert_equal_array(a.vv_F[1][1], np.array([ 4.,  5.], dtype=np.float32) )
    assert_equal_array(a.vv_F[-2][0], np.array([ 18.], dtype=np.float32) )
    assert_equal_array(a.vv_F[-2][-1],
                       np.array([ 18.,  19.,  20.,  21.,  22.,
                                  23.,  24.,  25.,  26.],
                                dtype=np.float32))


def test_string():
    a = rnp.root2rec(load('string.root'))
    types = [
        ('message', 'O'),
        ('vect', 'O'),
        ('vect2d', 'O'),
    ]
    assert_equal(a.dtype, types)
    assert_equal(a[0][0], 'Hello World!')
    assert_equal(a[0][1][0], 'Hello!')
    assert_equal(a[0][2][0][0], 'Hello!')


def test_slice():
    a = rnp.root2rec(load('single1.root'), stop=10)
    assert_equal(len(a), 10)
    assert_equal(a.n_int[-1], 10)

    a = rnp.root2rec(load('single1.root'), stop=11, start=1)
    assert_equal(len(a), 10)
    assert_equal(a.n_int[-1], 11)

    a = rnp.root2rec(load('single1.root'), stop=105, start=95)
    assert_equal(len(a), 5)
    assert_equal(a.n_int[-1], 100)


def test_weights():
    f = TFile(load('test.root'))
    tree = f.Get('tree')
    tree.SetWeight(5.)
    rec = rnp.tree2rec(tree, include_weight=True, weight_name='treeweight')
    assert_array_equal(rec['treeweight'], np.ones(100) * 5)
    f = load(['single1.root', 'single2.root'])
    a = rnp.root2array(f, include_weight=True)
    assert_array_equal(a['weight'],
        np.concatenate((np.ones(100) * 2., np.ones(100) * 3.)))


def test_PyROOT():
    f = TFile(load('single1.root'))
    tree = f.Get('tree')
    rnp.tree2array(tree)


def test_fill_hist():
    np.random.seed(0)
    data1D = np.random.randn(1E6)
    w1D = np.empty(1E6)
    w1D.fill(2.)
    data2D = np.random.randn(1E6, 2)
    data3D = np.random.randn(1E4, 3)

    a = TH1D('th1d', 'test', 1000, -5, 5)
    rnp.fill_hist(a, data1D)
    # one element lies beyond hist range; that's why it's not 1e6
    assert_almost_equal(a.Integral(), 999999.0)

    a_w = TH1D('th1dw', 'test', 1000, -5, 5)
    rnp.fill_hist(a_w, data1D, w1D)
    assert_almost_equal(a_w.Integral(), 999999.0 * 2)

    b = TH2D('th2d', 'test', 100, -5, 5, 100, -5, 5)
    rnp.fill_hist(b, data2D)
    assert_almost_equal(b.Integral(), 999999.0)

    c = TH3D('th3d', 'test', 10, -5, 5, 10, -5, 5, 10, -5, 5)
    rnp.fill_hist(c, data3D)
    assert_almost_equal(c.Integral(), 10000.0)

    # array and weights lengths do not match
    assert_raises(ValueError, rnp.fill_hist, c, data3D, np.ones(10))

    # weights is not 1D
    assert_raises(ValueError, rnp.fill_hist, c, data3D,
        np.ones((data3D.shape[0], 1)))

    # array not 2-d when filling 2D/3D histogram
    for h in (b, c):
        assert_raises(ValueError, rnp.fill_hist, h, np.random.randn(1E4))

    # length of second axis does not match dimensionality of histogram
    for h in (a, b, c):
        assert_raises(ValueError, rnp.fill_hist, h, np.random.randn(1E4, 4))

    # wrong type
    h = list()
    a = np.random.randn(100)
    assert_raises(TypeError, rnp.fill_hist, h, a)


def test_fill_profile():
    np.random.seed(0)
    w1D = np.empty(1E6)
    w1D.fill(2.)
    data1D = np.random.randn(1E6, 2)
    data2D = np.random.randn(1E6, 3)
    data3D = np.random.randn(1E4, 4)

    a = TProfile('th1d', 'test', 1000, -5, 5)
    rnp.fill_profile(a, data1D)
    assert_true(a.Integral() !=0)

    a_w = TProfile('th1dw', 'test', 1000, -5, 5)
    rnp.fill_profile(a_w, data1D, w1D)
    assert_true(a_w.Integral() != 0)
    assert_equal(a_w.Integral(), a.Integral())

    b = TProfile2D('th2d', 'test', 100, -5, 5, 100, -5, 5)
    rnp.fill_profile(b, data2D)
    assert_true(b.Integral() != 0)

    c = TProfile3D('th3d', 'test', 10, -5, 5, 10, -5, 5, 10, -5, 5)
    rnp.fill_profile(c, data3D)
    assert_true(c.Integral() != 0)

    # array and weights lengths do not match
    assert_raises(ValueError, rnp.fill_profile, c, data3D, np.ones(10))

    # weights is not 1D
    assert_raises(ValueError, rnp.fill_profile, c, data3D,
                  np.ones((data3D.shape[0], 1)))

    # array is not 2D
    assert_raises(ValueError, rnp.fill_profile, c, np.ones(10))

    # length of second axis is not one more than dimensionality of the profile
    for h in (a, b, c):
        assert_raises(ValueError, rnp.fill_profile, h, np.random.randn(1E4, 5))

    # wrong type
    assert_raises(TypeError, rnp.fill_profile,
                  TH1D("test", "test", 1, 0, 1), data1D)


def test_fill_graph():
    np.random.seed(0)
    data2D = np.random.randn(1E6, 2)
    data3D = np.random.randn(1E4, 3)

    graph = TGraph()
    rnp.fill_graph(graph, data2D)

    graph2d = TGraph2D()
    rnp.fill_graph(graph2d, data3D)

    # array not 2-d
    for g in (graph, graph2d):
        assert_raises(ValueError, rnp.fill_graph, g, np.random.randn(1E4))

    # length of second axis does not match dimensionality of histogram
    for g in (graph, graph2d):
        assert_raises(ValueError, rnp.fill_graph, g, np.random.randn(1E4, 4))

    # wrong type
    h = list()
    a = np.random.randn(100)
    assert_raises(TypeError, rnp.fill_graph, h, a)


def test_stretch():
    nrec = 5
    arr = np.empty(nrec,
        dtype=[
            ('scalar', np.int),
            ('df1', 'O'),
            ('df2', 'O'),
            ('df3', 'O')])

    for i in range(nrec):
        df1 = np.array(range(i + 1), dtype=np.float)
        df2 = np.array(range(i + 1), dtype=np.int) * 2
        df3 = np.array(range(i + 1), dtype=np.double) * 3
        arr[i] = (i, df1, df2, df3)

    stretched = rnp.stretch(
        arr, ['scalar', 'df1', 'df2', 'df3'])

    assert_equal(stretched.dtype,
        [('scalar', np.int),
         ('df1', np.float),
         ('df2', np.int),
         ('df3', np.double)])
    assert_equal(stretched.size, 15)

    assert_almost_equal(stretched['df1'][14], 4.0)
    assert_almost_equal(stretched['df2'][14], 8)
    assert_almost_equal(stretched['df3'][14], 12.0)
    assert_almost_equal(stretched['scalar'][14], 4)
    assert_almost_equal(stretched['scalar'][13], 4)
    assert_almost_equal(stretched['scalar'][12], 4)
    assert_almost_equal(stretched['scalar'][11], 4)
    assert_almost_equal(stretched['scalar'][10], 4)
    assert_almost_equal(stretched['scalar'][9], 3)

    arr = np.empty(1, dtype=[('scalar', np.int),])
    arr[0] = (1,)
    assert_raises(RuntimeError, rnp.stretch, arr, ['scalar',])

    nrec = 5
    arr = np.empty(nrec,
        dtype=[
            ('scalar', np.int),
            ('df1', 'O'),
            ('df2', 'O')])

    for i in range(nrec):
        df1 = np.array(range(i + 1), dtype=np.float)
        df2 = np.array(range(i + 2), dtype=np.int) * 2
        arr[i] = (i, df1, df2)
    assert_raises(ValueError, rnp.stretch, arr, ['scalar', 'df1', 'df2'])


def test_blockwise_inner_join():
    test_data = np.array([
        (1.0, np.array([11,12,13]), np.array([1,0,1]), 0, np.array([1,2,3])),
        (2.0, np.array([21,22,23]), np.array([-1,2,-1]), 1, np.array([31,32,33]))],
        dtype=[
            ('sl', np.float),
            ('al', 'O'),
            ('fk', 'O'),
            ('s_fk', np.int),
            ('ar', 'O')])
    # vector join
    a1 = rnp.blockwise_inner_join(
        test_data, ['sl', 'al'], test_data['fk'], ['ar'])

    # specify fk with string
    a1 = rnp.blockwise_inner_join(
        test_data, ['sl', 'al'], 'fk', ['ar'])

    exp1 = np.array([
        (1.0, 11, 2, 1),
        (1.0, 12, 1, 0),
        (1.0, 13, 2, 1),
        (2.0, 22, 33, 2)],
        dtype=[
            ('sl', '<f8'),
            ('al', '<i8'),
            ('ar', '<i8'),
            ('fk', '<i8')])
    assert_array_equal(a1, exp1, verbose=True)

    # vector join with force repeat
    a2 = rnp.blockwise_inner_join(
        test_data, ['sl','al'], test_data['fk'], ['ar'], force_repeat=['al'])
    exp2 = np.array([
        (1.0, np.array([11, 12, 13]), 2, 1),
        (1.0, np.array([11, 12, 13]), 1, 0),
        (1.0, np.array([11, 12, 13]), 2, 1),
        (2.0, np.array([21, 22, 23]), 33, 2)],
        dtype=[
            ('sl', '<f8'),
            ('al', '|O8'),
            ('ar', '<i8'),
            ('fk', '<i8')])
    assert_equal(str(a2), str(exp2)) # numpy testing doesn't like subarray
    assert_equal(a2.dtype, exp2.dtype)

    # scalar join
    a3 = rnp.blockwise_inner_join(
        test_data, ['sl', 'al'], test_data['s_fk'], ['ar'])
    exp3 = np.array([
        (1.0, [11, 12, 13], 1, 0),
        (2.0, [21, 22, 23], 32, 1)],
        dtype=[
            ('sl', '<f8'),
            ('al', '|O8'),
            ('ar', '<i8'),
            ('fk', '<i8')])
    assert_equal(str(a3), str(exp3)) # numpy testing doesn't like subarray
    assert_equal(a3.dtype, exp3.dtype)


def test_struct():
    assert_array_equal(rnp.root2rec(load('struct.root')),
        np.array([(10, 15.5, 20, 781.2)],
            dtype=[
                ('branch1_intleaf', '<i4'),
                ('branch1_floatleaf', '<f4'),
                ('branch2_intleaf', '<i4'),
                ('branch2_floatleaf', '<f4')]))


def test_array2tree():
    a = np.array([
        (12345, 2., 2.1, True),
        (3, 4., 4.2, False),],
        dtype=[
            ('x', np.int32),
            ('y', np.float32),
            ('z', np.float64),
            ('w', np.bool)])
    tmp = ROOT.TFile.Open('test_array2tree_temp_file.root', 'recreate')
    tree = rnp.array2tree(a)
    a_conv = rnp.tree2array(tree)
    assert_array_equal(a, a_conv)
    # extend the tree
    tree2 = rnp.array2tree(a, tree=tree)
    assert_equal(tree2.GetEntries(), len(a) * 2)
    a_conv2 = rnp.tree2array(tree2)
    assert_array_equal(np.hstack([a, a]), a_conv2)
    tmp.Close()
    os.remove(tmp.GetName())
    assert_raises(TypeError, rnp.array2tree, a, tree=object)


def test_array2root():
    a = np.array([
        (12345, 2., 2.1, True),
        (3, 4., 4.2, False),],
        dtype=[
            ('x', np.int32),
            ('y', np.float32),
            ('z', np.float64),
            ('w', np.bool)])
    tmp_fd, tmp_path = tempfile.mkstemp(suffix='.root')
    rnp.array2root(a, tmp_path, mode='recreate')
    a_conv = rnp.root2array(tmp_path)
    assert_array_equal(a, a_conv)
    # extend the tree
    rnp.array2root(a, tmp_path, mode='update')
    a_conv2 = rnp.root2array(tmp_path)
    assert_array_equal(np.hstack([a, a]), a_conv2)
    os.close(tmp_fd)
    os.remove(tmp_path)


def test_random_sample_f1():
    func = TF1("f1", "TMath::DiLog(x)")
    sample = rnp.random_sample(func, 100)
    assert_equal(sample.shape, (100,))
    rnp.random_sample(func, 100, seed=1)


def test_random_sample_f2():
    func = TF2("f2", "sin(x)*sin(y)/(x*y)")
    sample = rnp.random_sample(func, 100)
    assert_equal(sample.shape, (100, 2))


def test_random_sample_f3():
    func = TF3("f3", "sin(x)*sin(y)*sin(z)/(x*y*z)")
    sample = rnp.random_sample(func, 100)
    assert_equal(sample.shape, (100, 3))


def test_random_sample_h1():
    hist = TH1D("h1", "h1", 10, -3, 3)
    sample = rnp.random_sample(hist, 100)
    assert_equal(sample.shape, (100,))


def test_random_sample_h2():
    hist = TH2D("h2", "h2", 10, -3, 3, 10, -3, 3)
    sample = rnp.random_sample(hist, 100)
    assert_equal(sample.shape, (100, 2))


def test_random_sample_h3():
    hist = TH3D("h3", "h3", 10, -3, 3, 10, -3, 3, 10, -3, 3)
    sample = rnp.random_sample(hist, 100)
    assert_equal(sample.shape, (100, 3))


def test_random_sample_bad_input():
    func = TF1("f1", "TMath::DiLog(x)")
    assert_raises(ValueError, rnp.random_sample, func, 0)
    assert_raises(ValueError, rnp.random_sample, func, 10, seed=-1)
    assert_raises(TypeError, rnp.random_sample, object, 10)


def test_array():
    for copy in (True, False):
        for cls in (getattr(ROOT, 'TArray{0}'.format(atype))
                for atype in 'DFLIS'):
            a = cls(10)
            a[2] = 2
            b = rnp.array(a, copy=copy)
            assert_equal(b[2], 2)
            assert_equal(b.shape[0], 10)
        a = ROOT.TArrayC(10)
        b = rnp.array(a, copy=copy)
        assert_equal(b.shape[0], 10)
    assert_raises(TypeError, rnp.array, object)


def test_matrix():
    for cls in (getattr(ROOT, 'TMatrix{0}'.format(atype)) for atype in 'DF'):
        m = cls(5, 5)
        m[1][2] = 2
        n = rnp.matrix(m)
        assert_equal(n[1, 2], 2)

    for cls in (getattr(ROOT, 'TMatrix{0}Sym'.format(atype)) for atype in 'DF'):
        m = cls(5)
        m[2][2] = 2
        n = rnp.matrix(m)
        assert_equal(n[2, 2], 2)

    assert_raises(TypeError, rnp.matrix, object)


def test_rec2array():
    a = np.array([
        (12345, 2., 2.1, True),
        (3, 4., 4.2, False),],
        dtype=[
            ('x', np.int32),
            ('y', np.float32),
            ('z', np.float64),
            ('w', np.bool)])
    arr = rnp.rec2array(a)
    assert_array_equal(arr,
        np.array([
            [12345, 2, 2.1, 1],
            [3, 4, 4.2, 0]]))
    arr = rnp.rec2array(a, fields=['x', 'y'])
    assert_array_equal(arr,
        np.array([
            [12345, 2],
            [3, 4]]))
    # single field
    arr = rnp.rec2array(a, fields=['x'])
    assert_equal(arr.ndim, 1)
    assert_equal(arr.shape, (a.shape[0],))


def test_stack():
    rec = rnp.root2rec(load('test.root'))
    s = rnp.stack([rec, rec])
    assert_equal(s.shape[0], 2 * rec.shape[0])
    assert_equal(s.dtype.names, rec.dtype.names)
    s = rnp.stack([rec, rec], fields=['x', 'y'])
    assert_equal(s.shape[0], 2 * rec.shape[0])
    assert_equal(s.dtype.names, ('x', 'y'))
    # recs don't have identical fields
    rec2 = recfunctions.drop_fields(rec, ['i', 'x'])
    s = rnp.stack([rec, rec2])
    assert_equal(set(s.dtype.names), set(['y', 'z']))


def test_dup_idx():
    a = [1, 2, 3, 4, 3, 2]
    assert_array_equal(rnp.dup_idx(a), [1, 2, 4, 5])


def test_evaluate():
    # create functions and histograms
    f1 = TF1("f1", "x")
    f2 = TF2("f2", "x*y")
    f3 = TF3("f3", "x*y*z")
    h1 = TH1D("h1", "", 10, 0, 1)
    h1.FillRandom("f1")
    h2 = TH2D("h2", "", 10, 0, 1, 10, 0, 1)
    h2.FillRandom("f2")
    h3 = TH3D("h3", "", 10, 0, 1, 10, 0, 1, 10, 0, 1)
    h3.FillRandom("f3")
    # generate random arrays
    arr_1d = np.random.rand(5)
    arr_2d = np.random.rand(5, 2)
    arr_3d = np.random.rand(5, 3)
    arr_4d = np.random.rand(5, 4)
    # evaluate the functions
    assert_array_equal(rnp.evaluate(f1, arr_1d),
                       [f1.Eval(x) for x in arr_1d])
    assert_array_equal(rnp.evaluate(f1.GetTitle(), arr_1d),
                       [f1.Eval(x) for x in arr_1d])
    assert_array_equal(rnp.evaluate(f2, arr_2d),
                       [f2.Eval(*x) for x in arr_2d])
    assert_array_equal(rnp.evaluate(f2.GetTitle(), arr_2d),
                       [f2.Eval(*x) for x in arr_2d])
    assert_array_equal(rnp.evaluate(f3, arr_3d),
                       [f3.Eval(*x) for x in arr_3d])
    assert_array_equal(rnp.evaluate(f3.GetTitle(), arr_3d),
                       [f3.Eval(*x) for x in arr_3d])
    # 4d formula
    f4 = TFormula('test', 'x*y+z*t')
    assert_array_equal(rnp.evaluate(f4, arr_4d),
                       [f4.Eval(*x) for x in arr_4d])
    # evaluate the histograms
    assert_array_equal(rnp.evaluate(h1, arr_1d),
                       [h1.GetBinContent(h1.FindBin(x)) for x in arr_1d])
    assert_array_equal(rnp.evaluate(h2, arr_2d),
                       [h2.GetBinContent(h2.FindBin(*x)) for x in arr_2d])
    assert_array_equal(rnp.evaluate(h3, arr_3d),
                       [h3.GetBinContent(h3.FindBin(*x)) for x in arr_3d])
    # create a graph
    g = TGraph(2)
    g.SetPoint(0, 0, 1)
    g.SetPoint(1, 1, 2)
    assert_array_equal(rnp.evaluate(g, [0, .5, 1]), [1, 1.5, 2])
    from ROOT import TSpline3
    s = TSpline3("spline", g)
    assert_array_equal(rnp.evaluate(s, [0, .5, 1]),
                       [s.Eval(x) for x in [0, .5, 1]])
    # test exceptions
    assert_raises(TypeError, rnp.evaluate, object(), [1, 2, 3])
    assert_raises(ValueError, rnp.evaluate, h1, arr_2d)
    assert_raises(ValueError, rnp.evaluate, h2, arr_3d)
    assert_raises(ValueError, rnp.evaluate, h2, arr_1d)
    assert_raises(ValueError, rnp.evaluate, h3, arr_1d)
    assert_raises(ValueError, rnp.evaluate, h3, arr_2d)
    assert_raises(ValueError, rnp.evaluate, f1, arr_2d)
    assert_raises(ValueError, rnp.evaluate, f2, arr_3d)
    assert_raises(ValueError, rnp.evaluate, f2, arr_1d)
    assert_raises(ValueError, rnp.evaluate, f3, arr_1d)
    assert_raises(ValueError, rnp.evaluate, f3, arr_2d)
    assert_raises(ValueError, rnp.evaluate, g, arr_2d)
    assert_raises(ValueError, rnp.evaluate, s, arr_2d)
    assert_raises(ValueError, rnp.evaluate, "f", arr_1d)
    assert_raises(ValueError, rnp.evaluate, "x*y", arr_1d)
    assert_raises(ValueError, rnp.evaluate, "x", arr_2d)
    assert_raises(ValueError, rnp.evaluate, "x*y", arr_3d)
