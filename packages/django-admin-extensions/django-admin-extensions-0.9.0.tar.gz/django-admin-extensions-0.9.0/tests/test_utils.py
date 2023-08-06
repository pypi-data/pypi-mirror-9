from __future__ import absolute_import, unicode_literals

from adminextensions.utils import make_admin_url, print_link

from django.test import TestCase

from tests.app.models import SimpleModel


class UtilTests(TestCase):

    def test_make_admin_url(self):
        instance = SimpleModel.objects.create(pk=3)

        self.assertEqual(make_admin_url(SimpleModel, pk='5'),
                         '/admin/app/simplemodel/5/')

        self.assertEqual(make_admin_url(instance),
                         '/admin/app/simplemodel/3/')

        self.assertEqual(make_admin_url(SimpleModel, pk='5', action='history'),
                         '/admin/app/simplemodel/5/history/')

        self.assertEqual(make_admin_url(instance, action='delete'),
                         '/admin/app/simplemodel/3/delete/')

    def test_print_link(self):
        self.assertHTMLEqual(print_link('Text', '/test/url/', 'classname'),
                             '<a href="/test/url/" class="classname">Text</a>')
