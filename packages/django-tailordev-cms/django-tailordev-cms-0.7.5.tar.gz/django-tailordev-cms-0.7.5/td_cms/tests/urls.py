# -*- coding: utf-8 -*-
"""
Urls for testing purpose
"""
from django.conf.urls import include, patterns, url
from modeltranslation.settings import AVAILABLE_LANGUAGES

from .views import NotCMSTestView, RootTestView, BarDetailView


urlpatterns = patterns(
    '',

    # Test views
    url(r'^$',
        RootTestView.as_view(),
        name='root_view'),

    url(r'^this/is/a/testing_pattern/',
        NotCMSTestView.as_view(),
        name='not_cms_test_view'),
)

# Define translated urls for Page-derived objects detail view
for language_code in AVAILABLE_LANGUAGES:
    # All urls are prefixed by the language code for translated slugs
    # resolution
    base_url = r'^%s/' % language_code

    urlpatterns += patterns('',

        url(base_url + r'(?P<pk>\d+)/(?P<slug_%s>[-\w]+)/$' % language_code,
            BarDetailView.as_view(),
            name='bar_detail_%s' % language_code),
    )

# TD_CMS views
urlpatterns += patterns('',
    url(r'', include('td_cms.urls')),
)
