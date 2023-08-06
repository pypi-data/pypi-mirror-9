from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class SimpleModel(models.Model):
    text = models.CharField(max_length=100, default='', blank=True)

    def __str__(self):
        return self.text


@python_2_unicode_compatible
class ParentModel(models.Model):
    simplemodel = models.ForeignKey(SimpleModel)

    def __str__(self):
        return '(ParentModel: {})'.format(self.simplemodel)


@python_2_unicode_compatible
class ManySimpleModel(models.Model):
    simplemodel_set = models.ManyToManyField(SimpleModel)

    def __str__(self):
        return 'Nothing interesting'
