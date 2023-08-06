from __future__ import absolute_import, unicode_literals, print_function

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from .app.models import SimpleModel, ParentModel


class AdminTests(TestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='p')
        self.assertTrue(self.client.login(username='admin', password='p'))

    def get_changelist(self, model):
        info = (model._meta.app_label, model._meta.model_name)
        url = reverse("admin:%s_%s_changelist" % info)
        return self.client.get(url, follow=True)

    def get_change(self, instance):
        info = (instance._meta.app_label, instance._meta.model_name)
        url = reverse("admin:%s_%s_change" % info,
                      args=[instance.pk])
        return self.client.get(url, follow=True)

    def test_object_tools(self):
        instance = SimpleModel.objects.create(text='test')
        change = self.get_change(instance)
        self.assertContains(
            change, '<a href="/admin/app/parentmodel/?simplemodel__id={}" class="model_search">Parents</a>'.format(
                instance.pk))

        self.assertContains(
            change, '<a href="/admin/app/parentmodel/add/?simplemodel_id={}" class="addlink">Add parent</a>'.format(
                instance.pk))

    def test_list_fields_simplemodel(self):
        words = list('abcd' * 20)
        instance = SimpleModel.objects.create(text=' '.join(words))
        changelist = self.get_changelist(SimpleModel)
        self.assertContains(
            changelist, ' '.join(words[:20]) + ' ...')

    def test_list_fields_parentmodel(self):
        simple = SimpleModel.objects.create(text='foo')
        parent = ParentModel.objects.create(simplemodel=simple)

        changelist = self.get_changelist(ParentModel)
        self.assertContains(
            changelist, '<a href="/admin/app/simplemodel/{}/" class="">foo</a>'.format(simple.pk))
