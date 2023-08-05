from django.contrib import admin
from crm.group.models import Entry


class EntryAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    search_fields = ["=id", "^ticket__customer__last_name", "=date"]
    list_display = ["ticket", "date", "time", "was_present"]
    list_display_links = ["ticket"]
    list_filter = ["was_present", "date", "time"]
    list_select_related = True
    raw_id_fields = ["ticket"]
    autocomplete_lookup_fields = {"fk": ["ticket"]}

    class Media:
        js = [
            "group/js/jquery-2.0.0.js",
            "group/js/ajax.js"]
        css = {"all": [
            "crm/css/contract.css"]}


admin.site.register(Entry, EntryAdmin)
