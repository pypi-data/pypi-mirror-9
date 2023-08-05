from django.conf.urls import include
from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns(
    "",
    url(r"^group/", include("crm.group.urls", namespace="group")),
    url(r"^contract/", include("crm.contract.urls", namespace="contract")),
    url(r"^payment/", include("crm.payment.urls", namespace="payment")),
    url(r"^grappelli/", include("grappelli.urls")),
    url(r"", include(admin.site.urls)),
)
