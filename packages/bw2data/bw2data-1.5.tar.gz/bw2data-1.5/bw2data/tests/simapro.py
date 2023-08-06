# -*- coding: utf-8 -*-
from . import BW2DataTest
from .. import Database, databases
from ..io.import_simapro import SimaProImporter, MissingExchange, detoxify_re
from .fixtures.simapro_reference import background as background_data
import os
from stats_arrays import UndefinedUncertainty, NoUncertainty


SP_FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "simapro")


class SimaProImportTest(BW2DataTest):
    def extra_setup(self):
        # SimaPro importer always wants biosphere database
        database = Database("biosphere")
        database.register(
            format="Test data",
        )
        database.write({})

    def filepath(self, name):
        return os.path.join(SP_FIXTURES_DIR, name + '.txt')

    def test_invalid_file(self):
        sp = SimaProImporter(self.filepath("invalid"), depends=[])
        data = sp.load_file()
        with self.assertRaises(AssertionError):
            sp.verify_simapro_file(data)

    def test_overwrite(self):
        database = Database("W00t")
        database.register()
        sp = SimaProImporter(self.filepath("empty"), depends=[], overwrite=True)
        sp.importer()
        self.assertTrue("W00t" in databases)

    def test_no_overwrite(self):
        database = Database("W00t")
        database.register()
        sp = SimaProImporter(self.filepath("empty"), depends=[])
        with self.assertRaises(AssertionError):
            sp.importer()

    def test_import_one_empty_process(self):
        sp = SimaProImporter(self.filepath("empty"), depends=[])
        sp.importer()
        self.assertTrue("W00t" in databases)
        self.assertEqual(len(Database("W00t").load()), 1)

    def test_get_db_name(self):
        sp = SimaProImporter(self.filepath("empty"), depends=[])
        sp.importer()
        self.assertTrue("W00t" in databases)

    def test_set_db_name(self):
        sp = SimaProImporter(self.filepath("empty"), depends=[], name="A different one")
        sp.importer()
        self.assertTrue("A different one" in databases)
        self.assertTrue("W00t" not in databases)

    def test_default_geo(self):
        sp = SimaProImporter(self.filepath("empty"), depends=[], default_geo="Where?")
        sp.importer()
        data = Database("W00t").load().values()[0]
        self.assertEqual("Where?", data['location'])

    def test_no_multioutput(self):
        sp = SimaProImporter(self.filepath("multioutput"), depends=[])
        with self.assertRaises(AssertionError):
            sp.importer()

    def test_detoxify_re(self):
        self.assertFalse(detoxify_re.search("Cheese U"))
        self.assertFalse(detoxify_re.search("Cheese/CH"))
        self.assertTrue(detoxify_re.search("Cheese/CH U"))
        self.assertTrue(detoxify_re.search("Cheese/CH/I U"))
        self.assertTrue(detoxify_re.search("Cheese/CH/I S"))
        self.assertTrue(detoxify_re.search("Cheese/RER U"))
        self.assertTrue(detoxify_re.search("Cheese/CENTREL U"))
        self.assertTrue(detoxify_re.search("Cheese/CENTREL S"))

    def test_simapro_unit_conversion(self):
        sp = SimaProImporter(self.filepath("empty"), depends=[])
        sp.importer()
        data = Database("W00t").load().values()[0]
        self.assertEqual("unit", data['unit'])

    def test_dataset_definition(self):
        sp = SimaProImporter(self.filepath("empty"), depends=[])
        sp.importer()
        data = Database("W00t").load().values()[0]
        self.assertEqual(data, {
            "name": "Fish food",
            "unit": u"unit",
            "location": "GLO",
            "type": "process",
            "categories": ["Agricultural", "Animal production", "Animal foods"],
            "code": u'6524377b64855cc3daf13bd1bcfe0385',
            "exchanges": [{
                'amount': 1.0,
                'loc': 1.0,
                'input': ('W00t', u'6524377b64855cc3daf13bd1bcfe0385'),
                'type': 'production',
                'uncertainty type': NoUncertainty.id,
                'allocation': {'factor': 100.0, 'type': 'not defined'},
                'unit': 'unit',
                'folder': 'Agricultural\Animal production\Animal foods',
                'comment': '',
            }],
            "simapro metadata": {
                "Category type": "material",
                "Process identifier": "InsertSomethingCleverHere",
                "Type": "Unit process",
                "Process name": "bikes rule, cars drool",
            }
        })

    def test_production_exchange(self):
        sp = SimaProImporter(self.filepath("empty"), depends=[])
        sp.importer()
        data = Database("W00t").load().values()[0]
        self.assertEqual(data['exchanges'], [{
            'amount': 1.0,
            'loc': 1.0,
            'input': ('W00t', u'6524377b64855cc3daf13bd1bcfe0385'),
            'type': 'production',
            'uncertainty type': NoUncertainty.id,
            'allocation': {'factor': 100.0, 'type': 'not defined'},
            'unit': 'unit',
            'folder': 'Agricultural\Animal production\Animal foods',
            'comment': '',
        }])

    def test_simapro_metadata(self):
        sp = SimaProImporter(self.filepath("metadata"), depends=[])
        sp.importer()
        data = Database("W00t").load().values()[0]
        self.assertEqual(data['simapro metadata'], {
            "Simple": "yep!",
            "Multiline": ["This too", "works just fine"],
            "But stops": "in time"
        })

    def test_linking(self):
        # Test number of datasets
        # Test internal links
        # Test external links with and without slashes, with and without geo
        database = Database("background")
        database.register(
            format="Test data",
        )
        database.write(background_data)
        sp = SimaProImporter(self.filepath("simple"), depends=["background"])
        sp.importer()
        # data = Database("W00t").load()

    def test_missing(self):
        sp = SimaProImporter(self.filepath("missing"), depends=[])
        with self.assertRaises(MissingExchange):
            sp.importer()

    def test_unicode_strings(self):
        sp = SimaProImporter(self.filepath("empty"), depends=[], default_geo=u"Where?")
        sp.importer()
        for obj in Database("W00t").load().values():
            for key, value in obj.iteritems():
                if isinstance(key, basestring):
                    self.assertTrue(isinstance(key, unicode))
                if isinstance(value, basestring):
                    self.assertTrue(isinstance(value, unicode))

    def test_comments(self):
        self.maxDiff = None
        database = Database("background")
        database.register(
            format="Test data",
        )
        database.write(background_data)
        sp = SimaProImporter(self.filepath("comments"), depends=["background"])
        sp.importer()
        data = Database("W00t").load().values()[0]
        self.assertEqual(data['exchanges'], [{
            'amount': 2.5e-10,
            'comment': 'single line comment',
            'input': ('background', 1),
            'label': 'Materials/fuels',
            'loc': 2.5e-10,
            'location': 'CA',
            'name': 'lunch',
            'type': 'technosphere',
            'uncertainty': 'Lognormal',
            'uncertainty type': UndefinedUncertainty.id,
            'unit': u'kilogram'
        }, {
            'amount': 1.0,
            'comment': 'first line of the comment\nsecond line of the comment',
            'input': ('background', 2),
            'label': 'Materials/fuels',
            'loc': 1.0,
            'location': 'CH',
            'name': 'dinner',
            'type': 'technosphere',
            'uncertainty': 'Lognormal',
            'uncertainty type': UndefinedUncertainty.id,
            'unit': u'kilogram'
        },{
            'amount': 1.0,
            'loc': 1.0,
            'input': ('W00t', u'6524377b64855cc3daf13bd1bcfe0385'),
            'type': 'production',
            'uncertainty type': NoUncertainty.id,
            'allocation': {'factor': 100.0, 'type': 'not defined'},
            'unit': u'unit',
            'folder': 'Agricultural\Animal production\Animal foods',
            'comment': 'first line of comment\nsecond line of comment',
        }])


    # Test multiple background DBs
