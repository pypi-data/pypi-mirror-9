from adminextensions.shortcuts import register
from adminextensions.list_display import truncated_field, link_field
from adminextensions.object_tools import model_search, model_add
from adminextensions.admin import ExtendedModelAdmin

from .models import SimpleModel, ParentModel


@register(SimpleModel)
class SimpleModelAdmin(ExtendedModelAdmin):
    object_tools = {
        'change': [
            model_search('Parents', ParentModel,
                         lambda s: {'simplemodel__id': s.pk}),
            model_add('Add parent', ParentModel,
                      lambda s: {'simplemodel_id': s.pk}),
        ],
    }

    list_display = ['text', truncated_field('text')]


@register(ParentModel)
class ParentModelAdmin(ExtendedModelAdmin):
    list_display = [
        'pk',
        link_field('simplemodel')
    ]
