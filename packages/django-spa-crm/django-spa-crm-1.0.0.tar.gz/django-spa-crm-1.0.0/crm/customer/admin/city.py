from django.contrib import admin
from crm.customer.models import City


class CityAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    list_select_related = True
    search_fields = ["name", "state__name"]
    list_display = ["name", "state"]
    list_display_links = ["name"]
    list_filter = ["state"]
    ordering = ["name", "state"]


admin.site.register(City, CityAdmin)
