from django.contrib import admin
from crm.group.models import Type


class TypeAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    search_fields = ["^short_name", "^category__name", "^variant__name"]
    list_display = ["category", "short_name", "full_name"]
    list_display_links = ["short_name"]
    list_filter = ["category"]
    list_select_related = True
    ordering = ["short_name"]


admin.site.register(Type, TypeAdmin)
