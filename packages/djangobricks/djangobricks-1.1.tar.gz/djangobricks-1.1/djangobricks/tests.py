from __future__ import unicode_literals

import datetime
import os

from django import get_version
from django.db import models
from django.template import Template, Context
from django.test import SimpleTestCase
from django.test.utils import override_settings
from django.utils import unittest
from django.utils.encoding import python_2_unicode_compatible
from django.utils.six.moves import range

from .models import (
    SingleBrick,
    ListBrick,
    BaseWall,
    Criterion,
    SORTING_DESC,
    SORTING_ASC,
    BaseWallFactory,
    wall_factory,
)
from djangobricks.exceptions import TemplateNameNotFound

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

def default():
    return 1

def callback_filter_a(brick):
    return brick.item._meta.model_name == 'testmodela'

def callback_filter_b(brick):
    return brick.item._meta.model_name == 'testmodelb'

def callback_filter_always_true(brick):
    return True

class TestSingleBrick(SingleBrick):
    template_name = 'single_brick.html'


class TestListBrick(ListBrick):
    template_name = 'list_brick.html'


class TestNoTemplateSingleBrick(SingleBrick): pass


class NotABrick(object): pass


class TestBrickWall(BaseWall): pass


@python_2_unicode_compatible
class TestModelA(models.Model):
    name = models.CharField(max_length=8)
    popularity = models.PositiveIntegerField()
    pub_date = models.DateTimeField()
    is_sticky = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def callable_popularity(self):
        return self.popularity


@python_2_unicode_compatible
class TestModelB(models.Model):
    name = models.CharField(max_length=8)
    date_add = models.DateTimeField()
    popularity = models.PositiveIntegerField()
    is_sticky = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def pub_date(self):
        return self.date_add


@python_2_unicode_compatible
class TestModelC(models.Model):
    name = models.CharField(max_length=8)
    pub_date = models.DateTimeField()
    popularity = models.PositiveIntegerField()
    is_sticky = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class TestWallFactory(BaseWallFactory):
    def get_content(self):
        return (
            (TestSingleBrick, TestModelA.objects.all()),
            (TestSingleBrick, TestModelB.objects.all()),
        )


class TestWallFactoryNoCriteria(BaseWallFactory):
    def get_content(self):
        return (
            (TestSingleBrick, TestModelA.objects.all()),
            (TestSingleBrick, TestModelB.objects.all()),
        )


class TestWrongContentWallFactory(BaseWallFactory):
    def get_content(self):
        return (
            (NotABrick, TestModelA.objects.all()),
        )


