# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.utils.translation import check_for_language, activate
from django.conf import settings as conf

import models as mymodels

from django.views.generic import DetailView
from wkhtmltopdf.views import PDFTemplateView


def changelang(request, code):
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = HttpResponseRedirect(next)
    lang_code = code
    if lang_code and check_for_language(lang_code):
        activate(lang_code)
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
        else:
            response.set_cookie(conf.LANGUAGE_COOKIE_NAME, lang_code)
    return response


class PDFInvoiceDetailView(PDFTemplateView):

    # filename = 'my_pdf.pdf'
    template_name = "rinvoices/default.html"
    context_object_name = "myinvoice"

    def __init__(self):
        pass

    def get_context_data(self, **kwargs):
        lang = self.kwargs.get('lang', 'es')
        changelang(self.request, lang)
        myinvoice = get_object_or_404(mymodels.Invoice, id=self.kwargs['id'])
        dateinvoice = myinvoice.date.strftime('%b%y').lower()
        self.filename = '%s-%s_%s_%s.pdf' % (myinvoice.invoice_number,
                                             myinvoice.header.slug,
                                             myinvoice.customer.slug,
                                             dateinvoice)
        return {'myinvoice': myinvoice}


class InvoiceDetailView(DetailView):

    template_name = "rinvoices/default.html"
    context_object_name = "myinvoice"

    def __init__(self):
        pass

    def get_object(self):
        lang = self.kwargs.get('lang', 'es')
        changelang(self.request, lang)
        myinvoice = get_object_or_404(mymodels.Invoice, id=self.kwargs['id'])
        return myinvoice


class BudgetPDFInvoiceDetailView(PDFTemplateView):

    # filename = 'my_pdf.pdf'
    template_name = "rinvoices/budget.html"
    context_object_name = "myinvoice"

    def __init__(self):
        pass

    def get_context_data(self, **kwargs):
        lang = self.kwargs.get('lang', 'es')
        changelang(self.request, lang)
        myinvoice = get_object_or_404(mymodels.Budget, id=self.kwargs['id'])
        return {'myinvoice': myinvoice}


class BudgetInvoiceDetailView(DetailView):

    template_name = "rinvoices/budget.html"
    context_object_name = "myinvoice"

    def __init__(self):
        pass

    def get_object(self):
        lang = self.kwargs.get('lang', 'es')
        changelang(self.request, lang)
        myinvoice = get_object_or_404(mymodels.Budget, id=self.kwargs['id'])
        return myinvoice
