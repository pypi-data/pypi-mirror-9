# -*- coding: utf-8 -*-
import logging

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core.urlresolvers import resolve
from django.http import Http404
from django.utils.http import is_safe_url
from django.utils.translation import (
    activate as translation_activate, check_for_language, ugettext as _
)
from django.views.generic import DetailView, RedirectView
from importlib import import_module
from modeltranslation.settings import AVAILABLE_LANGUAGES
from purl import URL

from .models import Category, Page


logger = logging.getLogger(__name__)


class TranslatedSlugMixin(object):
    """
    Returns the object the view is displaying, given a translated slug.
    """

    def get_object(self, queryset=None):
        # Use a custom queryset if provided; this is required for subclasses
        # like DateDetailView
        if queryset is None:
            queryset = self.get_queryset()

        # Available languages translated slug field name and value
        for language in AVAILABLE_LANGUAGES:
            slug_field = 'slug_%s' % language

            # The translated slug value matching our url pattern
            slug = self.kwargs.get(slug_field, None)

            if slug:
                break

        # Our object
        queryset = queryset.filter(**{slug_field: slug})

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except ObjectDoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj


class SetLanguageView(RedirectView):
    """
    Mimic the django default set_language i18n view with language specific url
    support
    """
    permanent = False

    def get_redirect_url(self, **kwargs):
        """
        This is the core part
        """
        path = URL(self.request.META.get('HTTP_REFERER')).path()
        try:
            match = resolve(path)
        except Http404:
            return '/'

        next = self.request.REQUEST.get('next', None) or '/'

        # Get url slug
        fieldset = dict((k, v) for k, v in match.kwargs.iteritems() if 'slug_' in k)  # NOPEP8
        if fieldset:
            view_path = match.func.__module__
            view_name = match.func.func_name
            root_module = view_path.split('.')[0]

            # Import and define the module containing target view
            try:
                globals()[root_module] = import_module(root_module)
            except ImportError:
                logger.error(
                    'Cannot import module %s from matching view.' % (
                        root_module
                    )
                )
                return next

            # Instantiate the view
            #
            # Known issue: this may not work with function based views
            exec('view_class = %s.%s()' % (view_path, view_name))
            if hasattr(view_class, 'model'):  # NOQA
                obj = view_class.model.objects.get(**fieldset)  # NOQA
                next = obj.get_absolute_url()

        # Check url safety
        if not is_safe_url(url=next, host=self.request.get_host()):
            next = '/'

        return next

    def post(self, request, *args, **kwargs):
        """
        Get target language and save this parameter to user session
        """
        lang_code = request.POST.get('language', None)
        if lang_code and check_for_language(lang_code):
            if not hasattr(request, 'session'):
                raise ImproperlyConfigured(
                    'td_cms requires the django.contrib.sessions app '
                    'installed and configured'
                )
            request.session['django_language'] = lang_code
            translation_activate(lang_code)
        return super(SetLanguageView, self).post(request, *args, **kwargs)


class CategoryDetailView(TranslatedSlugMixin, DetailView):
    model = Category
    template_name = 'td_cms/category_detail.html'


class PageDetailView(TranslatedSlugMixin, DetailView):
    model = Page
    template_name = 'td_cms/page_detail.html'
