from __future__ import absolute_import, unicode_literals

import warnings

from django.contrib import admin

from .list_display import (
    link_field, serialized_many_to_many_field, truncated_field, related_field)
from .object_tools import model_link, model_search, model_add
from .utils import print_link, make_admin_url


def register(model):
    """
    Class decorator that registers it in the admin site

    Usage:

        @register(Book)
        class BookAdmin(ExtendedModelAdmin):
            pass
    """

    warnings.warn("Use the django.contrib.admin.register decorator instead",
                  PendingDeprecationWarning)
    def get_class(cls):
        admin.site.register(model, cls)
        return cls
    return get_class
