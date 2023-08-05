from .bindings import _FFI, _C
from .bn import Bn, force_Bn


from builtins import int        # pylint: disable=redefined-builtin
from builtins import object     # pylint: disable=redefined-builtin
from future.utils import python_2_unicode_compatible

from copy import copy
from binascii import hexlify
from hashlib import sha512

import pytest

def _check(return_val):
        """Checks the return code of the C calls"""
        if isinstance(return_val, int) and return_val == 1:
            return
        if isinstance(return_val, bool) and return_val == True:
            return

        raise Exception("EC exception") 
        

class EcGroup(object):

    @staticmethod
    def list_curves():
        """Return a dictionary of nid -> curve names"""
        size_t = int(_C.EC_get_builtin_curves(_FFI.NULL, 0))
        _check( 0 < size_t ) 
        names = _FFI.new("EC_builtin_curve[]", size_t)
        _C.EC_get_builtin_curves(names, size_t)

        all_curves = []
        for i in range(size_t):
            all_curves +=  [(int(names[i].nid), str(_FFI.string(names[i].comment)))]
        return dict(all_curves)
    
    def __init__(self, nid=713, optimize_mult=True):
        """Build an EC group from the Open SSL nid. By default use NIST p224, which in OpenSSL 64bit supports constant-time operations."""
        self.ecg = _C.EC_GROUP_new_by_curve_name(nid)
        if optimize_mult:
            _check( _C.EC_GROUP_precompute_mult(self.ecg, _FFI.NULL) )

    def parameters(self):
        """Returns a dictionary with the parameters (a,b and p) of the curve."""
        p, a, b = Bn(), Bn(), Bn()
        _check( _C.EC_GROUP_get_curve_GFp(self.ecg, p.bn, a.bn, b.bn, _FFI.NULL) )
        return {"p":p, "a":a, "b":b}

    def generator(self):
        """Returns the generator of the EC group"""
        g = EcPt(self)
        internal_g = _C.EC_GROUP_get0_generator(self.ecg)
        _check( _C.EC_POINT_copy(g.pt, internal_g) )
        return g

    def infinite(self):
        """Returns a point at infinity"""
        zero = EcPt(self)
        _check( _C.EC_POINT_set_to_infinity(self.ecg, zero.pt) )
        return zero

    def order(self):
        """Returns the order of the group as a Big Number"""
        o = Bn()
        _check( _C.EC_GROUP_get_order(self.ecg, o.bn, _FFI.NULL) )
        return o

    def __eq__(self, other):
        res = _C.EC_GROUP_cmp(self.ecg, other.ecg, _FFI.NULL)
        return res == 0

    def __ne__(self, other):
        return not self.__eq__(other)

    def nid(self):
        """Returns the Open SSL group ID"""
        return int(_C.EC_GROUP_get_curve_name(self.ecg))

    def __del__(self):
        _C.EC_GROUP_free(self.ecg)

    def check_point(self, pt):
        """Ensures the point is on the curve"""
        res = int(_C.EC_POINT_is_on_curve(self.ecg, pt.pt, _FFI.NULL))
        return res == 1

    def hash_to_point(self, hinput):
        """Hash a string into an EC Point."""
        p = self.parameters()["p"]
        
        pt = EcPt(self)
        xhash = hinput
        y = 1    
        ret = 0

        while ret == 0:
            xhash = sha512(xhash).digest()
            x = Bn.from_binary(xhash) % p
            ret = _C.EC_POINT_set_compressed_coordinates_GFp(self.ecg, pt.pt, x.bn, y, _FFI.NULL)

        assert self.check_point(pt)
        _check( ret )
        return pt

