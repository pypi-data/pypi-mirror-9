import datetime
import logging
import warnings
from django.db import models
from django.db.models import Max
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from crm.date.models import Month
from crm.date.models import Season
from crm.payment.models import Payment


log = logging.getLogger("crm.models.contract")

warnings.warn("Hide defaults inside the model", PendingDeprecationWarning)
DEFAULT_COST = 0
DEFAULT_TYPE = 1
DEFAULT_UID = ""
DEFAULT_FULL_YEAR = False
DEFAULT_DOCUMENT = 2
DEFAULT_ACTIVE = True
TYPE_RESERVATION = 1
TYPE_CONTRACT = 2
TYPE_RESIGNATION = 3
TYPE_WAITING_LIST = 4
TYPE_PASS = 5
TYPE_INTERNET_SELFCARE_RESERVATION = 6
TYPE_CHOICES = [
    (1, _("Reservation")),
    (2, _("Contract")),
    (3, _("Resignation")),
    (4, _("Waiting List")),
    (5, _("Swimming pool pass"))]


class Contract(models.Model):
    season = models.ForeignKey("date.Season", verbose_name=_("Season"), default=Season.current().id)
    accountant = models.ForeignKey("auth.User", default=1, verbose_name=_("Accountant"), editable=False)
    customer = models.ForeignKey("customer.Customer", verbose_name=_("Customer"))
    group = models.ForeignKey("group.Group", verbose_name=_("Group"))
    active = models.BooleanField(verbose_name=_("Contract Active?"), default=DEFAULT_ACTIVE)
    need_verification = models.BooleanField(verbose_name=_("Need verification?"), default=False)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, verbose_name=_("Contract type"), default=DEFAULT_TYPE)
    comment = models.TextField(verbose_name=_("Contract comment"), unique=False, null=True, blank=True)
    comment2 = models.TextField(verbose_name=_("Payment comment"), unique=False, null=True, blank=True)
    reservation_end_date = models.DateField(null=True, blank=True, default=Season.current().end, verbose_name=_("Reservation end"), help_text=_("Leave blank to auto assign automatic value"))
    resignation_date = models.DateField(null=True, blank=True, default=datetime.date.today, verbose_name=_("Resignation date"), help_text=_("Leave blank to auto assign automatic value"))
    uid = models.IntegerField(default=DEFAULT_UID, help_text=_("Leave blank for auto assign with next possible value"), null=True, blank=True, verbose_name=_("User ID"))
    document = models.ForeignKey("contract.Document", null=True, blank=True, default=DEFAULT_DOCUMENT, verbose_name=_("Contract Document"))
    cost = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True, verbose_name=_("Group cost"), default=DEFAULT_COST, help_text=_("use . (Dot) for separating decimal values"))
    full_year = models.BooleanField(default=DEFAULT_FULL_YEAR, verbose_name=_("Full year"))
    signup_date = models.DateField(null=True, blank=True, default=datetime.date.today, verbose_name=_("Signup date"))
    start_date = models.DateField(null=True, blank=True, default=Season.current().start, verbose_name=_("Contract start date"))
    end_date = models.DateField(null=True, blank=True, default=Season.current().end, verbose_name=_("Contract end date"))

    @staticmethod
    def autocomplete_search_fields():
        return ["customer__last_name__icontains"]

    def is_outdated(self):
        if not self.active:
            return True

        if self.type == TYPE_RESERVATION:
            outdated = self.reservation_end_date < datetime.date.today()
            if outdated and self.active:
                self.active = False
                self.save()
                return True
            if self.type == TYPE_RESERVATION:
                return outdated

        if self.type == TYPE_RESIGNATION:
            outdated = self.resignation_date < datetime.date.today()
            if outdated and self.active:
                self.active = False
                self.save()
                return True
            if self.type == TYPE_RESIGNATION:
                return outdated

        return False

    def valid_payment_for_current_month(self):
        sum = Payment.objects.filter(uid=self.id, month=Month.current()).aggregate(Sum("amount"))
        if not sum["amount__sum"] or self.cost > sum["amount__sum"]:
            return False
        return True

    def get_absolute_url(self):
        return "/contract/contract/%s/" % self.id

    def __str__(self):
        return "%d - %s %s (%s) - %s %.5s" % (
            self.uid,
            self.customer.last_name,
            self.customer.first_name,
            self.group.type,
            self.group.day,
            self.group.hour)

    def save(self, *args, **kwargs):
        import warnings
        warnings.warn("Cleanup this mess", PendingDeprecationWarning)

        from pprint import pformat
        log.debug("Object '{obj}' saving with data: \n{data}".format(
            obj=self,
            data=pformat(vars(self))))

        if not self.cost:
            self.cost = 0
        if self.type == TYPE_INTERNET_SELFCARE_RESERVATION:
            self.active = True
            self.reservation_end_date = Season.current().subscription_start
            self.uid = 0
        elif self.type == TYPE_PASS:
            self.active = True
            self.reservation_end_date = Season.current().subscription_start
            self.uid = 0
        elif self.type == TYPE_RESERVATION:
            self.is_outdated()
            if not self.reservation_end_date:
                self.reservation_end_date = Season.current().subscription_start
            self.uid = 0
        elif self.type == TYPE_WAITING_LIST:
            self.active = True
            self.uid = 0
        elif self.type == TYPE_RESIGNATION:
            if not self.resignation_date:
                self.resignation_date = datetime.date.today()
            self.is_outdated()
        elif self.type == TYPE_CONTRACT:
            self.active = True
            try:
                if type(self.uid) != int or self.uid == 0:
                    self.uid = Contract.objects.filter(season=self.season).aggregate(Max("uid"))["uid__max"] + 1
            except:
                self.uid = 1
            self.reservation_end_date = None
            self.resignation_date = None
        super(Contract, self).save(*args, **kwargs)

    class Meta:
        app_label = "contract"
        ordering = ["season", "uid", "signup_date"]
        verbose_name = _("Contract")
        verbose_name_plural = _("Contracts")
