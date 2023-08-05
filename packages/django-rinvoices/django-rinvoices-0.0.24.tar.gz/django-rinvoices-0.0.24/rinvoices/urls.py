# -*- coding: utf-8 -*-

from django.conf.urls.defaults import *
from rinvoices.views import InvoiceDetailView, PDFInvoiceDetailView, BudgetPDFInvoiceDetailView, BudgetInvoiceDetailView
from wkhtmltopdf.views import PDFTemplateView

# Llamamos al registro a traves del formulario RegisterForm que hemos creado
urlpatterns = patterns('',
    # url(r'^PDF/(?P<id>[-\w/]+)/$', PDFTemplateView.as_view(template_name='rinvoices/default.html',
    #                                       filename='invoice.pdf'), name='pdf'),

    url(r'^txtPDF/(?P<id>[-\w/]+)/$', InvoiceDetailView.as_view()),
    url(r'^txtPDF/(?P<id>[-\w/]+)/(?P<lang>[-\w/]+)$', InvoiceDetailView.as_view()),
    url(r'^PDF/(?P<id>[-\w/]+)/$', PDFInvoiceDetailView.as_view()),
    url(r'^PDF/(?P<id>[-\w/]+)/(?P<lang>[-\w/]+)$', PDFInvoiceDetailView.as_view()),

    url(r'^budget_txtPDF/(?P<id>[-\w/]+)/$', BudgetInvoiceDetailView.as_view()),
    url(r'^budget_txtPDF/(?P<id>[-\w/]+)/(?P<lang>[-\w/]+)$', BudgetInvoiceDetailView.as_view()),
    url(r'^budget_PDF/(?P<id>[-\w/]+)/$', BudgetPDFInvoiceDetailView.as_view()),
    url(r'^budget_PDF/(?P<id>[-\w/]+)/(?P<lang>[-\w/]+)$', BudgetPDFInvoiceDetailView.as_view()),

)
