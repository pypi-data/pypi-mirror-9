# -*- coding: utf-8 -*-
from django.db import models

from linguist.models.base import Translation
from linguist.metaclasses import ModelMeta as LinguistMeta
from linguist.mixins import ManagerMixin as LinguistManagerMixin

import six


# Managers
# ------------------------------------------------------------------------------

class FooManager(LinguistManagerMixin, models.Manager):
    """
    Manager of Foo model.
    """
    pass


class BarManager(LinguistManagerMixin, models.Manager):
    """
    Manager of Bar model.
    """
    pass


class DefaultLanguageFieldManager(LinguistManagerMixin, models.Manager):
    """
    Manager of DefaultLanguageFieldModel.
    """
    pass


class DeciderManager(LinguistManagerMixin, models.Manager):
    """
    Manager of DeciderModel
    """
    pass


# Models
# ------------------------------------------------------------------------------

class FooModel(six.with_metaclass(LinguistMeta, models.Model)):
    """
    A foo.
    """
    title = models.CharField(max_length=255)
    excerpt = models.TextField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = FooManager()

    class Meta:
        linguist = {
            'identifier': 'foo',
            'fields': ('title', 'excerpt', 'body'),
        }


class BarModel(six.with_metaclass(LinguistMeta, models.Model)):
    """
    A bar.
    """
    title = models.CharField(max_length=255, null=True, blank=True)

    objects = BarManager()

    class Meta:
        linguist = {
            'identifier': 'bar',
            'fields': ('title', ),
        }


class DefaultLanguageFieldModel(six.with_metaclass(LinguistMeta, models.Model)):
    """
    A bar.
    """
    title = models.CharField(max_length=255, null=True, blank=True)
    lang = models.CharField(max_length=2, default='fr')

    objects = DefaultLanguageFieldManager()

    class Meta:
        linguist = {
            'identifier': 'default_language_field_model',
            'fields': ('title', ),
            'default_language_field': 'lang',
        }


class DefaultLanguageFieldModelWithCallable(six.with_metaclass(LinguistMeta, models.Model)):
    """
    A bar.
    """
    title = models.CharField(max_length=255, null=True, blank=True)
    lang = models.CharField(max_length=2, default='fr')

    objects = DefaultLanguageFieldManager()

    class Meta:
        verbose_name = 'default_language_with_callable'
        linguist = {
            'identifier': 'default_language_field_model',
            'fields': ('title', ),
            'default_language_field': 'language',
        }

    def language(self):
        return 'fr'


class CustomTranslationModel(Translation):
    class Meta:
        abstract = False


class DeciderModel(six.with_metaclass(LinguistMeta, models.Model)):
    """
    Example of a model using decider feature.
    """
    title = models.CharField(max_length=255, null=True, blank=True)

    objects = DeciderManager()

    class Meta:
        linguist = {
            'identifier': 'default_language_field_model',
            'fields': ('title', ),
            'decider': CustomTranslationModel,
        }
