"""Test package."""

# Package to test
from mutabletuple import mutabletuple, MtFactory, MtNoDefault

# Native import
import unittest
import pickle
from collections import OrderedDict


class TestMutableTuple(unittest.TestCase):

    def test_factory_repr(self):
        Point  = mutabletuple('Point', [('x', 0), ('y', 0)])
        self.assertEqual(str(MtFactory(Point, 2)), "{'x': 2, 'y': 0}")


    def test_factory_with_args(self):
        Point  = mutabletuple('Point', [('x', 0), ('y', 0)])
        Vector = mutabletuple('Vector', [('p1', MtFactory(Point, 2)), ('p2', MtFactory(Point, 4, 8))])

        v1     = Vector()
        self.assertEqual(v1, Vector(Point(2, 0), Point(4, 8)))
        self.assertEqual(str(v1), "{'p1': {'x': 2, 'y': 0}, 'p2': {'x': 4, 'y': 8}}")


    def test_factory_and_nested(self):
        Point  = mutabletuple('Point', [('x', 0), ('y', 0)])
        Vector = mutabletuple('Vector', [('p1', MtFactory(Point)), ('p2', MtFactory(Point))])
        Shape  = mutabletuple('Shape', [('v1', MtFactory(Vector)), ('v2', MtFactory(Vector))])
        p1     = Point()
        p2     = Point()
        v1     = Vector(Point(0, 0), Point(0, 0))
        v2     = Vector()
        s1     = Shape(Vector(Point(0, 0), Point(0, 0)), Vector())
        s2     = Shape()

        # Test that modifying p2 do not modify p1
        p2.x = 20
        self.assertNotEqual(id(p1), id(p2))
        self.assertEqual(p1, Point())
        self.assertEqual(str(p1), "{'x': 0, 'y': 0}")

        # Test that every new object is unique
        self.assertNotEqual(id(v1), id(v2))
        self.assertNotEqual(id(v1.p1), id(v2.p1))
        self.assertNotEqual(id(v1.p2), id(v2.p2))
        self.assertNotEqual(id(v1.p1), id(v1.p2))
        self.assertNotEqual(id(v2.p1), id(v2.p2))

        # Test that modifying v2 do not modify v1
        v2.p1.x = 20
        self.assertEqual(v1, Vector())
        self.assertEqual(str(v1), "{'p1': {'x': 0, 'y': 0}, 'p2': {'x': 0, 'y': 0}}")


        # Test that every new object is unique
        self.assertNotEqual(id(s1), id(s2))
        self.assertNotEqual(id(s1.v1), id(s2.v1))
        self.assertNotEqual(id(s1.v2), id(s2.v2))
        self.assertNotEqual(id(s1.v1), id(s1.v2))
        self.assertNotEqual(id(s2.v1), id(s2.v2))

        # Test that modifying s2 do not modify s1
        s2.v1.p1.x = 20
        self.assertEqual(s1, Shape())
        self.assertEqual(str(s1), "{'v1': {'p1': {'x': 0, 'y': 0}, 'p2': {'x': 0, 'y': 0}}, 'v2': {'p1': {'x': 0, 'y': 0}, 'p2': {'x': 0, 'y': 0}}}")


    def test_nested(self):
        Point  = mutabletuple('Point', [('x', 0), ('y', 0)])
        Vector = mutabletuple('Vector', [('p1', MtFactory(Point)), ('p2', MtFactory(Point))])
        Shape  = mutabletuple('Shape', [('v1', MtFactory(Vector)), ('v2', MtFactory(Vector))])

        s = Shape()
        self.assertEqual(str(s), "{'v1': {'p1': {'x': 0, 'y': 0}, 'p2': {'x': 0, 'y': 0}}, 'v2': {'p1': {'x': 0, 'y': 0}, 'p2': {'x': 0, 'y': 0}}}")
        self.assertEqual(s._asdict(), {'v1': {'p1': {'x': 0, 'y': 0}, 'p2': {'x': 0, 'y': 0}}, 'v2': {'p1': {'x': 0, 'y': 0}, 'p2': {'x': 0, 'y': 0}}})

        s.v1.p2.y = 30
        self.assertEqual(str(s), "{'v1': {'p1': {'x': 0, 'y': 0}, 'p2': {'x': 0, 'y': 30}}, 'v2': {'p1': {'x': 0, 'y': 0}, 'p2': {'x': 0, 'y': 0}}}")
        self.assertEqual(s._asdict(), {'v1': {'p1': {'x': 0, 'y': 0}, 'p2': {'x': 0, 'y': 30}}, 'v2': {'p1': {'x': 0, 'y': 0}, 'p2': {'x': 0, 'y': 0}}})


    def test_merge(self):
        Point  = mutabletuple('Point', [('x', 0), ('y', 0)])
        Vector = mutabletuple('Vector', [('p1', MtFactory(Point)), ('p2', MtFactory(Point))])
        Shape  = mutabletuple('Shape', [('v1', MtFactory(Vector)), ('v2', MtFactory(Vector))])

        s = Shape()
        d = {'v1': {'p1': {'x': 20}, 'p2': Point(30, 40)}}
        s.merge(d)
        self.assertEqual(str(s), "{'v1': {'p1': {'x': 20, 'y': 0}, 'p2': {'x': 30, 'y': 40}}, 'v2': {'p1': {'x': 0, 'y': 0}, 'p2': {'x': 0, 'y': 0}}}")
        self.assertEqual(s._asdict(), {'v1': {'p1': {'x': 20, 'y': 0}, 'p2': {'x': 30, 'y': 40}}, 'v2': {'p1': {'x': 0, 'y': 0}, 'p2': {'x': 0, 'y': 0}}})

        s = Shape()
        d = OrderedDict([('v1', OrderedDict([('p1', OrderedDict([('x', 20)]))]))])
        s.merge(d)
        self.assertEqual(str(s), "{'v1': {'p1': {'x': 20, 'y': 0}, 'p2': {'x': 0, 'y': 0}}, 'v2': {'p1': {'x': 0, 'y': 0}, 'p2': {'x': 0, 'y': 0}}}")
        self.assertEqual(s._asdict(), {'v1': {'p1': {'x': 20, 'y': 0}, 'p2': {'x': 0, 'y': 0}}, 'v2': {'p1': {'x': 0, 'y': 0}, 'p2': {'x': 0, 'y': 0}}})


    def test_simple(self):
        # Declare members as string
        Point = mutabletuple('Point', 'x y')
        p = Point(10, 20)
        self.assertEqual(str(p), "{'x': 10, 'y': 20}")

        # Declare members as list
        Point = mutabletuple('Point', ['x', 'y'])
        p = Point(10, 20)
        self.assertEqual(str(p), "{'x': 10, 'y': 20}")

        # Declare members as list with default
        Point = mutabletuple('Point', [('x', 10), ('y', 20)])
        p = Point()
        self.assertEqual(str(p), "{'x': 10, 'y': 20}")

        self.assertEqual(Point(10, 11), Point(10, 11))
        self.assertNotEqual(Point(10, 11), Point(10, 12))


    def test_dict(self):
        Point  = mutabletuple('Point', [('x', 0), ('y', 0)])
        Vector = mutabletuple('Vector', [('p1', MtFactory(Point)), ('p2', MtFactory(Point))])
        Shape  = mutabletuple('Shape', [('v1', MtFactory(Vector)), ('v2', MtFactory(Vector))])

        p = Point(10, 20)
        self.assertEqual(p._asdict(), {'x': 10, 'y': 20})

        s1 = Shape(Vector(Point(3, 4)))
        s2 = Shape()
        s2.merge(s1._asdict())
        self.assertEqual(s1, s2)


    def test_ordered_dict_simple(self):
        Point = mutabletuple('Point', ['x', 'y'])
        p = Point(10, 20)
        self.assertEqual(p.orderedDict(), OrderedDict([('x', 10), ('y', 20)]))


    def test_default(self):
        Point = mutabletuple('Point', 'x y z', default=100)
        self.assertEqual(Point(), Point(100, 100, 100))
        self.assertEqual(Point(10), Point(10, 100, 100))
        self.assertEqual(Point(10, 20), Point(10, 20, 100))
        self.assertEqual(Point(10, 20, 30), Point(10, 20, 30))
        self.assertEqual(Point()._asdict(), {'x': 100, 'y': 100, 'z': 100})


    def test_unknown_key(self):
        Point = mutabletuple('Point', 'x y')
        p = Point(10, 20)
        self.assertRaises(AttributeError, getattr, p, 'z')
        self.assertRaises(AttributeError, setattr, p, 'z', 30)


    def test_unique_identifier(self):
        Point = mutabletuple('Point', 'x y')
        p = Point(10, 20)
        self.assertTrue(hasattr(p, 'MutableTupleUniqueIdentifier'))


    def test_writable(self):
        Point = mutabletuple('Point', ['x', ('y', 10), ('z', 20)], 100)
        p = Point(0)
        self.assertEqual((p.x, p.y, p.z), (0, 10, 20))
        p.x = -1
        self.assertEqual((p.x, p.y, p.z), (-1, 10, 20))
        p.y = -1
        self.assertEqual((p.x, p.y, p.z), (-1, -1, 20))
        p.z = None
        self.assertEqual((p.x, p.y, p.z), (-1, -1, None))


    def test_MtNoDefault(self):
        # MtNoDefault is only really useful with we're using a mapping
        #  plus a default value. it's the only way to specify that
        #  some of the fields use the default.
        Point = mutabletuple('Point', {'x':0, 'y':MtNoDefault}, default=5)
        p = Point()
        self.assertEqual(p.x, 0)
        self.assertEqual(p.y, 5)


    def test_iteration(self):
        Point = mutabletuple('Point', ['x', ('y', 10), ('z', 20)], [1, 2, 3])
        p = Point()
        self.assertEqual(len(p), 3)

        self.assertEqual(list(iter(p)), [[1, 2, 3], 10, 20])

        for expected, found in zip([[1, 2, 3], 10, 20], p):
            self.assertEqual(expected, found)

        for expected, found in zip((('x', [1, 2, 3]), ('y', 10), ('z', 20)), p.iteritems()):
            self.assertEqual(expected, found)


    def test_getitem(self):
        Point = mutabletuple('Point', 'a b')
        p = Point(1, 2)
        self.assertEqual((p[0], p[1]), (1, 2))
        self.assertEqual(list(p), [1, 2])
        self.assertRaises(IndexError, p.__getitem__, 2)


    def test_setitem(self):
        Point = mutabletuple('Point', 'a b')
        p = Point(1, 2)
        p[0] = 10
        self.assertEqual(list(p), [10, 2])
        p[1] = 20
        self.assertEqual(list(p), [10, 20])
        self.assertRaises(IndexError, p.__setitem__, 2, 3)


# *****************************************************************************
# Pickle test
# *****************************************************************************
# test both pickle and cPickle in 2.x, but just pickle in 3.x
try:
    import cPickle
    pickle_modules = (pickle, cPickle)
except ImportError:
    pickle_modules = (pickle,)

# types used for pickle tests
TestMT0 = mutabletuple('TestMT0', '')
TestMT1 = mutabletuple('TestMT1', 'x y z', default=4)
TestMT2 = mutabletuple('TestMT2', [('mt1', MtFactory(TestMT1, 50, 60, 70)), ('a', 1), ('b', [2, 3, 4])])

# Warning Pickling does not work for mutabletuple that have no default values.
class TestMutableTuplePickle(unittest.TestCase):
    def test_pickle(self):
        for p in (TestMT0(), TestMT1(x=10, y=20, z=30), TestMT2()):
            for module in pickle_modules:
                for protocol in range(-1, module.HIGHEST_PROTOCOL + 1):
                    q = module.loads(module.dumps(p, protocol))
                    self.assertEqual(p, q)
                    self.assertEqual(p._fields, q._fields)
                    self.assertNotIn(b'OrderedDict', module.dumps(p, protocol))
