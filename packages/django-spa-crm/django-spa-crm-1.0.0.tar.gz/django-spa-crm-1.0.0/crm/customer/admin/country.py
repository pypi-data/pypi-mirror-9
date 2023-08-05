from django.contrib import admin
from crm.customer.models import Country


class CountryAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    list_select_related = True
    search_fields = ["name", "iso_alpha_2", "iso_alpha_3"]
    list_display = ["continent", "name", "iso_alpha_2", "iso_alpha_3"]
    list_display_links = ["name"]
    list_filter = ["continent"]


admin.site.register(Country, CountryAdmin)
