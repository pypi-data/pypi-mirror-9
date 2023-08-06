from __future__ import absolute_import, unicode_literals

from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.utils import six

from .utils import print_link, make_admin_url


__all__ = ['model_search', 'model_add', 'model_link']


def object_tool(fn):
    """
    Marks a function for use as an object tool. Use as a decorator.
    """
    fn.do_not_call_in_templates = True
    return fn


def model_search(text, model, args):
    """
    An object tool to link to a change list with a preloaded search term

    `text` is the label to use on the object tool, while `model` is the model
    class to link to. `args` is a callable that should return a `dict` of
    querystring arguments when passed an instance of the original model.

    Usage:

        class AuthorModelAdmin(ExtendedModelAdmin):
            object_tools = {
                'change': [model_search(
                    "Books", Book,
                    lambda author: {'author__id': author.id})]
            }
    """

    app_label = model._meta.app_label
    model_name = model._meta.model_name

    url_name = 'admin:%s_%s_changelist' % (app_label, model_name)

    @object_tool
    def tool(context, link_class="model_search"):

        url = reverse(url_name)

        qd = QueryDict(None, mutable=True)
        qd.update(args(context['original']))

        query_string = qd.urlencode()
        search_url = url + '?' + query_string

        return print_link(text, search_url, link_class)
    return tool


def model_link(text, model, pk_getter, action="change"):
    """
    An object tool to link to a related model from a models page
    Used in `list_display` to link to a related model instance's view/edit page

    `pk_getter` can be either a string naming the pk field of the related
    model, or a callable which returns the pk of the related model.

    `action` can be any of the admin actions: 'change', 'history', or 'delete'.
    The default is 'change'

    Usage:

        class BookModelAdmin(ExtendedModelAdmin):
            object_tools = {
                'change': [model_link("Author", Author, 'author_id')]
            }
    """

    app_label = model._meta.app_label
    model_name = model._meta.model_name

    if isinstance(pk_getter, six.string_types):
        pk_name = pk_getter
        pk_getter = lambda object: getattr(object, pk_name)

    @object_tool
    def tool(context, link_class="model_search"):
        pk = pk_getter(context['original'])
        if pk:
            url = make_admin_url(model, pk=pk, action=action)
            return print_link(text, url, link_class)
        else:
            return ''
    return tool


def model_add(text, model, defaults=None):
    """
    An object tool that links to the add form for `model`, possibly supplying
    default values for some fields.

    If supplied, `defaults` should be a callable that returns a dict of
    default values to be passed to the add form.

    Usage:

        class AuthorModelAdmin(ExtendedModelAdmin):
            object_tools = {
                'change': [model_add(
                    "Add book", Book, lambda author: {'author': author.pk}
                )]
            }
    """
    app_label = model._meta.app_label
    model_name = model._meta.model_name

    url_name = 'admin:%s_%s_add' % (app_label, model_name)

    @object_tool
    def tool(context, link_class="addlink"):
        url = reverse(url_name)

        if defaults is not None:
            original = context['original']
            querydict = QueryDict('', mutable=True)
            querydict.update(defaults(original))

            url = '?'.join((url, querydict.urlencode()))

        return print_link(text, url, link_class)
    return tool
