import warnings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from crm.contract.models import Contract
from crm.contract.models.contract import TYPE_RESERVATION
from crm.contract.models.contract import TYPE_CONTRACT
from crm.contract.models.contract import TYPE_WAITING_LIST
from crm.contract.models.contract import TYPE_PASS
from crm.date.models import Season


warnings.warn("Hide defaults in model", PendingDeprecationWarning)
DEFAULT_COST = 0
DEFAULT_DISCOUNT = 0
DEFAULT_GID = ""
DEFAULT_DOCUMENT = 1


class Group(models.Model):
    season = models.ForeignKey("date.Season", verbose_name=_("Season"), default=Season.current().id)
    gid = models.IntegerField(verbose_name=_("Group ID"), default=DEFAULT_GID)
    type = models.ForeignKey("group.Type", verbose_name=_("Type"))
    day = models.ForeignKey("date.Weekday", verbose_name=_("Week day"))
    hour = models.TimeField(verbose_name=_("Hour"))
    document = models.ForeignKey("contract.Document", null=True, blank=True, default=DEFAULT_DOCUMENT, verbose_name=_("Contract Document"))
    cost = models.DecimalField(decimal_places=2, max_digits=5, null=False, verbose_name=_("Cost"), default=DEFAULT_COST, help_text=_("use . (Dot) for separating decimal values"))
    discount = models.DecimalField(decimal_places=2, max_digits=5, null=False, verbose_name=_("Discount"), default=DEFAULT_DISCOUNT, help_text=_("use . (Dot) for separating decimal values"))
    cost_2010 = models.DecimalField(decimal_places=2, max_digits=5, null=False, verbose_name=_("Cost"), default=DEFAULT_COST, help_text=_("use . (Dot) for separating decimal values"))
    discount_2010 = models.DecimalField(decimal_places=2, max_digits=5, null=False, verbose_name=_("Discount"), default=DEFAULT_DISCOUNT, help_text=_("use . (Dot) for separating decimal values"))
    pool = models.ForeignKey("group.Pool", verbose_name=_("Lokacja"))
    instructor = models.ForeignKey("group.Instructor", verbose_name=_("Instructor"), related_name="instructor")
    disabled = models.BooleanField(verbose_name=_("Disabled?"), default=False)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True)

    @staticmethod
    def autocomplete_search_fields():
        return ["type__short_name__icontains", "day__name__startswith", "hour__startswith"]

    @staticmethod
    def get(gid):
        return Group.objects.get(gid=gid)

    def contracts(self, active=True):
        return Contract.objects.all(group=self, active=active)

    @staticmethod
    def hours(groups):
        return groups.values("hour", "pool").distinct().order_by("hour")

    def count(self, type):
        return Contract.objects.filter(group=self, type=type).count()

    def summary(self):
        warnings.warn("Use types from contract.TYPE_...")
        warnings.warn("Hardcoded data")
        if self.type.short_name == "GIM":
            ret = _("Swimming pool pass: %(count)s") % {"count": self.count(TYPE_PASS)}
            ret += _(" - Reservations: %(count)s") % {"count": self.count(TYPE_RESERVATION)}
        else:
            ret = _("Contracts: %(count)s") % {"count": self.count(TYPE_CONTRACT)}
            ret += _(" - Reservations: %(count)s") % {"count": self.count(TYPE_RESERVATION)}
            ret += _(" - Swimming pool pass: %(count)s") % {"count": self.count(TYPE_PASS)}
            ret += _(" - Waiting: %(count)s") % {"count": self.count(TYPE_WAITING_LIST)}
        return ret

    def __str__(self):
        ret = "%s - [%s %s]" % (
            self.season,
            _(self.day.name),
            self.hour.strftime("%H:%M"))
        if self.type.short_name:
            ret += " " + self.type.short_name
        ret += " -- " + self.summary()
        return ret

    class Meta:
        app_label = "group"
        ordering = ["day", "hour"]
        verbose_name = _("Group")
        verbose_name_plural = _("Groups")
