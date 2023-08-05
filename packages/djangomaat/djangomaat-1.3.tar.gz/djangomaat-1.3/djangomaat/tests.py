from django.utils import unittest
from django.db import models
try:
    from django.contrib.contenttypes.fields import ReverseGenericRelatedObjectsDescriptor
except ImportError:
    # Django < 1.7
    from django.contrib.contenttypes.generic import ReverseGenericRelatedObjectsDescriptor

from djangomaat.register import maat
from djangomaat.handlers import MaatHandler
from djangomaat.exceptions import *

class TestMaatHandler(MaatHandler):

    def get_pk_list_for_typology1(self):
        return TestModel.objects.order_by('name').values_list('pk', flat=True).iterator()

    def get_pk_list_for_typology2(self):
        return []


class TestModel(models.Model):
    name = models.CharField(max_length=8)

    def __unicode__(self):
        return unicode(self.name)


class TestManager(models.Manager):
    pass


class MockLogger(object):
    def write(self, something):
        pass

class ClientTest(unittest.TestCase):

    def setUp(self):
        self.h = TestMaatHandler(TestModel)

    def tearDown(self):
        self.h = None

    def test_default_model_manager(self):
        self.assertEqual(self.h._get_model_manager().__class__, models.Manager)

    def test_custom_model_manager(self):
        tmp = TestModel.objects
        TestModel.objects = TestManager
        self.assertEqual(self.h._get_model_manager().__class__, models.Manager)
        TestModel.objects = tmp

    def test_non_existent_model_manager(self):
        tmp = self.h.manager
        self.h.manager = 'TestManager'
        self.assertRaises(ManagerDoesNotExist, self.h._get_model_manager)
        self.h.manager = tmp

    def test_validate_valid_typology1(self):
        self.assertIsNone(self.h._validate_typology('typology1'))

    def test_validate_valid_typology2(self):
        self.assertIsNone(self.h._validate_typology('typology2'))

    def test_validate_invalid_typology(self):
        self.assertRaises(TypologyNotImplemented, self.h._validate_typology, 'x')

    def test_register_already_registered_model(self):
        maat.register(TestModel, TestMaatHandler)
        self.assertRaises(ModelAlreadyRegistered, maat.register, TestModel, TestMaatHandler)
        maat.unregister(TestModel)

    def test_register_monkey_patching(self):
        maat.register(TestModel, TestMaatHandler)
        self.assertTrue(hasattr(TestModel, 'maat'))
        self.assertEqual(TestModel.maat.__class__, TestMaatHandler)
        self.assertTrue(hasattr(TestModel, 'maat_ranking'))
        self.assertEqual(TestModel.maat_ranking.__class__, ReverseGenericRelatedObjectsDescriptor)
        maat.unregister(TestModel)

    def test_register_handlers_list(self):
        maat.register(TestModel, TestMaatHandler)
        self.assertEqual(maat.get_registered_handlers()[0].__class__, TestMaatHandler)
        maat.unregister(TestModel)

    def test_retrieve_implemented_empty_typology(self):
        maat.register(TestModel, TestMaatHandler)
        self.assertEqual(list(TestModel.maat.ordered_by('typology1')), [])
        maat.unregister(TestModel)

    def test_retrieve_not_implemente_typology(self):
        maat.register(TestModel, TestMaatHandler)
        self.assertRaises(TypologyNotImplemented, TestModel.maat.ordered_by, 'x')
        maat.unregister(TestModel)

    def test_register_handler_for_model(self):
        maat.register(TestModel, TestMaatHandler)
        self.assertEqual(maat.get_handler_for_model(TestModel).__class__, TestMaatHandler)
        maat.unregister(TestModel)

    def test_register_handler_for_unregistered_model(self):
        self.assertRaises(ModelNotRegistered, maat.get_handler_for_model, TestModel)

    def test_flush_and_retrieve(self):
        maat.register(TestModel, TestMaatHandler)
        object1 = TestModel.objects.create(name='object1')
        object2 = TestModel.objects.create(name='object2')
        object3 = TestModel.objects.create(name='object3')
        object4 = TestModel.objects.create(name='object4')
        object5 = TestModel.objects.create(name='object5')
        self.h.flush_ordered_objects()
        expected = [object1, object2, object3, object4, object5]
        self.assertEqual(list(TestModel.maat.ordered_by('typology1')), expected)
        expected.reverse()
        self.assertEqual(list(TestModel.maat.ordered_by('-typology1')), expected)
        self.assertEqual(list(TestModel.maat.ordered_by('typology2')), [])
        self.assertEqual(list(TestModel.maat.ordered_by('-typology2')), [])
        TestModel.objects.all().delete()
        maat.unregister(TestModel)

    def test_flush_and_retrieve_massive(self):
        maat.register(TestModel, TestMaatHandler)
        TestModel.objects.bulk_create((TestModel(name='object{:05d}'.format(i)) for i in range(20000)), 250)
        expected = list(TestModel.objects.all())
        self.h.flush_ordered_objects()
        self.assertEqual(list(TestModel.maat.ordered_by('typology1')), expected)
        expected.reverse()
        self.assertEqual(list(TestModel.maat.ordered_by('-typology1')), expected)
        self.assertEqual(list(TestModel.maat.ordered_by('typology2')), [])
        self.assertEqual(list(TestModel.maat.ordered_by('-typology2')), [])
        # Avoid "too many sql variables"
        for i in range(0, 21000, 100):
            TestModel.objects.filter(id__lt=i).delete()

        maat.unregister(TestModel)

    def test_simulated_flush_and_retrieve(self):
        maat.register(TestModel, TestMaatHandler)
        TestModel.objects.create(name='object1')
        TestModel.objects.create(name='object2')
        TestModel.objects.create(name='object3')
        TestModel.objects.create(name='object4')
        TestModel.objects.create(name='object5')
        self.h.flush_ordered_objects(simulate=True)
        self.assertEqual(list(TestModel.maat.ordered_by('typology1')), [])
        TestModel.objects.all().delete()
        maat.unregister(TestModel)

    def test_logged_flush_and_retrieve(self):
        maat.register(TestModel, TestMaatHandler)
        object1 = TestModel.objects.create(name='object1')
        object2 = TestModel.objects.create(name='object2')
        object3 = TestModel.objects.create(name='object3')
        object4 = TestModel.objects.create(name='object4')
        object5 = TestModel.objects.create(name='object5')
        self.h.flush_ordered_objects(logger=MockLogger())
        expected = [object1, object2, object3, object4, object5]
        self.assertEqual(list(TestModel.maat.ordered_by('typology1')), expected)
        expected.reverse()
        self.assertEqual(list(TestModel.maat.ordered_by('-typology1')), expected)
        self.assertEqual(list(TestModel.maat.ordered_by('typology2')), [])
        self.assertEqual(list(TestModel.maat.ordered_by('-typology2')), [])
        TestModel.objects.all().delete()
        maat.unregister(TestModel)

    def test_simulated_and_logged_flush_and_retrieve(self):
        maat.register(TestModel, TestMaatHandler)
        TestModel.objects.create(name='object1')
        TestModel.objects.create(name='object2')
        TestModel.objects.create(name='object3')
        TestModel.objects.create(name='object4')
        TestModel.objects.create(name='object5')
        self.h.flush_ordered_objects(logger=MockLogger(), simulate=True)
        self.assertEqual(list(TestModel.maat.ordered_by('typology1')), [])
        TestModel.objects.all().delete()
        maat.unregister(TestModel)
