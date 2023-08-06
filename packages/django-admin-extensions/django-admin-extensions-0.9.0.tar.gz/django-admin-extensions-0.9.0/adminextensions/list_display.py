from __future__ import absolute_import, unicode_literals

from django.template.defaultfilters import truncatewords
from django.utils.html import escape, strip_tags
from django.utils import six 

from .utils import make_admin_url, print_link

if six.PY3:
    from functools import reduce


__all__ = ['link_field', 'serialized_many_to_many_field', 'truncated_field',
           'related_field']


def link_display_item(short_description, allow_tags=True,
                      admin_order_field=None):
    """
    Marks a function for use as a link_display item. Use as a decorator.
    """
    def decorator(fn):
        fn.short_description = short_description
        fn.allow_tags = allow_tags
        fn.admin_order_field = admin_order_field
        return fn
    return decorator


def link_field(field, action="change", formatter=six.text_type,
               short_description=None):
    """
    An list field item that links to a related model instance from the
    changelist view

    `field` is the name of the related model on the source model.

    `action` can be any of the admin actions: 'change', 'history', or 'delete'.
    The default is 'change'

    `formatter` is used to transform the related model to a string. The default
    is to call the `__str__()` method on the instance.

    `short_description` is used as the column header. It defaults to the field
    name.

    Usage:

        class BookModelAdmin(ExtendedModelAdmin):
            list_display = ('name', link_field('author'))
    """

    if short_description is None:
        short_description = field

    @link_display_item(short_description)
    def item(obj):
        related = getattr(obj, field)
        if related is None:
            return '<em>(None)</em>'

        url = make_admin_url(related, action=action)
        name = formatter(related)

        link = print_link(escape(name), url)

        return link

    return item


def serialized_many_to_many_field(field, formatter=six.text_type, joiner=', ',
                                  short_description=None, linked=False):
    """
    Display all the related instances in a ManyToMany relation

    `field` is the name of the relation on the source model.

    `formatter` is used to transform the related instance to a string. The
    default is to call the `__str__()` method on the instance.

    `joiner` is inserted between every instance. Defaults to ', '

    `short_description` is used as the column header. It defaults to the field
    name.

    If `linked` is True, each model instance is linked to its `change` view.

    Usage:

        class BookModelAdmin(ExtendedModelAdmin):
            list_display = ('name', serialized_many_to_many_field('publishers'))
    """
    if short_description is None:
        short_description = field

    old_formatter = formatter
    if linked:
        formatter = lambda obj: print_link(escape(old_formatter(obj)), make_admin_url(obj))
    else:
        formatter = lambda obj: escape(old_formatter(obj))

    @link_display_item(short_description)
    def item(obj):
        return joiner.join(formatter(x) for x in getattr(obj, field).all())

    return item


def truncated_field(field, length=20, short_description=None, strip_html=False):
    """
    Display a truncated version of `field` in the list display

    The field is limited to `length` words, using Djangos `truncatewords`
    helper.

    `short_description` is used as the column header. It defaults to the field
    name.

    Usage:

        class BookModelAdmin(ExtendedModelAdmin):
            list_display = ('name', serialized_many_to_many_field('publishers'))
    """
    if short_description is None:
        short_description = field

    @link_display_item(short_description)
    def item(obj):
        text = getattr(obj, field)
        if strip_html:
            text = strip_tags(text)

        return escape(truncatewords(text, length))

    return item


def related_field(field, formatter=None, short_description=None):
    """
    Show a related field in `list_display`

    `field` is the double-underscore-delimited path to the field to display,
    such as `author__name`.

    `formatter` takes the value and formats it for display. The default is to
    just return the value. The Django admin is fairly sensible at formatting
    things.

    `short_description` is used as the column header. It defaults to `field`.
    """

    if short_description is None:
        short_description = field

    if formatter is None:
        formatter = lambda x: x

    field_path = field.split('__')

    @link_display_item(short_description, admin_order_field=field)
    def item(obj):
        return escape(formatter(reduce(getattr, field_path, obj)))

    return item
