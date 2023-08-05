from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from crm.payment.models import Payment
from crm.payment.models import Method


class MethodAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    list_select_related = True
    list_display = ["name", "comment"]
    list_display_links = ["name"]
    ordering = ["name"]


class PaymentAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    search_fields = ["=uid__uid", "^uid__customer__last_name",
                     "=uid__customer__ssn", "=date"]
    list_select_related = True
    list_display = ["view_uid", "month", "amount", "date", "method", "comment"]
    list_display_links = ["date"]
    list_filter = ["date", "method", "month", "accountant", "amount"]
    ordering = ["uid", "month", "date"]
    readonly_fields = ["uid"]

    def view_uid(self, payment):
        return "<a href='/contract/contract/%s/'>%s</a>" % (
            payment.uid.id,
            payment.uid)
    view_uid.allow_tags = True
    view_uid.short_description = _("Customer")


admin.site.register(Method, MethodAdmin)
admin.site.register(Payment, PaymentAdmin)
