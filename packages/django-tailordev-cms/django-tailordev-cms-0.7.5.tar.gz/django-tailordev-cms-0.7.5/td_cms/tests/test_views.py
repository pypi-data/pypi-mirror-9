# -*- coding: utf-8 -*-
"""
Django TailorDev CMS

Test views
"""
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.translation import activate, get_language

from ..models import Page
from .factories import BarFactory
from .mixins import TDCMSTestMixin


class SetLanguageViewTests(TDCMSTestMixin, TestCase):
    """
    Tests for the SetLanguageView
    """
    def setUp(self):
        # We reset english as default
        activate('en')

        self._set_category()
        self._set_page(categories=(self.category, ))

        # Set translation
        self.category.name_fr = u"Catégorie 1"
        self.category.save()

        self.page.title_fr = u"Titre 1"
        self.page.save()

    def test_redirection_for_a_page(self):
        """
        Test the post method for a page

        We receive the language code and the next url from the set language
        form
        """
        # This is the default language
        self.assertEqual(get_language(), u'en')

        # Post data to switch the language and follow redirect
        url = reverse('td_cms_set_language')
        response = self.client.post(
            url,
            {
                'next': '/',
                'language': 'fr',
            },
            follow=True,
            HTTP_REFERER=self.page.get_absolute_url(),
        )
        self.assertEqual(response.status_code, 200)

        # This is the translated url were we should have been redirected
        expected_path = u'/fr/categorie-1/titre-1/'
        self.assertEqual(response.request['PATH_INFO'], expected_path)

        # Check that the language has been updated
        self.assertEqual(get_language(), u'fr')

        # Now switch back to en
        response = self.client.post(
            url,
            {
                'next': '/',
                'language': 'en',
            },
            follow=True,
            HTTP_REFERER=self.page.get_absolute_url(),
        )
        self.assertEqual(response.status_code, 200)

        # This is the translated url were we should have been redirected
        expected_path = u'/en/category-1/title-1/'
        self.assertEqual(response.request['PATH_INFO'], expected_path)

        # Check that the language has been updated
        self.assertEqual(get_language(), u'en')

    def test_redirection_for_a_category(self):
        """
        Test the post method for a category

        We receive the language code and the next url from the set language
        form
        """
        # This is the default language
        self.assertEqual(get_language(), u'en')

        # Post data to switch the language and follow redirect
        url = reverse('td_cms_set_language')
        response = self.client.post(
            url,
            {
                'next': '/',
                'language': 'fr',
            },
            follow=True,
            HTTP_REFERER=self.category.get_absolute_url(),
        )
        self.assertEqual(response.status_code, 200)

        # This is the translated url were we should have been redirected
        expected_path = u'/fr/categorie-1/'
        self.assertEqual(response.request['PATH_INFO'], expected_path)

        # Check that the language has been updated
        self.assertEqual(get_language(), u'fr')

        # Switch back to en
        response = self.client.post(
            url,
            {
                'next': '/',
                'language': 'en',
            },
            follow=True,
            HTTP_REFERER=self.category.get_absolute_url(),
        )
        self.assertEqual(response.status_code, 200)

        # This is the translated url were we should have been redirected
        expected_path = u'/en/category-1/'
        self.assertEqual(response.request['PATH_INFO'], expected_path)

        # Check that the language has been updated
        self.assertEqual(get_language(), u'en')

    def test_redirection_for_a_non_cms_page(self):
        """
        Test redirection for an existing url that is not a page or a category
        """
        url = reverse('td_cms_set_language')
        http_referer = reverse('not_cms_test_view')

        response = self.client.post(
            url,
            {
                'next': http_referer,
                'language': 'fr',
            },
            follow=True,
            HTTP_REFERER=http_referer,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], http_referer)

    def test_redirection_from_an_unknown_path(self):
        """
        Test redirection from a 404 http referer
        """
        url = reverse('td_cms_set_language')
        http_referer = u'/nowhere/'

        response = self.client.post(
            url,
            {
                'next': http_referer,
                'language': 'fr',
            },
            follow=True,
            HTTP_REFERER=http_referer,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/')

    def test_redirection_to_an_unsafe_url(self):
        """
        Test redirection to an 'unsafe' url
        """
        url = reverse('td_cms_set_language')
        http_referer = reverse('not_cms_test_view')

        response = self.client.post(
            url,
            {
                'next': 'http://comsource.fr',
                'language': 'fr',
            },
            follow=True,
            HTTP_REFERER=http_referer,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], '/')

    @override_settings(
        INSTALLED_APPS=(),
        MIDDLEWARE_CLASSES=(),
    )
    def test_redirection_without_active_session(self):
        """
        Test redirection without an active session
        """
        # This is the default language
        self.assertEqual(get_language(), u'en')

        # Post data to switch the language and follow redirect
        url = reverse('td_cms_set_language')
        with self.assertRaises(ImproperlyConfigured):
            self.client.post(
                url,
                {
                    'next': '/',
                    'language': 'fr',
                },
                follow=True,
                HTTP_REFERER=self.page.get_absolute_url(),
            )

    def test_redirection_for_a_page_derived_model_detail_view(self):
        """
        Test redirection for a Page-derived model detail view
        """
        bar = BarFactory(
            title_en=u'This is a bar',
            title_fr=u'Ceci est un bar'
        )

        url = reverse('td_cms_set_language')
        http_referer = bar.get_absolute_url()

        response = self.client.post(
            url,
            {
                'next': '/',
                'language': 'fr',
            },
            follow=True,
            HTTP_REFERER=http_referer,
        )

        expected_path = '/fr/1/ceci-est-un-bar/'
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request['PATH_INFO'], expected_path)


