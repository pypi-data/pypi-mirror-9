import logging
import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _


logger = logging.getLogger("crm.payment")


class Method(models.Model):
    name = models.CharField(unique=True, max_length=50, verbose_name=_("Name"))
    need_verification = models.BooleanField(verbose_name=_("Need verification?"), default=False)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "payment"
        ordering = ["name"]
        verbose_name = _("Method")
        verbose_name_plural = _("Methods")


class Payment(models.Model):
    uid = models.ForeignKey("contract.Contract", verbose_name=_("Contract"))
    month = models.ForeignKey("date.Month", verbose_name=_("Month"), default=13)
    amount = models.IntegerField(verbose_name=_("Amount"), default=0)
    date = models.DateField(verbose_name=_("Date"), default=datetime.date.today)
    date_added = models.DateTimeField(default=datetime.datetime.now, verbose_name=_("Date"), editable=False)
    accountant = models.ForeignKey("auth.User", default=1, verbose_name=_("Accountant"), null=True, blank=True, unique=False, editable=False)
    method = models.ForeignKey("payment.Method", verbose_name=_("Payment Method"), default=1)
    comment = models.CharField(verbose_name=_("Comment"), unique=False, null=True, blank=True, max_length=255)

    def save(self, *args, **kwargs):
        if self.amount <= 0:
            logger.warning("Cannot have payments less or equal to zero")
            return None
        super(Payment, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return "/payment/payment/%s/" % self.id

    def __str__(self):
        return "%s, %s, %s, %s" % (self.date, self.amount, self.method, self.uid)

    class Meta:
        app_label = "payment"
        ordering = ["month"]
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")
