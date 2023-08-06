from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe


__all__ = ['make_admin_url', 'print_link']


def make_admin_url(model, pk=None, action="change"):
    """
    Given a model and an action, make a url to the correct admin page

    If `model` is a model instance, that models `pk` is used as the instance to
    link to. Otherwise, a `pk` to link to must be provided. The function can
    thus be used with either a model instance, or a Model class and a `pk`.

    Usage:
        make_admin_url(Foo, pk=10)  # '/admin/app/foo/10/'

        foo = Foo.objects.get(pk=4)
        make_admin_url(foo)  # '/admin/app/foo/4/'
        make_admin_url(foo, action="delete")  # '/admin/app/foo/delete/4/'

    """
    app_label = model._meta.app_label.lower()
    model_name = model._meta.model_name
    url_name = "admin:%s_%s_%s" % (app_label, model_name, action)

    if pk is None:
        pk = model.pk

    url = reverse(url_name, args=(pk,))
    return url


def print_link(text, url, class_name=""):
    """
    Prints an HTML link, given the inner text, a url, and an optional class
    name. None of the inputs are escaped.
    """
    return mark_safe(
        '<a href="%s" class="%s">%s</a>' % (url, class_name, text))
