from __future__ import absolute_import, unicode_literals

from django.test import TestCase
from django.utils.six import text_type

from adminextensions.list_display import (
    link_field, serialized_many_to_many_field, truncated_field, related_field)

from .app.models import SimpleModel, ParentModel, ManySimpleModel

class ListDisplayTests(TestCase):

    def setUp(self):
        self.parentmodel = ParentModel.objects.create(
            simplemodel=SimpleModel.objects.create(text='foo'))

    def test_link_field_simple(self):
        callable = link_field('simplemodel')
        self.assertHTMLEqual(
            callable(self.parentmodel),
            '<a href="/admin/app/simplemodel/1/" class="">foo</a>')
        self.assertEqual(callable.short_description, 'simplemodel')

    def test_link_field_description(self):
        callable = link_field('simplemodel', short_description='Simple model')
        self.assertEqual(callable.short_description, 'Simple model')

    def test_link_field_formatter(self):
        callable = link_field('simplemodel', formatter=lambda s: s.text.upper())
        self.assertHTMLEqual(
            callable(self.parentmodel),
            '<a href="/admin/app/simplemodel/1/" class="">FOO</a>')

    def test_link_field_history(self):
        callable = link_field('simplemodel', action='history')
        self.assertHTMLEqual(
            callable(self.parentmodel),
            '<a href="/admin/app/simplemodel/1/history/" class="">foo</a>')


class SerializedManyToManyTests(TestCase):

    texts = ['foo', 'bar', 'baz', 'quux']

    def setUp(self):
        self.many = ManySimpleModel.objects.create()
        self.many.simplemodel_set = [SimpleModel.objects.create(text=text)
                                     for text in self.texts]

    def test_serialized_many_to_many(self):
        callable = serialized_many_to_many_field('simplemodel_set')
        self.assertEqual(
            callable(self.many),
            ', '.join(self.texts))
        self.assertEqual(callable.short_description, 'simplemodel_set')

    def test_serialized_joiner(self):
        callable = serialized_many_to_many_field(
            'simplemodel_set', joiner=' - ')
        self.assertEqual(
            callable(self.many),
            ' - '.join(self.texts))

    def test_serialized_description(self):
        callable = serialized_many_to_many_field(
            'simplemodel_set', short_description='Simple models')
        self.assertEqual(callable.short_description, 'Simple models')

    def test_serialized_formatter(self):
        callable = serialized_many_to_many_field(
            'simplemodel_set', joiner=' and ', formatter=lambda s: s.text.upper())
        self.assertEqual(
            callable(self.many),
            ' and '.join(map(text_type.upper, self.texts)))

    def test_serialized_formatter(self):
        callable = serialized_many_to_many_field(
            'simplemodel_set', joiner=' and ', formatter=lambda s: s.text.upper())
        self.assertEqual(
            callable(self.many),
            ' and '.join(map(text_type.upper, self.texts)))

    def test_serialized_linker(self):
        callable = serialized_many_to_many_field(
            'simplemodel_set', linked=True)
        self.assertEqual(
            callable(self.many),
            ', '.join(
                '<a href="/admin/app/simplemodel/{}/" class="">{}</a>'.format(s.pk, s.text)
                for s in self.many.simplemodel_set.all()))


class TruncatedFieldTests(TestCase):

    words = ['a', 'b', 'c', 'd'] * 20

    def setUp(self):
        self.simplemodel = SimpleModel(text=' '.join(self.words))

    def test_truncated_field(self):
        callable = truncated_field('text')
        self.assertEqual(callable(self.simplemodel),
                         ' '.join(self.words[:20]) + ' ...')
        self.assertEqual(callable.short_description,
                         'text')

    def test_truncated_strip(self):
        callable = truncated_field('text', strip_html=True)
        self.simplemodel.text = '<p>{}</p>'.format(self.simplemodel.text)
        self.assertEqual(callable(self.simplemodel),
                         ' '.join(self.words[:20]) + ' ...')

    def test_truncated_description(self):
        callable = truncated_field('text', short_description='Some text')
        self.assertEqual(callable.short_description,
                         'Some text')

    def test_truncated_length(self):
        callable = truncated_field('text', length=10)
        self.assertEqual(callable(self.simplemodel),
                         ' '.join(self.words[:10]) + ' ...')

        callable = truncated_field('text', length=100)
        self.assertEqual(callable(self.simplemodel),
                         ' '.join(self.words))


class RelatedFieldTests(TestCase):

    def setUp(self):
        self.simplemodel = SimpleModel.objects.create(text='foo')
        self.parentmodel = ParentModel.objects.create(simplemodel=self.simplemodel)

    def test_related_field(self):
        callable = related_field('simplemodel__text')
        self.assertEqual(callable(self.parentmodel),
                         'foo')
        self.assertEqual(callable.short_description, 'simplemodel__text')

    def test_related_description(self):
        callable = related_field('simplemodel__text', short_description='Text')
        self.assertEqual(callable.short_description, 'Text')

    def test_related_formatter(self):
        callable = related_field('simplemodel__text', formatter=text_type.upper)
        self.assertEqual(callable(self.parentmodel),
                         'FOO')
