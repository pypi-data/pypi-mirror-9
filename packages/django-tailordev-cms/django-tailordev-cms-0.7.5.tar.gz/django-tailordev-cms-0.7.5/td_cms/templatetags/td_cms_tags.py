# -*- coding: utf-8 -*-
import logging

from datetime import datetime
from django import template
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from modeltranslation.settings import AVAILABLE_LANGUAGES

from td_cms.models import Category, Page

register = template.Library()
logger = logging.getLogger(__name__)


@register.assignment_tag
def get_parent_categories():
    """
    Add TD CMS page categories to the context
    """
    return Category.visible_objects.all()


@register.assignment_tag
def get_highlighted_pages():
    """
    Add TD CMS highlighted pages to the context
    """
    return Page.highlighted_objects.all()


@register.assignment_tag
def get_category(slug):
    """
    Add a category to the context given its slug
    """
    for language_code in AVAILABLE_LANGUAGES:
        slug_field = 'slug_%s' % language_code
        try:
            return Category.objects.get(**{slug_field: slug})
        except:
            pass
    logger.warning("Cannot resolve category slug '%s'" % slug)
    return None


@register.assignment_tag
def get_page(slug):
    """
    Add a page to the context given its slug
    """
    for language_code in AVAILABLE_LANGUAGES:
        slug_field = 'slug_%s' % language_code
        try:
            return Page.objects.get(**{slug_field: slug})
        except:
            pass
    logger.warning("Cannot resolve page slug '%s'" % slug)
    return None


@register.assignment_tag
def get_page_url_for_language(page, language_code):
    """
    Get page url for a speficied language code.

    Returns: the url or '/' if a NoReverseMatch exception is raised

    ex: get_page_url_for_language page fr as url
    """
    if language_code not in AVAILABLE_LANGUAGES:
        msg = "Selected language %s is not available" % language_code
        raise ImproperlyConfigured(msg)

    if page is None:
        msg = "Input page does not exists"
        raise ObjectDoesNotExist(msg)

    category = page.categories.all()[0]
    view_name = 'page_detail_%s' % language_code
    category_slug = getattr(category, 'slug_%s' % language_code, None)
    page_slug = getattr(page, 'slug_%s' % language_code, None)

    # Silently fail when page has not been translated
    if None in (page_slug, category_slug):
        return '/'

    return reverse(view_name, args=[category_slug, page_slug])


@register.filter
def timestamp(value):
    """
    Convert a datetime object representation to a unix timestamp.

    If the object to filter is not a valid datetime.datetime instance, returns
    the original unmodified object.
    """
    if not isinstance(value, datetime):
        return value
    return value.strftime("%s")


@register.inclusion_tag(
    'td_cms/partials/comments/disqus_thread.html',
    takes_context=True
)
def show_disqus_thread(context):
    """
    Show the disqus thread for a Page that allows comments
    """
    if not getattr(settings, 'TD_CMS_DISQUS_SHORTNAME', None):
        msg = _('TD_CMS_DISQUS_SHORTNAME parameter is missing in your '
                'settings')
        messages.warning(context['request'], msg)
        return context

    context.update(
        {
            'disqus_shortname': settings.TD_CMS_DISQUS_SHORTNAME,
        }
    )
    return context
