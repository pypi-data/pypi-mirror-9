import datetime
import warnings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from crm.contract.models.contract import TYPE_RESERVATION
from crm.contract.models.contract import TYPE_PASS
from crm.contract.models.contract import TYPE_WAITING_LIST
from crm.contract.models.contract import TYPE_RESIGNATION
from crm.contract.models.contract import TYPE_CONTRACT
from crm.payment.models import Payment
from crm.contract.models import Contract
from crm.date.models import Season


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1
    classes = ["collapse"]


class ContractAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list_filter_sidebar.html"
    search_fields = ["^customer__last_name", "=uid"]
    list_display = ["season", "view_uid", "view_customer",
                    "view_comment_contract", "view_group", "view_day",
                    "view_type",  "view_last_payment", "view_comment_payment",
                    "signup_date", "resignation_date"]
    list_display_links = ["view_customer"]
    list_filter = ["season", "type", "" "group__day", "group__hour"]
    list_select_related = True
    ordering = ["season", "uid", "signup_date"]
    inlines = [PaymentInline]
    radio_fields = {"type": admin.VERTICAL}
    readonly_fields = ["id"]
    raw_id_fields = ["customer", "group"]
    autocomplete_lookup_fields = {"fk": ["customer", "group"]}
    fieldsets = [
        (None, {
            "fields": ["season", "customer", "group", "type", "comment",
                       "comment2", "signup_date", "id"]}),
        (_("Reservation"), {
            "fields": ["reservation_end_date", ],
            "classes": ["reservation-type"]}),
        (_("Resignation"), {
            "fields": ["resignation_date", ],
            "classes": ["resignation-type"]}),
        (_("Contract"), {
            "fields": ["uid", "document", "cost", "start_date", "end_date", ],
            "classes": ["contract-type"]})]

    def view_last_payment(self, contract):
        try:
            payment = Payment.objects.filter(uid=contract.id).order_by("-date")[0]
            return "{date}<br />{method}&nbsp;{amount}zł".format(date=payment.date, amount=payment.amount, method=payment.method)
        except IndexError:
            return ""
    view_last_payment.allow_tags = True
    view_last_payment.short_description = _("Last Payment")

    def changelist_view(self, request, extra_context=None):
        if "season__id__exact" not in request.GET:
            q = request.GET.copy()
            q["season__id__exact"] = Season.current().id
            request.GET = q
            request.META["QUERY_STRING"] = request.GET.urlencode()
        return super(ContractAdmin, self).changelist_view(request, extra_context=extra_context)

    def view_uid(self, contract):
        if contract.uid:
            return "<div style='text-align: center'>%s</div>" % contract.uid
        return ""
    view_uid.allow_tags = True
    view_uid.short_description = _("User ID")

    def view_customer(self, contract):
        ret = "%s %s" % (
            contract.customer.last_name,
            contract.customer.first_name)
        if contract.customer.address and contract.customer.zip_code:
            ret += "<br />(%s, %s)" % (contract.customer.address, contract.customer.zip_code.city.name)
        elif contract.customer.address:
            ret += "<br />(%s)" % contract.customer.address
        elif contract.customer.zip_code:
            ret += "<br />(%s)" % contract.customer.zip_code.city.name
        return ret
    view_customer.allow_tags = True
    view_customer.short_description = _("Customer")

    def view_comment_contract(self, contract):
        if contract.comment:
            return "<div style='color: #f00; max-width: 275px;'>%s</div>" % contract.comment
        return ""
    view_comment_contract.allow_tags = True
    view_comment_contract.short_description = _("Contract comment")

    def view_group(self, contract):
        warnings.warn("Convert to {% url %}", DeprecationWarning)
        return "<nobr><a href='/group/show/%d/'>%s</a></nobr>" % (
            contract.group.id,
            contract.group.type.short_name)
    view_group.allow_tags = True
    view_group.short_description = _("Group")

    def view_day(self, contract):
        return "<div style='text-align: center'>%s<br />%s</div>" % (
            contract.group.day,
            contract.group.hour.strftime("%H:%M"))
    view_day.short_description = _("Day")
    view_day.allow_tags = True

    def view_type(self, contract):
        warnings.warn("Simplify logic", PendingDeprecationWarning)
        if not contract.reservation_end_date:
            contract.reservation_end_date = ""

        if not contract.resignation_date:
            contract.resignation_date = ""

        if contract.type == TYPE_RESERVATION:
            if contract.reservation_end_date < datetime.date.today():
                if contract.active:
                    contract.active = False
                    contract.save()
                return _("<div class='outdated-admin'>Outdated reservation<br />%(reservation_end_date)s</div>") % {"reservation_end_date": contract.reservation_end_date}
            else:
                if not contract.active:
                    contract.active = False
                    contract.save()
                return _("<div class='reservation-admin'>Reservation<br />%(reservation_end_date)s</div>") % {"reservation_end_date": contract.reservation_end_date}

        if contract.type == TYPE_RESIGNATION:
            return _("<div class='resignation-admin'>Resignation<br />%(resignation_date)s</div>") % {"resignation_date": contract.resignation_date}

        if contract.type == TYPE_WAITING_LIST:
            return "<div class='waiting-admin'>%s</div>" % _("Waiting List")

        if contract.type == TYPE_CONTRACT:
            if contract.valid_payment_for_current_month():
                return _("<div class='contract-admin'>Contract</div>")
            else:
                return _("<div class='contract-admin-late-payment'>Contract<br />Late&nbsp;Payment</div>")

        if contract.type == TYPE_PASS:
            return _("<div class='contract-admin'>Swimming pool pass</div>")

    view_type.allow_tags = True
    view_type.short_description = _("Contract type")

    def view_comment_payment(self, contract):
        if contract.comment2:
            return "<div style='color: #f00; max-width: 275px;'>%s</div>" % (contract.comment2)
        return ""
    view_comment_payment.allow_tags = True
    view_comment_payment.short_description = _("Payment comment")

    class Media:
        js = [
            "contract/js/jquery-2.0.0.min.js",
            "contract/js/ajax.js",
            "contract/js/add-print-button.js",
            "contract/js/contract.js"]
        css = {"all": [
            "contract/css/contract.css",
            "contract/css/hide-id-field.css"]}


admin.site.register(Contract, ContractAdmin)
