# -*- coding: utf-8 -*-
from . import BW2DataTest
from ..data_store import DataStore
from ..errors import UnsafeData, InvalidPackage
from ..io import BW2Package
from ..method import Method
from ..serialization import SerializedDict
import copy
import fractions


class MockMetadata(SerializedDict):
    filename = "mock-meta.json"

mocks = MockMetadata()


class MockDS(DataStore):
    """Mock DataStore for testing"""
    metadata = mocks
    validator = lambda x, y: True
    dtype_fields = []

    def process_data(self, row):
        return (), 0


class BW2PackageTest(BW2DataTest):
    def extra_setup(self):
        mocks.__init__()

    def test_class_metadata(self):
        class_metadata = {
            'module': 'bw2data.tests.packaging',
            'name': 'MockDS',
        }
        self.assertEqual(
            BW2Package._get_class_metadata(MockDS('foo')),
            class_metadata
        )

    def test_validation(self):
        good_dict = {
            'metadata': {'foo': 'bar'},
            'name': 'Johnny',
            'class': {
                'module': 'some',
                'name': 'thing'
            },
            'data': {}
        }
        self.assertTrue(BW2Package._is_valid_package(good_dict))
        d = copy.deepcopy(good_dict)
        d['name'] = ()
        self.assertTrue(BW2Package._is_valid_package(d))
        for key in ['metadata', 'name', 'data']:
            d = copy.deepcopy(good_dict)
            del d[key]
            self.assertFalse(BW2Package._is_valid_package(d))

    def test_whitelist(self):
        good_class_metadata = {
            'module': 'bw2data.tests.packaging',
            'name': 'MockDS',
        }
        bad_class_metadata = {
            'module': 'some.package',
            'name': 'Foo',
        }
        self.assertTrue(BW2Package._is_whitelisted(good_class_metadata))
        self.assertFalse(BW2Package._is_whitelisted(bad_class_metadata))

    def test_create_class_whitelist(self):
        bad_class_metadata = {
            'module': 'some.package',
            'name': 'Foo',
        }
        with self.assertRaises(UnsafeData):
            BW2Package._create_class(bad_class_metadata)
        with self.assertRaises(ImportError):
            BW2Package._create_class(bad_class_metadata, False)

    def test_create_class(self):
        class_metadata = {
            'module': 'collections',
            'name': 'Counter'
        }
        cls = BW2Package._create_class(class_metadata, False)
        import collections
        self.assertEqual(cls, collections.Counter)
        class_metadata = {
            'module': 'bw2data.method',
            'name': 'Method'
        }
        cls = BW2Package._create_class(class_metadata, False)
        self.assertEqual(cls, Method)

    def test_load_obj(self):
        test_data = {
            'metadata': {'foo': 'bar'},
            'name': ['Johnny', 'B', 'Good'],
            'class': {
                'module': 'fractions',
                'name': 'Fraction'
            },
            'data': {}
        }
        after = BW2Package._load_obj(copy.deepcopy(test_data), False)
        for key in test_data:
            self.assertTrue(key in after)
        with self.assertRaises(InvalidPackage):
            BW2Package._load_obj({})
        self.assertEqual(after['class'], fractions.Fraction)

    def test_create_obj(self):
        mock_data = {
            'class': {'module': 'bw2data.tests.packaging', 'name': 'MockDS'},
            'metadata': {'circle': 'square'},
            'data': [],
            'name': 'Wilhelm'
        }
        data = BW2Package._load_obj(mock_data)
        obj = BW2Package._create_obj(data)
        self.assertTrue(isinstance(obj, MockDS))
        self.assertTrue("Wilhelm" in mocks)
        self.assertEqual(mocks['Wilhelm'], {'circle': 'square'})
        self.assertEqual(MockDS("Wilhelm").load(), [])

    def test_roundtrip_obj(self):
        obj = MockDS("Slick Al")
        obj.register()
        obj.write(["a boring string", {'foo': 'bar'}, (1,2,3)])
        fp = BW2Package.export_obj(obj)
        obj.deregister()
        del obj
        self.assertFalse('Slick Al' in mocks)
        obj = BW2Package.import_file(fp)
        self.assertTrue('Slick Al' in mocks)
        self.assertTrue(isinstance(obj, MockDS))
        self.assertEqual(obj.load(), ["a boring string", {'foo': 'bar'}, (1,2,3)])

    def test_roundtrip_objs(self):
        pass
