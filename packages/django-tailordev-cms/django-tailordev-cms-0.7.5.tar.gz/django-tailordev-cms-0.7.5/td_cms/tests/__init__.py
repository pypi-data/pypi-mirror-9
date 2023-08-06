# -*- coding: utf-8 -*-
"""
Models loaded for testing purpose
"""
from django.db import models
from django.utils.translation import get_language
from mptt.fields import TreeManyToManyField

from ..abstract_models import AbstractPage
from ..models import Category


class Foo(models.Model):
    """
    Foo model is only defined here for testing purpose
    """
    title = models.CharField(max_length=200)
    categories = TreeManyToManyField(Category, related_name='foos',
                                     null=True, blank=True)


class Bar(AbstractPage):
    """
    A Page-derived test model
    """
    @models.permalink
    def get_absolute_url(self):
        language = get_language().split('-')[0]
        return (r'bar_detail_%s' % language, (unicode(self.pk), self.slug))


# Register Bar model translations
from modeltranslation.translator import translator, TranslationOptions


class BarTranslationOptions(TranslationOptions):
    fields = ('title', 'slug', 'synopsis', 'content',)


translator.register(Bar, BarTranslationOptions)
