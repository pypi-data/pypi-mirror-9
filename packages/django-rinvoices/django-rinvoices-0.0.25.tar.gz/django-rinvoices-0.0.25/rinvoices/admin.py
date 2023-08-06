# -*- coding: utf-8 -*-

from django.contrib import admin
import models as mymodels


class LinesInline(admin.TabularInline):
    model = mymodels.Line


class AdminInvoices(admin.ModelAdmin):

    list_display = ('customer', 'invoice_number', 'date', 'taxes',
                    'retentions', 'total', 'currency', 'registered', 'sent',
                    'charged', 'get_PDF')
    inlines = [LinesInline, ]
    ordering = ('-date',)

    """
    Para agregar TinyMCE en los newforms-admin:
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor#Withnewforms-admin
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor
    """

    class Media:
        js = ('js/tiny_mce/tiny_mce.js',
              'js/textareas.js',
              # https://docs.djangoproject.com/en/1.4/howto/static-files/
              'js/invoices.js',
              )

    def get_PDF(self, obj):
        return '<a href="/rinvoices/PDF/%s/es">PDFes</a>, \
                <a href="/rinvoices/PDF/%s/en">PDFen</a>, \
                <a href="/rinvoices/txtPDF/%s/es">TXTes</a>, \
                <a href="/rinvoices/txtPDF/%s/en">TXTen</a>' % (str(obj.id),
                                                                str(obj.id),
                                                                str(obj.id),
                                                                str(obj.id))
    get_PDF.allow_tags = True

    # def save_model(self, request, obj, form, change):
    #     obj.save()
    #     lines = mymodels.Line.objects.all().filter(invoice=obj)
    #     subtotal = 0
    #     subtotal_iva = 0
    #     for line in lines:
    #         subtotal = float(subtotal) + float(line.amount)
    #     obj.subtotal = subtotal
    #     obj.subtotal_iva = obj.subtotal * float(obj.taxes.value)
    #     obj.subtotal_retentions = obj.subtotal * float(obj.retentions.value) * -1
    #     obj.total = obj.subtotal + obj.subtotal_iva + obj.subtotal_retentions
    #     obj.save()


class BudgetLinesInline(admin.TabularInline):
    model = mymodels.BudgetLine


class AdminBudgets(admin.ModelAdmin):

    list_display = ('customer', 'header', 'date', 'total', 'currency', 'get_PDF2')
    inlines = [ BudgetLinesInline, ]
    ordering = ('-date',)

    """
    Para agregar TinyMCE en los newforms-admin:
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor#Withnewforms-admin
    - http://code.djangoproject.com/wiki/AddWYSIWYGEditor
    """

    class Media:
        js = ('js/tiny_mce/tiny_mce.js',
              'js/textareas.js',
              )

    def get_PDF2(self, obj):
        return '<a href="/rinvoices/budget_PDF/%s/es">PDFes</a>, <a href="/rinvoices/budget_PDF/%s/en">PDFen</a>, <a href="/rinvoices/budget_txtPDF/%s/es">TXTes</a>, <a href="/rinvoices/budget_txtPDF/%s/en">TXTen</a>' % (str(obj.id), str(obj.id), str(obj.id), str(obj.id))
    get_PDF2.allow_tags = True

    def save_model(self, request, obj, form, change):
        obj.save()


class AdminReceivedInvoices(admin.ModelAdmin):

    list_display = ('provider', 'reference', 'title', 'description', 'date', 'total', 'paid', 'registered')
    list_filter = ('provider', 'date', 'paid', 'registered')
    ordering = ('-date',)

admin.site.register(mymodels.Invoice, AdminInvoices)
admin.site.register(mymodels.InvoiceReceive, AdminReceivedInvoices)
admin.site.register(mymodels.Header)
admin.site.register(mymodels.Customer)
admin.site.register(mymodels.Provider)
admin.site.register(mymodels.Tax)
admin.site.register(mymodels.Retention)
admin.site.register(mymodels.QuantityUnit)
admin.site.register(mymodels.Currency)
admin.site.register(mymodels.Budget, AdminBudgets)
