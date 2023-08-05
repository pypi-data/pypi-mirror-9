from django.contrib import admin
from crm.group.models import Pool


class PoolAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    list_select_related = True
    list_display = ["name", "capacity"]
    list_display_links = ["name"]
    list_filter = ["capacity"]
    ordering = ["name"]


admin.site.register(Pool, PoolAdmin)
