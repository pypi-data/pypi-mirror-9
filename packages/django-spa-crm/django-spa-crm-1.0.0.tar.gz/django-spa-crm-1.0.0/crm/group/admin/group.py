import warnings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from crm.contract.models import Contract
from crm.date.models import Season
from crm.group.models import Group


class ContractInline(admin.TabularInline):
    model = Contract
    max_num = 15
    extra = 1


class GroupAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    search_fields = ["=gid", "^type__short_name"]
    list_display = ["season", "day", "view_hour", "view_capacity", "pool",
                    "view_type", "cost", "discount", "view_comment",
                    "instructor"]
    list_display_links = ["view_capacity"]
    list_filter = ["season", "pool", "type", "day", "hour", "instructor", "cost", "discount"]
    list_select_related = True
    ordering = ["hour"]

    def changelist_view(self, request, extra_context=None):
        if "season__id__exact" not in request.GET:
            q = request.GET.copy()
            q["season__id__exact"] = Season.current().id
            request.GET = q
            request.META["QUERY_STRING"] = request.GET.urlencode()
        return super(GroupAdmin, self).changelist_view(request, extra_context=extra_context)

    def view_capacity(self, group):
        return group.summary()
    view_capacity.short_description = _("Capacity")

    def view_hour(self, group):
        return group.hour.strftime("%H:%M")
    view_hour.short_description = _("Hour")

    def view_comment(self, group):
        if not group.comment:
            return ""
        return "<div style='color: #f00; max-width: 275px;'>%s</div>" % group.comment
    view_comment.allow_tags = True
    view_comment.short_description = _("Comment")

    def view_type(self, group):
        if not group.type:
            return ""
        warnings.warn("Convert to {% url %}", DeprecationWarning)
        return "<a href='/group/show/%s/'>%s</a>" % (group.id, group.type)
    view_type.allow_tags = True
    view_type.short_description = _("Type")


admin.site.register(Group, GroupAdmin)
