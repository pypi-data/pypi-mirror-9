import datetime
from django.db.models import Sum
from django.views.generic import TemplateView
from crm.payment.models import Payment
from crm.payment.models import Method
from crm.date.models import Season
from crm.date.models import Month
from crm.contract.models.contract import TYPE_CONTRACT
from crm.contract.models import Contract


class ReportListView(TemplateView):
    template_name = "payment/report-index.html"

    def get_context_data(self, **kwargs):
        seasons = Season.objects.all()
        months = Month.objects.all()
        return {'seasons': seasons, 'months': months}


class DateRangeReport(TemplateView):
    template_name = "payment/report-view.html"

    def get_context_data(self, **kwargs):
        start = self.request.GET["start"]
        end = self.request.GET["end"]
        payments = Payment.objects.filter(date__range=(start, end), amount__gt=0).order_by("date")
        methods = Method.objects.all()

        for method in methods:
            method.sum = payments.filter(method=method).aggregate(Sum('amount'))['amount__sum']
            method.count = payments.filter(method=method).count()

        return {
            "date_start": start,
            "date_end": end,
            "count": payments.count(),
            "sum": payments.aggregate(Sum('amount'))['amount__sum'],
            "methods": methods,
            "payments": payments}


class MonthlyStatementView(TemplateView):
    template_name = "payment/report-view.html"

    def get_context_data(self, **kwargs):
        season = Season.objects.get(name=self.request.GET["season"])
        month = Month.objects.get(id=self.request.GET["month"])
        payments = Payment.objects.filter(uid__season=season, month=month, amount__gt=0).order_by("date")
        methods = Method.objects.all()

        for method in methods:
            method.sum = payments.filter(method=method).aggregate(Sum('amount'))['amount__sum']
            method.count = payments.filter(method=method).count()

        return {
            "date_start": datetime.date(2013, month.id, 1),
            "date_end": datetime.date(2013, month.id, 30),
            "count": payments.count(),
            "sum": payments.aggregate(Sum('amount'))['amount__sum'],
            "methods": methods,
            "payments": payments}


class MissingPaymentsView(TemplateView):
    template_name = "payment/missing-payments.html"

    def get_context_data(self, **kwargs):
        season = Season.objects.get(name=self.request.GET["season"])
        month = Month.objects.get(id=self.request.GET["month"])
        today = datetime.date.today()
        active_contracts = Contract.objects.filter(season=season, active=True, type=TYPE_CONTRACT, start_date__lte=today)
        payments = Payment.objects.filter(month=month, amount__gt=0)
        missing_payments = []
        total = 0

        for contract in active_contracts:
            contract.already_paid = payments.filter(uid=contract).aggregate(Sum('amount'))['amount__sum'] or 0
            contract.ballance = contract.group.cost - contract.already_paid
            if contract.ballance:
                missing_payments.append(contract)
                total += contract.ballance

        return {
            "season": season,
            "month": month,
            "payments": missing_payments,
            "total": total}