@override_settings(TEMPLATE_DIRS=['%s/../tests/templates' % CURRENT_DIR])
class BrickTest(SimpleTestCase):

    def setUp(self):
        self.bricks = []

    def tearDown(self):
        TestModelA.objects.all().delete()
        TestModelB.objects.all().delete()
        TestModelC.objects.all().delete()
        self.bricks = []

    def _create_model_a_objects_and_bricks(self):
        objectA1 = TestModelA.objects.create(name='objectA1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        objectA2 = TestModelA.objects.create(name='objectA2', popularity=4,
            pub_date=datetime.datetime(2011, 1, 1, 12, 0), is_sticky=False)
        objectA3 = TestModelA.objects.create(name='objectA3', popularity=3,
            pub_date=datetime.datetime(2012, 1, 1, 12, 0), is_sticky=True)
        objectA4 = TestModelA.objects.create(name='objectA4', popularity=2,
            pub_date=datetime.datetime(2013, 1, 1, 12, 0), is_sticky=False)

        self.brickA1 = SingleBrick(objectA1)
        self.brickA2 = SingleBrick(objectA2)
        self.brickA3 = SingleBrick(objectA3)
        self.brickA4 = SingleBrick(objectA4)
        for i in range(1, 5):
            self.bricks.append(getattr(self, 'brickA%s' % i))

    def _create_model_b_objects_and_bricks(self):
        objectB1 = TestModelB.objects.create(name='objectB1', popularity=10,
            date_add=datetime.datetime(2006, 1, 1, 12, 0), is_sticky=False)
        objectB2 = TestModelB.objects.create(name='objectB2', popularity=9,
            date_add=datetime.datetime(2007, 1, 1, 12, 0), is_sticky=False)
        objectB3 = TestModelB.objects.create(name='objectB3', popularity=8,
            date_add=datetime.datetime(2008, 1, 1, 12, 0), is_sticky=True)
        objectB4 = TestModelB.objects.create(name='objectB4', popularity=7,
            date_add=datetime.datetime(2009, 1, 1, 12, 0), is_sticky=False)

        self.brickB1 = SingleBrick(objectB1)
        self.brickB2 = SingleBrick(objectB2)
        self.brickB3 = SingleBrick(objectB3)
        self.brickB4 = SingleBrick(objectB4)
        for i in range(1, 5):
            self.bricks.append(getattr(self, 'brickB%s' % i))

    def _create_model_c_objects_and_bricks(self):
        objectC1 = TestModelC.objects.create(name='objectC1', popularity=20,
            pub_date=datetime.datetime(2002, 1, 1, 12, 0), is_sticky=False)
        objectC2 = TestModelC.objects.create(name='objectC2', popularity=19,
            pub_date=datetime.datetime(2003, 1, 1, 12, 0), is_sticky=False)
        objectC3 = TestModelC.objects.create(name='objectC3', popularity=18,
            pub_date=datetime.datetime(2004, 1, 1, 12, 0), is_sticky=True)
        objectC4 = TestModelC.objects.create(name='objectC4', popularity=17,
            pub_date=datetime.datetime(2005, 1, 1, 12, 0), is_sticky=False)

        self.brickC1 = ListBrick([objectC1, objectC2])
        self.brickC2 = ListBrick([objectC3, objectC4])
        for i in range(1, 3):
            self.bricks.append(getattr(self, 'brickC%s' % i))

    # Slicing, iteration, length

    def test_slicing(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks)
        self.assertEqual(wall[0], self.brickA1)
        self.assertEqual(wall[:1], [self.brickA1])
        self.assertEqual(wall[1:3], [self.brickA2, self.brickA3])

    def test_iteration(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks)
        for i, brick in enumerate(wall):
            i += 1
            self.assertEqual(brick, getattr(self, 'brickA%s' % i))

    def test_length(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks)
        self.assertEqual(len(wall), 4)

    # Instantiation

    def test_single_brick_init(self):
        objectA1 = TestModelA.objects.create(name='objectA1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        objectA2 = TestModelA.objects.create(name='objectA2', popularity=4,
            pub_date=datetime.datetime(2011, 1, 1, 12, 0), is_sticky=False)
        objectA3 = TestModelA.objects.create(name='objectA3', popularity=3,
            pub_date=datetime.datetime(2012, 1, 1, 12, 0), is_sticky=True)
        objectA4 = TestModelA.objects.create(name='objectA4', popularity=2,
            pub_date=datetime.datetime(2013, 1, 1, 12, 0), is_sticky=False)

        bricks = SingleBrick.get_bricks_for_queryset(TestModelA.objects.all())
        wall = TestBrickWall(bricks)
        self.assertEqual(wall[0].item, objectA1)
        self.assertEqual(wall[1].item, objectA2)
        self.assertEqual(wall[2].item, objectA3)
        self.assertEqual(wall[3].item, objectA4)

    def test_list_brick_init(self):
        objectA1 = TestModelA.objects.create(name='objectA1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        objectA2 = TestModelA.objects.create(name='objectA2', popularity=4,
            pub_date=datetime.datetime(2011, 1, 1, 12, 0), is_sticky=False)
        objectA3 = TestModelA.objects.create(name='objectA3', popularity=3,
            pub_date=datetime.datetime(2012, 1, 1, 12, 0), is_sticky=True)
        objectA4 = TestModelA.objects.create(name='objectA4', popularity=2,
            pub_date=datetime.datetime(2013, 1, 1, 12, 0), is_sticky=False)

        bricks = ListBrick.get_bricks_for_queryset(TestModelA.objects.all())
        wall = TestBrickWall(bricks)
        self.assertEqual(wall[0].items, [objectA1, objectA2, objectA3, objectA4])

    # Missing criterion attribute

    def test_missing_criterion_attribute(self):
        objectA1 = TestModelA.objects.create(name='objectA1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        criterion = Criterion('i_dont_exist')
        self.assertIsNone(criterion.get_value_for_item(objectA1))

    # Callable criterion

    def test_callable_criterion(self):
        objectA1 = TestModelA.objects.create(name='objectA1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        criterion = Criterion('callable_popularity')
        self.assertEqual(criterion.get_value_for_item(objectA1), 5)

    def test_callable_criterion_in_wall(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('callable_popularity'), SORTING_DESC),
        ))
        expected = [self.brickA1, self.brickA2, self.brickA3, self.brickA4]
        self.assertEqual(list(wall), expected)

    # Callable default criterion

    def test_callable_default_criterion(self):
        objectA1 = TestModelA.objects.create(name='objectA1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        criterion = Criterion('i_dont_exist', default=default)
        self.assertEqual(criterion.get_value_for_item(objectA1), 1)

    def test_callable_default_criterion_in_wall(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('i_dont_exist', default=default), SORTING_DESC),
        ))
        expected = [self.brickA1, self.brickA2, self.brickA3, self.brickA4]
        self.assertEqual(list(wall), expected)

    # Callback criterion

    def test_callback_criterion(self):
        objectA1 = TestModelA.objects.create(name='objectA1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        objectA2 = TestModelA.objects.create(name='objectA2', popularity=4,
            pub_date=datetime.datetime(2011, 1, 1, 12, 0), is_sticky=False)
        objectA3 = TestModelA.objects.create(name='objectA3', popularity=3,
            pub_date=datetime.datetime(2012, 1, 1, 12, 0), is_sticky=True)
        objectA4 = TestModelA.objects.create(name='objectA4', popularity=2,
            pub_date=datetime.datetime(2013, 1, 1, 12, 0), is_sticky=False)
        item_list = [objectA1, objectA2, objectA3, objectA4]
        criterion = Criterion('popularity', max)
        self.assertEqual(criterion.get_value_for_list(item_list), 5)

    def test_custom_callback_criterion(self):
        objectA1 = TestModelA.objects.create(name='objectA1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        objectA2 = TestModelA.objects.create(name='objectA2', popularity=4,
            pub_date=datetime.datetime(2011, 1, 1, 12, 0), is_sticky=False)
        objectA3 = TestModelA.objects.create(name='objectA3', popularity=3,
            pub_date=datetime.datetime(2012, 1, 1, 12, 0), is_sticky=True)
        objectA4 = TestModelA.objects.create(name='objectA4', popularity=4,
            pub_date=datetime.datetime(2013, 1, 1, 12, 0), is_sticky=False)
        item_list = [objectA1, objectA2, objectA3, objectA4]
        criterion = Criterion('popularity', lambda x:sum(x)/len(x))
        self.assertEqual(criterion.get_value_for_list(item_list), 4)

    def test_callback_criterion_in_wall(self):
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity', callback=min), SORTING_ASC),
        ))
        expected = [self.brickC2, self.brickC1]
        self.assertEqual(list(wall), expected)

    # Callback default criterion

    def test_callback_default_criterion(self):
        objectA1 = TestModelA.objects.create(name='objectA1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        objectA2 = TestModelA.objects.create(name='objectA2', popularity=4,
            pub_date=datetime.datetime(2011, 1, 1, 12, 0), is_sticky=False)
        objectA3 = TestModelA.objects.create(name='objectA3', popularity=3,
            pub_date=datetime.datetime(2012, 1, 1, 12, 0), is_sticky=True)
        objectA4 = TestModelA.objects.create(name='objectA4', popularity=2,
            pub_date=datetime.datetime(2013, 1, 1, 12, 0), is_sticky=False)
        item_list = [objectA1, objectA2, objectA3, objectA4]
        criterion = Criterion('i_dont_exist', max, default=10)
        self.assertEqual(criterion.get_value_for_list(item_list), 10)

    def test_callback_default_empty_list_criterion(self):
        criterion = Criterion('_', max, default=10)
        self.assertEqual(criterion.get_value_for_list([]), 10)

    # Callback callable default criterion

    def test_callback_callable_default_criterion(self):
        objectA1 = TestModelA.objects.create(name='objectA1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        objectA2 = TestModelA.objects.create(name='objectA2', popularity=4,
            pub_date=datetime.datetime(2011, 1, 1, 12, 0), is_sticky=False)
        objectA3 = TestModelA.objects.create(name='objectA3', popularity=3,
            pub_date=datetime.datetime(2012, 1, 1, 12, 0), is_sticky=True)
        objectA4 = TestModelA.objects.create(name='objectA4', popularity=2,
            pub_date=datetime.datetime(2013, 1, 1, 12, 0), is_sticky=False)
        item_list = [objectA1, objectA2, objectA3, objectA4]
        criterion = Criterion('i_dont_exist', max, default=default)
        self.assertEqual(criterion.get_value_for_list(item_list), 1)

    def test_callback_callable_default_empty_list_criterion(self):
        criterion = Criterion('_', max, default=default)
        self.assertEqual(criterion.get_value_for_list([]), 1)

    # Wrong call

    def test_callback_value_error_criterion(self):
        criterion = Criterion('_')
        with self.assertRaises(ValueError):
            criterion.get_value_for_list('im_wrong')

    # Single keys - Single bricks- Single models

    def test_single_key_desc_sorting_single_bricks_single_models(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity'), SORTING_DESC),
        ))
        expected = [self.brickA1, self.brickA2, self.brickA3, self.brickA4]
        self.assertEqual(list(wall), expected)

    def test_single_key_asc_sorting_single_bricks_single_models(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity'), SORTING_ASC),
        ))
        expected = [self.brickA4, self.brickA3, self.brickA2, self.brickA1]
        self.assertEqual(list(wall), expected)

    # Multi keys - Single bricks - Single Models

    def test_multi_key_1_sorting_single_bricks_single_models(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('is_sticky'), SORTING_DESC),
            (Criterion('popularity'), SORTING_DESC),
        ))
        expected = [self.brickA3, self.brickA1, self.brickA2, self.brickA4]
        self.assertEqual(list(wall), expected)

    def test_multi_key_2_sorting_single_bricks_single_models(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('is_sticky'), SORTING_ASC),
            (Criterion('popularity'), SORTING_DESC),
        ))
        expected = [self.brickA1, self.brickA2, self.brickA4, self.brickA3]
        self.assertEqual(list(wall), expected)

    # Single keys - Single bricks - Multi models

    def test_single_key_desc_sorting_single_bricks_multi_models(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity'), SORTING_DESC),
        ))
        expected = [self.brickB1, self.brickB2, self.brickB3, self.brickB4,
                    self.brickA1, self.brickA2, self.brickA3, self.brickA4]
        self.assertEqual(list(wall), expected)

    def test_single_key_asc_sorting_single_bricks_multi_models(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity'), SORTING_ASC),
        ))
        expected = [self.brickA4, self.brickA3, self.brickA2, self.brickA1,
                    self.brickB4, self.brickB3, self.brickB2, self.brickB1]
        self.assertEqual(list(wall), expected)

    # Multi keys - Single bricks - Multi models

    def test_multi_key_1_sorting_single_bricks_multi_models(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('is_sticky'), SORTING_DESC),
            (Criterion('popularity'), SORTING_DESC),
        ))
        expected = [self.brickB3, self.brickA3, self.brickB1, self.brickB2,
                    self.brickB4, self.brickA1, self.brickA2, self.brickA4]
        self.assertEqual(list(wall), expected)

    def test_multi_key_2_sorting_single_bricks_multi_models(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('is_sticky'), SORTING_ASC),
            (Criterion('popularity'), SORTING_DESC),
        ))
        expected = [self.brickB1, self.brickB2, self.brickB4, self.brickA1,
                    self.brickA2, self.brickA4, self.brickB3, self.brickA3]
        self.assertEqual(list(wall), expected)

    # Single keys - Multi bricks - Single models

    def test_single_key_1_sorting_multi_bricks_single_models(self):
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity', callback=max), SORTING_DESC),
        ))
        expected = [self.brickC1, self.brickC2]
        self.assertEqual(list(wall), expected)

    def test_single_key_2_sorting_multi_bricks_single_models(self):
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity', callback=min), SORTING_DESC),
        ))
        expected = [self.brickC1, self.brickC2]
        self.assertEqual(list(wall), expected)

    def test_single_key_3_sorting_multi_bricks_single_models(self):
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity', callback=max), SORTING_ASC),
        ))
        expected = [self.brickC2, self.brickC1]
        self.assertEqual(list(wall), expected)

    def test_single_key_4_sorting_multi_bricks_single_models(self):
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity', callback=min), SORTING_ASC),
        ))
        expected = [self.brickC2, self.brickC1]
        self.assertEqual(list(wall), expected)

    # Multi keys - Multi bricks - Single models

    def test_multi_key_1_sorting_multi_bricks_single_models(self):
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('pub_date', callback=max), SORTING_DESC),
            (Criterion('popularity', callback=max), SORTING_DESC),
        ))
        expected = [self.brickC2, self.brickC1]
        self.assertEqual(list(wall), expected)

    def test_multi_key_2_sorting_multi_bricks_single_models(self):
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('pub_date', callback=max), SORTING_ASC),
            (Criterion('popularity', callback=min), SORTING_DESC),
        ))
        expected = [self.brickC1, self.brickC2]
        self.assertEqual(list(wall), expected)

    # Multi keys - Mixed bricks - Multi models

    def test_multi_key_1_sorting_multi_bricks_multi_models(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('is_sticky', default=False), SORTING_DESC),
            (Criterion('pub_date', callback=max), SORTING_DESC),
        ))
        expected = [self.brickA3, self.brickB3,
                    self.brickA4, self.brickA2, self.brickA1,
                    self.brickB4, self.brickB2, self.brickB1,
                    self.brickC2, self.brickC1]
        self.assertEqual(list(wall), expected)

    def test_multi_key_2_sorting_multi_bricks_multi_models(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        self._create_model_c_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('is_sticky', default=False), SORTING_DESC),
            (Criterion('pub_date', callback=max), SORTING_ASC),
        ))
        expected = [self.brickB3, self.brickA3,
                    self.brickC1, self.brickC2,
                    self.brickB1, self.brickB2, self.brickB4,
                    self.brickA1, self.brickA2, self.brickA4]
        self.assertEqual(list(wall), expected)

    def test_multi_key_1_sorting_single_bricks_multi_models_reversed(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('is_sticky'), SORTING_DESC),
            (Criterion('popularity'), SORTING_DESC),
        ))
        expected = [self.brickB3, self.brickA3, self.brickB1, self.brickB2,
                    self.brickB4, self.brickA1, self.brickA2, self.brickA4]
        expected = reversed(expected)
        self.assertEqual(list(reversed(list(wall))), list(expected))

    # Pickle

    def test_pickle(self):
        import pickle
        import datetime
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('is_sticky', default=datetime.datetime.now), SORTING_DESC),
        ))
        pickled = pickle.dumps(wall)
        unpickled = pickle.loads(pickled)
        self.assertListEqual([i.item for i in list(wall)], [i.item for i in list(unpickled)])

    # Brick

    def test_single_brick_context(self):
        obj = TestModelA.objects.create(name='objectA1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        brick = TestSingleBrick(obj)
        self.assertEqual(brick.get_context(), {'object': obj})

    def test_list_brick_context(self):
        obj1 = TestModelC.objects.create(name='objectC1', popularity=20,
            pub_date=datetime.datetime(2002, 1, 1, 12, 0), is_sticky=False)
        obj2 = TestModelC.objects.create(name='objectC2', popularity=19,
            pub_date=datetime.datetime(2003, 1, 1, 12, 0), is_sticky=False)
        brick = TestListBrick([obj1, obj2])
        self.assertEqual(brick.get_context(), {'object_list': [obj1, obj2]})

    def test_list_brick_chunk(self):
        now = datetime.datetime.now()
        objects = []
        for i in range(12):
            obj = TestModelC.objects.create(name=i, popularity=i, pub_date=now)
            objects.append(obj)
        bricks = TestListBrick.get_bricks_for_queryset(TestModelC.objects.all())
        for i in range(3):
            start = i * TestListBrick.chunk_size
            stop = start + TestListBrick.chunk_size
            self.assertEqual(bricks[i].items, objects[start:stop])

    # Template Tag

    def test_template_tag_single_brick(self):
        obj = TestModelA.objects.create(name='objectA1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        brick = TestSingleBrick(obj)
        template = Template('{% load render_brick from bricks %}{% render_brick brick %}')
        html = template.render(Context({'brick': brick}))
        self.assertHTMLEqual(html, 'objectA1')

    @unittest.skipIf(get_version().startswith('1.5'), 'Django is too old')
    def test_template_tag_single_brick_template_used(self):
        obj = TestModelA.objects.create(name='objectA1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        brick = TestSingleBrick(obj)
        template = Template('{% load render_brick from bricks %}{% render_brick brick %}')
        with self.assertTemplateUsed('single_brick.html'):
            template.render(Context({'brick': brick}))

    def test_template_tag_list_brick(self):
        obj1 = TestModelC.objects.create(name='objectC1', popularity=20,
            pub_date=datetime.datetime(2002, 1, 1, 12, 0), is_sticky=False)
        obj2 = TestModelC.objects.create(name='objectC2', popularity=19,
            pub_date=datetime.datetime(2003, 1, 1, 12, 0), is_sticky=False)
        brick = TestListBrick([obj1, obj2])
        template = Template('{% load render_brick from bricks %}{% render_brick brick %}')
        html = template.render(Context({'brick': brick}))
        self.assertHTMLEqual(html, 'objectC1objectC2')

    @unittest.skipIf(get_version().startswith('1.5'), 'Django is too old')
    def test_template_tag_list_brick_template_used(self):
        obj1 = TestModelC.objects.create(name='objectC1', popularity=20,
            pub_date=datetime.datetime(2002, 1, 1, 12, 0), is_sticky=False)
        obj2 = TestModelC.objects.create(name='objectC2', popularity=19,
            pub_date=datetime.datetime(2003, 1, 1, 12, 0), is_sticky=False)
        brick = TestListBrick([obj1, obj2])
        template = Template('{% load render_brick from bricks %}{% render_brick brick %}')
        with self.assertTemplateUsed('list_brick.html'):
            template.render(Context({'brick': brick}))

    def test_template_tag_extra_context(self):
        obj = TestModelA.objects.create(name='objectA1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        brick = TestSingleBrick(obj)
        template = Template('{% load render_brick from bricks %}{% render_brick brick foo="bar" %}')
        html = template.render(Context({'brick': brick}))
        self.assertHTMLEqual(html, 'objectA1bar')

    def test_template_tag_single_brick_no_template(self):
        obj = TestModelA.objects.create(name='objectA1', popularity=5,
            pub_date=datetime.datetime(2010, 1, 1, 12, 0), is_sticky=False)
        brick = TestNoTemplateSingleBrick(obj)
        template = Template('{% load render_brick from bricks %}{% render_brick brick %}')
        with self.assertRaises(TemplateNameNotFound):
            template.render(Context({'brick': brick}))

    # Filtering

    @unittest.skipIf(get_version().startswith('1.5'), 'Django is too old')
    def test_matching_filter(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity'), SORTING_DESC),
        ))
        wall = wall.filter(callback_filter_a)
        expected = [self.brickA1, self.brickA2, self.brickA3, self.brickA4]
        self.assertEqual(list(wall), expected)

    @unittest.skipIf(get_version().startswith('1.5'), 'Django is too old')
    def test_matching_filter_multi_models(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity'), SORTING_ASC),
        ))
        wall = wall.filter(callback_filter_a)
        expected = [self.brickA4, self.brickA3, self.brickA2, self.brickA1]
        self.assertEqual(list(wall), expected)

    def test_non_matching_filter(self):
        self._create_model_a_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity'), SORTING_DESC),
        ))
        wall = wall.filter(lambda x:False)
        self.assertEqual(list(wall), [])

    @unittest.skipIf(get_version().startswith('1.5'), 'Django is too old')
    def test_matching_filter_multiple(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity'), SORTING_ASC),
        ))
        filtered_wall_a = wall.filter(callback_filter_a)
        expected = [self.brickA4, self.brickA3, self.brickA2, self.brickA1]
        self.assertEqual(list(filtered_wall_a), expected)
        filtered_wall_b = wall.filter(callback_filter_b)
        expected = [self.brickB4, self.brickB3, self.brickB2, self.brickB1]
        self.assertEqual(list(filtered_wall_b), expected)
        expected = [self.brickA4, self.brickA3, self.brickA2, self.brickA1,
                    self.brickB4, self.brickB3, self.brickB2, self.brickB1]
        self.assertEqual(list(wall), expected)

    @unittest.skipIf(get_version().startswith('1.5'), 'Django is too old')
    def test_matching_filter_multiple_callback(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity'), SORTING_ASC),
        ))
        filtered_wall = wall.filter([callback_filter_a, callback_filter_always_true])
        expected = [self.brickA4, self.brickA3, self.brickA2, self.brickA1]
        self.assertEqual(list(filtered_wall), expected)

    @unittest.skipIf(get_version().startswith('1.5'), 'Django is too old')
    def test_matching_filter_multiple_callback_or(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        wall = TestBrickWall(self.bricks, criteria=(
            (Criterion('popularity'), SORTING_ASC),
        ))
        filtered_wall = wall.filter([callback_filter_a, callback_filter_always_true], 'OR')
        expected = [self.brickA4, self.brickA3, self.brickA2, self.brickA1,
                    self.brickB4, self.brickB3, self.brickB2, self.brickB1]
        self.assertEqual(list(filtered_wall), expected)

    def test_factory_class(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        criteria = (
            (Criterion('is_sticky'), SORTING_ASC),
            (Criterion('popularity'), SORTING_DESC),
        )
        wall = TestWallFactory(criteria).wall()
        expected = [self.brickB1.item, self.brickB2.item, self.brickB4.item,
                    self.brickA1.item, self.brickA2.item, self.brickA4.item,
                    self.brickB3.item, self.brickA3.item]
        self.assertEqual([b.item for b in wall], expected)

    def test_factory_no_criteria(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        wall = TestWallFactoryNoCriteria().wall()
        expected = [self.brickA1.item, self.brickA2.item, self.brickA3.item,
                    self.brickA4.item, self.brickB1.item, self.brickB2.item,
                    self.brickB3.item, self.brickB4.item]
        self.assertEqual([b.item for b in wall], expected)

    def test_wrong_factory(self):
        self._create_model_a_objects_and_bricks()
        with self.assertRaises(TypeError):
            TestWrongContentWallFactory().wall()

    def test_factory_method_single_queryset(self):
        self._create_model_a_objects_and_bricks()
        criteria = (
            (Criterion('is_sticky'), SORTING_ASC),
            (Criterion('popularity'), SORTING_DESC),
        )
        wall = wall_factory(TestModelA.objects.all(), TestSingleBrick,
                            criteria=criteria)
        expected = [self.brickA1.item, self.brickA2.item, self.brickA4.item,
                    self.brickA3.item]
        self.assertEqual([b.item for b in wall], expected)

    def test_factory_method_multiple_queryset(self):
        self._create_model_a_objects_and_bricks()
        self._create_model_b_objects_and_bricks()
        criteria = (
            (Criterion('is_sticky'), SORTING_ASC),
            (Criterion('popularity'), SORTING_DESC),
        )
        content = (
            TestModelA.objects.all(),
            TestModelB.objects.all(),
        )
        wall = wall_factory(content, TestSingleBrick, criteria=criteria)
        expected = [self.brickB1.item, self.brickB2.item, self.brickB4.item,
                    self.brickA1.item, self.brickA2.item, self.brickA4.item,
                    self.brickB3.item, self.brickA3.item]
        self.assertEqual([b.item for b in wall], expected)
