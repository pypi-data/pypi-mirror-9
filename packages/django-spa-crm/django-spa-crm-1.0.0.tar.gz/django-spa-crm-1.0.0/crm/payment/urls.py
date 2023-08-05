from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib.auth.decorators import permission_required
from crm.payment.views import ReportListView
from crm.payment.views import DateRangeReport
from crm.payment.views import MissingPaymentsView
from crm.payment.views import MonthlyStatementView


urlpatterns = patterns(
    "",
    url(r"report/$",
        permission_required("payment.change_payment")(ReportListView.as_view()),
        name="report"),

    url(r"report/date-range/$",
        permission_required("payment.change_payment")(DateRangeReport.as_view()),
        name="report-date-range"),

    url(r"report/monthly-statement/$",
        permission_required("payment.change_payment")(MonthlyStatementView.as_view()),
        name="report-monthly-statement"),

    url(r"report/missing/$",
        permission_required("payment.change_payment")(MissingPaymentsView.as_view()),
        name="report-missing"),
)
