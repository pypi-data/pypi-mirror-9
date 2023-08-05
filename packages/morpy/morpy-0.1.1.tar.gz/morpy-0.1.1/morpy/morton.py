from copy import copy
class MortonLib(object):
    """docstring for MortonLib"""
    def __init__(self, ndim=3):
        self.ndim = ndim

    def morton_to_ijk(self, key):
        iarr = [0]*self.ndim
        level = 0
        while key > 0:
            for d in range(self.ndim):
                iarr[self.ndim-d-1] += (key & 1) << level
                key = key >> 1
            level += 1
        return iarr

    def ijk_to_morton(self, iarr):
        iarr = copy(iarr)
        m = 0
        level = 0
        while any([i > 0 for i in iarr]):
            for d, i in enumerate(iarr):
                m |= (i & 1) << (self.ndim*level + (self.ndim-d-1))
                iarr[d] = iarr[d] >> 1
            level += 1
        return m

def test_all():
    mlib = MortonLib(ndim=8)
    for m in range(4**3):
        iarr = mlib.morton_to_ijk(m)
        n = mlib.ijk_to_morton(iarr)
        print iarr, m, n
        assert m==n
    print 'Test passed'

if __name__ == "__main__":
    test_all()
