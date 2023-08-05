from django.contrib import admin
from crm.customer.models import State


class StateAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    list_select_related = True
    search_fields = ["name", "country"]
    list_display = ["name", "country"]
    list_display_links = ["name"]
    list_filter = ["country"]


admin.site.register(State, StateAdmin)
