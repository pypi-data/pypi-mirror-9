import numpy as np
from time import time
from cmorton import MortonLib

def test_types():
    mlib = MortonLib(8)
    k = np.random.randint(int(1e6))
    i32 = mlib.get_cell(k)
    mlib.get_cell(long(k))
    i64 = i32.astype('uint64')
    print k, i32, mlib.get_key(i32)
    mlib.get_key(i32)
    mlib.get_key(i64)

def time_decode():
    mlib = MortonLib(3)
    N = int(1e6)
    t1 = -time()
    for i in xrange(N):
        mlib.get_cell(i)
    t1 += time()
    print 'Decoded %i in %e seconds' % (N, t1)

def time_decode_arr():
    mlib = MortonLib(3)
    N = int(1e6)
    t1 = -time()
    arr = np.arange(N)
    mlib.get_cells(arr)
    t1 += time()
    print 'Array decoded %i in %e seconds' % (N, t1)

def test_all():
    mlib = MortonLib(ndim=3)
    t1 = -time()
    for m in range(4**3):
        iarr = mlib.get_cell(m)
        n = mlib.get_key(iarr)
        # print iarr, m, n
        assert m==n
    t1 += time()
    print 'keys encoded/decoded in %e seconds' % (t1)
    print 'Test passed'

def test_arr():
    mlib = MortonLib(6)
    marr = np.arange(int(1e6))
    t1 = -time()
    iarr = mlib.get_cells(marr)
    t1 += time()
    print 'Array decoded in %e seconds' % (t1)
    t1 = -time()
    marr2 = mlib.get_keys(iarr)
    t1 += time()
    print 'Array encoded in %e seconds' % (t1)
    assert np.all(marr == marr2)

if __name__ == "__main__":
    test_types()
    time_decode_arr()
    test_all()
    test_arr()
    # time_decode_arr()
    # test_all()
