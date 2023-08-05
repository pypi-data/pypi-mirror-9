from django.contrib import admin
from crm.date.models import Month
from crm.date.models import Season
from crm.date.models import Weekday


class SeasonAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    list_select_related = True
    search_fields = ["name"]
    list_display = ["name", "start", "end", "subscription_start"]
    list_display_links = ["name"]


admin.site.register(Month)
admin.site.register(Season, SeasonAdmin)
admin.site.register(Weekday)
