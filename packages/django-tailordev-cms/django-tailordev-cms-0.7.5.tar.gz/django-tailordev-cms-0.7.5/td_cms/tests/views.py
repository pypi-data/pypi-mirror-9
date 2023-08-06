# -*- coding: utf-8 -*-
from django.views.generic import DetailView, TemplateView

from . import Bar


class NotCMSTestView(TemplateView):
    """
    A simple view used for testing purpose
    """
    template_name = '_layouts/base.html'


class RootTestView(TemplateView):
    """
    A root view for testing purpose
    """
    template_name = '_layouts/base.html'


class BarDetailView(DetailView):
    """
    A Page-derived model detail view
    """
    model = Bar
    template_name = 'td_cms/page_detail.html'
