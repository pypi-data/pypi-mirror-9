from django.contrib import admin
from crm.contract.models import Ticket
from crm.group.models import Entry


class EntryInline(admin.TabularInline):
    model = Entry
    extra = 1
    classes = ["collapse"]


class TicketAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    list_select_related = True
    list_filter = ["begin", "end"]
    search_fields = ["customer__last_name"]
    list_display = ["customer", "begin", "end", "comment"]
    list_display_links = ["customer"]
    inlines = [EntryInline]
    readonly_fields = ["id"]
    raw_id_fields = ["customer"]
    autocomplete_lookup_fields = {"fk": ["customer"]}

    class Media:
        js = [
            "contract/js/jquery-2.0.0.min.js",
            "contract/js/add-entrylist-button.js"]
        css = {"all": [
            "contract/css/hide-id-field.css",
            "contract/css/contract.css"]}


admin.site.register(Ticket, TicketAdmin)
