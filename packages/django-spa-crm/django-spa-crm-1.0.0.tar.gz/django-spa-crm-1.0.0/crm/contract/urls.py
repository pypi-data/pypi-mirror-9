from django.conf.urls import patterns
from django.conf.urls import url
from crm.contract.views import ContractPrintView
from crm.contract.views import AddendumPrintView
from crm.contract.views import SamplePrintView


urlpatterns = patterns(
    "",
    url(r"print/addendum/(?P<document_id>\d+)/$", AddendumPrintView.as_view(), name="print-addendum"),
    url(r"print/contract/(?P<user_id>\d+)/$", ContractPrintView.as_view(), name="print-contract"),
    url(r"print/sample/(?P<document_id>\d+)/$", SamplePrintView.as_view(), name="print-sample"),
)
