from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from crm.customer.models import Customer


class CustomerAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    list_select_related = True
    search_fields = ["=id", "^last_name", "=ssn", "^address",
                     "=zip_code__zip_code"]
    list_display = ["last_name", "first_name", "view_ssn", "view_phone", "address",
                    "zip_code"]
    list_display_links = ["last_name", "first_name"]
    raw_id_fields = ["zip_code"]
    autocomplete_lookup_fields = {"fk": ["zip_code"]}

    def view_ssn(self, customer):
        if not customer.ssn:
            return ""
        return customer.ssn
    view_ssn.allow_tags = False
    view_ssn.short_description = _("SSN")

    def view_phone(self, customer):
        try:
            return " ".join([customer.phone[0:3], customer.phone[3:6], customer.phone[6:9]])
        except IndexError:
            return ""
    view_phone.allow_tags = False
    view_phone.short_description = _("Phone")

    class Media:
        css = {"all": ["customer/css/customer.css"]}


admin.site.register(Customer, CustomerAdmin)