class CategoryDetailViewTests(TDCMSTestMixin, TestCase):
    """
    Tests for the CategoryDetailView
    """
    def setUp(self):
        self._set_category()
        self._add_pages()

    def test_get(self):
        """
        Test the CategoryDetailView get method
        """
        response = self.client.get(self.category.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['category'], self.category)

    def test_get_unknown_slug(self):
        """
        Test the CategoryDetailView get method with an unknown object
        """
        kwargs = {
            'slug_en': 'this-is-a-wrong-slug',
        }
        url = reverse('category_detail_en', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_css_styles_are_included(self):
        """
        Test TailorDev CMS css styles are loaded
        """
        response = self.client.get(self.category.get_absolute_url())

        css_link = ''.join(
            '<link rel="stylesheet" href="/static/td_cms/css/styles.css" />'
        )
        self.assertContains(response, css_link)

    def test_get_with_a_different_language_from_session(self):
        """
        Test a category detailled view display for another language
        """
        self.category.name_fr = u"Catégorie 1"
        self.category.save()

        url_fr = "/fr/categorie-1/"
        url_en = "/en/category-1/"

        response = self.client.get(url_en)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['category'], self.category)

        response = self.client.get(url_fr)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['category'], self.category)


class PageDetailViewTests(TDCMSTestMixin, TestCase):
    """
    Tests for the CategoryDetailView
    """
    def setUp(self):
        self._set_category()
        self._add_pages()

    def test_get(self):
        """
        Test the PageDetailView get method
        """
        page = Page.objects.get(id=1)
        response = self.client.get(page.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'], page)

    def test_get_unknown_slug(self):
        """
        Test the PageDetailView get method with an unknown object
        """
        kwargs = {
            'category_slug': self.category.slug,
            'slug_en': 'this-is-a-wrong-slug',
        }
        url = reverse('page_detail_en', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_css_styles_are_included(self):
        """
        Test TailorDev CMS css styles are loaded
        """
        page = Page.objects.get(id=1)
        response = self.client.get(page.get_absolute_url())

        css_link = ''.join(
            '<link rel="stylesheet" href="/static/td_cms/css/styles.css" />'
        )
        self.assertContains(response, css_link)

    def test_get_with_a_different_language_from_session(self):
        """
        Test a page detailled view display for another language
        """
        self.category.name_fr = u"Catégorie 1"
        self.category.save()

        page = self.category.page.get(slug=u'django-book-vol-1')
        page.title_fr = u"Le livre Django (vol. 1)"
        page.save()

        url_fr = "/fr/categorie-1/le-livre-django-vol-1/"
        url_en = "/en/category-1/django-book-vol-1/"

        response = self.client.get(url_en)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'], page)

        response = self.client.get(url_fr)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'], page)
