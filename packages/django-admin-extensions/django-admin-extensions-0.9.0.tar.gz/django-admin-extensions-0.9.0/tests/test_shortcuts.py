from __future__ import absolute_import, unicode_literals

from unittest import TestCase

from django.contrib import admin

from .app.models import SimpleModel


class ShortcutTests(TestCase):
    def test_register(self):
        # The SimpleModel in the test app is registered using this shortcut,
        # so if that model is registered, it worked.
        self.assertTrue(SimpleModel in admin.site._registry)
