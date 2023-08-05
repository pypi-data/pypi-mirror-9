from django.contrib import admin
from crm.contract.models import Addendum
from crm.date.models import Season


class AddendumAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    list_select_related = True
    search_fields = ["^contract__customer__last_name", "=contract__uid"]
    list_display = ["season", "contract", "document", "type", "group",
                    "gid_to", "comment"]
    list_display_links = ["contract"]
    list_filter = ["season", "type", "document"]
    radio_fields = {"type": admin.VERTICAL}
    raw_id_fields = ["contract", "group", "gid_to"]
    autocomplete_lookup_fields = {"fk": ["contract", "group", "gid_to"]}

    def changelist_view(self, request, extra_context=None):
        if "season__id__exact" not in request.GET:
            q = request.GET.copy()
            q["season__id__exact"] = Season.current().id
            request.GET = q
            request.META["QUERY_STRING"] = request.GET.urlencode()
        return super(AddendumAdmin, self).changelist_view(request, extra_context=extra_context)

    class Media:
        js = [
            "contract/js/addendum.js",
            "contract/js/ajax.js"]
        css = {"all": [
            "contract/css/contract.css"]}


admin.site.register(Addendum, AddendumAdmin)
