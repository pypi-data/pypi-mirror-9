from django.contrib import admin
from crm.customer.models import ZipCode


class ZipCodeAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    list_select_related = True
    search_fields = ["zip_code", "city__name"]
    list_display = ["zip_code", "city"]
    list_display_links = ["zip_code"]
    list_filter = ["city"]
    ordering = ["city", "zip_code"]
    raw_id_fields = ["city"]
    autocomplete_lookup_fields = {"fk": ["city"]}

    class Media:
        css = {"all": ["customer/css/zipcode.css"]}


admin.site.register(ZipCode, ZipCodeAdmin)
