from __future__ import absolute_import, unicode_literals

from django.http import QueryDict
from django.test import TestCase

from adminextensions.object_tools import model_link, model_search, model_add

from .app.models import SimpleModel, ParentModel


class BaseTestCase(TestCase):
    def setUp(self):
        self.simplemodel = SimpleModel.objects.create(text='text')
        self.parentmodel = ParentModel.objects.create(simplemodel=self.simplemodel)

class ModelLinkTests(BaseTestCase):

    def test_model_link_string_getter(self):
        tool = model_link('View', SimpleModel, 'simplemodel_id')
        self.assertHTMLEqual(
            tool({'original': self.parentmodel}),
            '<a href="/admin/app/simplemodel/{}/" class="model_search">View</a>'.format(self.simplemodel.pk))

    def test_model_link_callable_getter(self):
        tool = model_link('View', SimpleModel, lambda p: p.simplemodel_id)
        self.assertHTMLEqual(
            tool({'original': self.parentmodel}),
            '<a href="/admin/app/simplemodel/{}/" class="model_search">View</a>'.format(self.simplemodel.pk))

    def test_model_link_action(self):
        tool = model_link('History', SimpleModel, 'simplemodel_id', action='history')
        self.assertHTMLEqual(
            tool({'original': self.parentmodel}),
            '<a href="/admin/app/simplemodel/{}/history/" class="model_search">History</a>'.format(self.simplemodel.pk))


class ModelSearchTests(BaseTestCase):

    def test_model_search(self):
        tool = model_search('Parents', ParentModel, lambda s: {'simplemodel_id': s.id})
        self.assertHTMLEqual(
            tool({'original': self.simplemodel}),
            '<a href="/admin/app/parentmodel/?simplemodel_id={}" class="model_search">Parents</a>'.format(self.simplemodel.id))


class ModelAddTests(BaseTestCase):

    def test_model_add(self):
        tool = model_add('Add parent', ParentModel)
        self.assertHTMLEqual(
            tool({'original': self.simplemodel}),
            '<a href="/admin/app/parentmodel/add/" class="addlink">Add parent</a>')

    def test_model_add_defaults(self):
        defaults = lambda s: {'simplemodel_id': s.id, 'another': 'foo'}
        tool = model_add('Add parent', ParentModel, defaults)

        querydict = QueryDict('', mutable=True)
        querydict.update(defaults(self.simplemodel))

        self.assertHTMLEqual(
            tool({'original': self.simplemodel}),
            '<a href="/admin/app/parentmodel/add/?{}" class="addlink">Add parent</a>'.format(
                querydict.urlencode()))
