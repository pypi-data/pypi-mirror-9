import datetime
from itertools import chain
import warnings
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.views.generic import TemplateView
from crm.contract.models.contract import TYPE_CONTRACT
from crm.contract.models.contract import TYPE_RESERVATION
from crm.contract.models.contract import TYPE_RESIGNATION
from crm.contract.models.contract import TYPE_WAITING_LIST
from crm.contract.models.contract import TYPE_INTERNET_SELFCARE_RESERVATION
from crm.contract.models.contract import TYPE_PASS
from crm.contract.models import Contract
from crm.payment.models import Payment
from crm.date.models import Month
from crm.date.models import Season
from crm.date.models import Weekday
from crm.group.models import Group
from crm.group.models import Pool
from crm.group.models import Entry


class ShowView(TemplateView):
    template_name = "group/show.html"

    def clean(contracts):
        today = datetime.date.today()
        for contract in contracts.filter(reservation_end_date__lt=today):
            contract.active = False
            contract.save()

    def get_context_data(self, gid, **kwargs):
        warnings.warn("This class is not finished", DeprecationWarning)
        group = Group.get(gid)
        contracts = Group.contracts()
        self.clean(contracts)
        inactive = Group.contracts(active=False).order_by("reservation_end_date", "resignation_date")
        contracts = contracts.filter(type=TYPE_CONTRACT).order_by("uid")
        not_contracts = contracts.exclude(type=TYPE_CONTRACT).order_by("type", "reservation_end_date", "resignation_date")
        active = list(chain(contracts, not_contracts))
        return {
            "tickets": tickets,
            "group": group,
            "contracts_active": contracts_active,
            "contracts_inactive": contracts_inactive,
            "w": w,
            "i": i,
            "p": p,
            "r": r,
            "c": c,
            "rg": rg,
            "contracts": contracts,
            "not_contracts": not_contracts}


@login_required
def show(request, gid):
    warnings.warn("Rewrite to class based views", PendingDeprecationWarning)
    warnings.warn("Split in separe methods")
    today = datetime.date.today()
    group = get_object_or_404(Group, id=gid)
    make_clean = Contract.objects.filter(group__id=gid, reservation_end_date__lt=datetime.date.today(), active=True)
    for m in make_clean:
        m.active = False
        m.save()
    contracts_inactive = Contract.objects.filter(group__id=gid, active=False).order_by("reservation_end_date", "resignation_date")
    contracts = Contract.objects.filter(group__id=gid, active=True, type=TYPE_CONTRACT).order_by("uid")
    not_contracts = Contract.objects.filter(group__id=gid, active=True).exclude(type=TYPE_CONTRACT).order_by("type", "reservation_end_date", "resignation_date")
    contracts_active = list(chain(contracts, not_contracts))
    for c in contracts_active:
        c.payment_past = Payment.objects.filter(uid=c.id, month=Month.previous()).aggregate(Sum("amount"))["amount__sum"]
        c.payment_present = Payment.objects.filter(uid=c.id, month=Month.current()).aggregate(Sum("amount"))["amount__sum"]
        c.payment_future = Payment.objects.filter(uid=c.id, month=Month.next()).aggregate(Sum("amount"))["amount__sum"]
        c.payment_wpisowe = Payment.objects.filter(uid=c.id, month__name="Wpisowe").aggregate(Sum("amount"))["amount__sum"]
        if not c.payment_future:
            c.payment_future = ""
        if not c.payment_present:
            c.payment_present = ""
        if not c.payment_past:
            c.payment_past = ""
    for c in contracts_inactive:
        c.payment_past = Payment.objects.filter(uid=c.id, month=Month.previous()).aggregate(Sum("amount"))["amount__sum"]
        c.payment_present = Payment.objects.filter(uid=c.id, month=Month.current()).aggregate(Sum("amount"))["amount__sum"]
        c.payment_future = Payment.objects.filter(uid=c.id, month=Month.next()).aggregate(Sum("amount"))["amount__sum"]
        if not c.payment_future:
            c.payment_future = ""
        if not c.payment_present:
            c.payment_present = ""
        if not c.payment_past:
            c.payment_past = ""
    c = Contract.objects.filter(group=group, type=TYPE_CONTRACT).count()
    r = Contract.objects.filter(group=group, type=TYPE_RESERVATION).count()
    rg = Contract.objects.filter(group=group, type=TYPE_RESIGNATION).count()
    w = Contract.objects.filter(group=group, type=TYPE_WAITING_LIST).count()
    i = Contract.objects.filter(group=group, type=TYPE_INTERNET_SELFCARE_RESERVATION).count()
    p = Contract.objects.filter(group=group, type=TYPE_PASS).count()
    tickets = Entry.objects.filter(time=group.hour, date__gte=today).order_by("ticket__begin", "ticket__id")
    p = tickets.count()
    return render_to_response("group/show.html", {
        "tickets": tickets,
        "group": group,
        "contracts_active": contracts_active,
        "contracts_inactive": contracts_inactive,
        "w": w,
        "i": i,
        "p": p,
        "r": r,
        "c": c,
        "rg": rg,
        "contracts": contracts,
        "not_contracts": not_contracts})


class TimetableView(TemplateView):
    template_name = "group/timetable.html"

    def set_group_information(self, group):
        if group.season == Season.current():
            group.passes = Entry.count(weekday=group.day.order, time=group.hour)
        else:
            group.passes = 0
        group.contract = group.count(TYPE_CONTRACT)
        group.reservation = group.count(TYPE_RESERVATION)
        group.reservation += group.count(TYPE_WAITING_LIST)
        group.sum = group.passes + group.contract + group.reservation
        group.max = group.type.capacity
        return group

    def get_context_data(self, season=None, type=None, **kwargs):
        if not season:
            season = Season.current().name
        season = Season.objects.get(name=season)
        groups = Group.objects.filter(disabled=False, season=season)
        week = Weekday.objects.all()
        pools = Pool.objects.all()
        if type:
            groups = groups.filter(type__id=type)
        hours = Group.hours(groups)
        for event in hours:
            event["pool"] = Pool.objects.get(id=event["pool"])
        for group in groups:
            self.set_group_information(group)
        return {"season": season, "groups": groups, "weekday": week, "hours": hours, "pools": pools}


class TimetableViewNextSeason(TimetableView):
    def get_context_data(self, season=None, type=None, **kwargs):
        season = Season.next().name
        return super(TimetableViewNextSeason, self).get_context_data(season, **kwargs)


timetable = TimetableView.as_view()
timetable_next_season = TimetableViewNextSeason.as_view()
