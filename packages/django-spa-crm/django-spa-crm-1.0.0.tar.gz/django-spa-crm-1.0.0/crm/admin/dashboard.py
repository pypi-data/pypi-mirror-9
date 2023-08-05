from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from grappelli.dashboard import Dashboard
from grappelli.dashboard import modules


class CRMIndexDashboard(Dashboard):
    def init_with_context(self, context):

        self.children.append(modules.ModelList(
            title=_("Contracts"),
            column=1,
            collapsible=False,
            models=["crm.contract.*"]))

        self.children.append(modules.ModelList(
            title=_("Customers"),
            column=1,
            collapsible=False,
            models=["crm.customer.*"]))

        self.children.append(modules.ModelList(
            title=_("Dates"),
            column=1,
            collapsible=False,
            models=["crm.date.*"]))

        self.children.append(modules.ModelList(
            title=_("Groups"),
            column=1,
            collapsible=False,
            models=["crm.group.*"]))

        if context["user"].has_perm("admin.add_user"):
            self.children.append(modules.ModelList(
                title=_("Administration"),
                column=2,
                collapsible=True,
                models=["django.contrib.*"],
                css_classes=["grp-closed"]))

        self.children.append(modules.RecentActions(
            title=_("Recent Actions"),
            limit=5,
            collapsible=True,
            column=2,
            css_classes=["grp-closed"]))

        self.children.append(modules.LinkList(
            title=_("Shortcuts"),
            collapsible=False,
            column=2,
            children=[
                {"title": _("Timetable Current Season"),
                 "url": reverse("group:timetable-current-season")},
                {"title": _("Timetable Next Season"),
                 "url": reverse("group:timetable-next-season")},
                {"title": _("Payment Reports"),
                 "url": reverse("payment:report")}]))

        if context["user"].has_perm("payment.view_payment"):
            self.children.append(modules.ModelList(
                title=_("Payments"),
                column=1,
                collapsible=False,
                models=["crm.payment.*"]))
