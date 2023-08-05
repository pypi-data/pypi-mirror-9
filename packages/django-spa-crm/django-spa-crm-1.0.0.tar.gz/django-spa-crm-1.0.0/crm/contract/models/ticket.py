import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Ticket(models.Model):
    customer = models.ForeignKey("customer.Customer", verbose_name=_("Customer"))
    begin = models.DateField(verbose_name=_("Start time"), default=datetime.date.today)
    end = models.DateField(verbose_name=_("Expiration day"), default=datetime.date.today)
    active = models.BooleanField(verbose_name=_("Active?"), default=True)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True)

    def get_absolute_url(self):
        return "/contract/ticket/%s/" % self.id

    @staticmethod
    def autocomplete_search_fields():
        return ["customer__last_name__icontains", "customer__ssn__iexact"]

    def __str__(self):
        return "%(customer)s" % {"customer": self.customer}

    class Meta:
        app_label = "contract"
        ordering = ["begin"]
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")