@python_2_unicode_compatible
class EcPt(object):
    """An EC point, supporting point addition, doubling 
    and multiplication with a scalar
    """
    __slots__ = ["pt", "group"]
    
    @staticmethod
    def from_binary(sbin, group):
        "Create a point from a string binary sequence"
        new_pt = EcPt(group)
        _check( _C.EC_POINT_oct2point(group.ecg, new_pt.pt, sbin, len(sbin), _FFI.NULL) )
        return new_pt

    def __init__(self, group):
        self.group = group
        self.pt = _C.EC_POINT_new(group.ecg)

    def __copy__(self):
        new_point = EcPt(self.group)
        _check( _C.EC_POINT_copy(new_point.pt, self.pt) )
        return new_point

    def pt_add(self, other):
        """Adds two points together. Synonym with self + other."""
        return self.__add__(other)

    def __add__(self, other):
        _check( type(other) == EcPt )
        _check( other.group == self.group )
        result = EcPt(self.group)
        _check( _C.EC_POINT_add(self.group.ecg, result.pt, self.pt, other.pt, _FFI.NULL) )
        return result

    def pt_double(self):
        """Doubles the point. equivalent to "self + self"."""
        result = EcPt(self.group)
        _check( _C.EC_POINT_dbl(self.group.ecg, result.pt, self.pt, _FFI.NULL) )
        return result

    def pt_neg(self):
        """Returns the negative of the point. Synonym with -self"""
        return self.__neg__()

    def __neg__(self):
        result = copy(self)
        _check( _C.EC_POINT_invert(self.group.ecg, result.pt, _FFI.NULL) )
        return result

    def pt_mul(self, scalar):
        """Returns the product of the point with a scalar (not communtative). Synonym with scalar * self."""
        return self.__rmul__(scalar)

    @force_Bn(1)
    def __rmul__(self, other):
        result = EcPt(self.group)
        _check( _C.EC_POINT_mul(self.group.ecg, result.pt, _FFI.NULL, self.pt, other.bn, _FFI.NULL) )
        return result

    def pt_eq(self, other):
        """Returns a boolean denoting whether the points are equal. Synonym with self == other."""
        return self.__eq__(other)

    def __eq__(self, other):
        _check( type(other) == EcPt )
        _check( other.group == self.group )
        r = int(_C.EC_POINT_cmp(self.group.ecg, self.pt, other.pt, _FFI.NULL))
        return r == 0

    def __ne__(self, other):
        return not self.__eq__(other)

    def __del__(self):
        _C.EC_POINT_clear_free(self.pt)

    def __hash__(self):
        return self.export().__hash__()

    def export(self):
        """Returns a string binary representation of the point"""
        size = _C.EC_POINT_point2oct(self.group.ecg, self.pt, _C.POINT_CONVERSION_COMPRESSED, 
                             _FFI.NULL, 0, _FFI.NULL)
        buf = _FFI.new("unsigned char[]", size)
        _C.EC_POINT_point2oct(self.group.ecg, self.pt, _C.POINT_CONVERSION_COMPRESSED,
                             buf, size, _FFI.NULL)
        output = bytes(_FFI.buffer(buf)[:])
        return output

    def is_infinite(self):
        """Returns True if this point is at infinity, otherwise False."""
        return self == self.group.infinite() 

    def get_affine(self):
        """Return the affine coordinates (x,y) of this EC Point."""
        if self == self.group.infinite():
            raise Exception("EC Infinity has no affine coordinates.")
        x = Bn()
        y = Bn()
        _check( _C.EC_POINT_get_affine_coordinates_GFp(self.group.ecg,
self.pt, x.bn, y.bn, _FFI.NULL))
        return (x,y)

    def __str__(self):
        return hexlify(self.export()).decode("utf8")

## Ignore some lint warning in tests
# pylint: disable=unused-variable

def test_ec_list_group():
    c = EcGroup.list_curves()
    assert len(c) > 0 
    assert 713 in c
    assert 410 in c

def test_ec_build_group():
    G = EcGroup(409)
    assert G.nid() == 409
    H = EcGroup(410)
    assert G.check_point(G.generator())
    assert not H.check_point(G.generator())
    order = G.order()
    assert str(order) == "6277101735386680763835789423176059013767194773182842284081"
    assert G == G
    assert not (G == H)
    assert G != H
    assert not (G != G)
    assert "a" in G.parameters()

    h1 = G.hash_to_point(b"Hello2")

def test_ec_arithmetic():
    G = EcGroup(713)
    g = G.generator()
    assert g + g == g + g  
    assert g + g == g.pt_double()
    assert g + g == Bn(2) * g  
    assert g + g == 2 * g  
     
    assert g + g != g + g + g 
    assert g + (-g) == G.infinite()
    d = {}
    d[2*g] = 2
    assert d[2*g] == 2

    ## Test long names
    assert (g + g).pt_eq(g + g)  
    assert g + g == g.pt_add(g)  
    assert -g == g.pt_neg()  
    assert 10 * g == g.pt_mul(10)

    assert len(str(g)) > 0 

def test_ec_io():
    G = EcGroup(713)
    g = G.generator()

    x,y = g.get_affine()
    assert len(g.export()) == 29
    i = G.infinite()
    assert len(i.export()) == 1
    assert EcPt.from_binary(g.export(), G) == g
    assert EcPt.from_binary(i.export(), G) == i

def test_affine_inf():
    G = EcGroup(713)
    inf = G.infinite()

    with pytest.raises(Exception) as excinfo:
        inf.get_affine()
    assert 'EC Infinity' in str(excinfo.value)

    


def test_p224_const_timing():
    import time

    ## Note: NIST / SECG p224 is nid: 713/712 (p192 is nid:711)
    G = EcGroup(713)
    g = G.generator()
    order = G.order()
    h = order.random() * g

    repreats = 100
    t = []
    for x in range(0, 200, 20):
        o = Bn(2) ** x
        tests = [o.random() for _ in range(repreats)]

        t0 = time.clock()
        for y in tests:
            dud = y * h
        t += [time.clock() - t0]
        print(x, t[-1] / repreats)
    assert abs(t[0] - t[-1]) < 1.0 / 100

# pylint: enable=unused-variable