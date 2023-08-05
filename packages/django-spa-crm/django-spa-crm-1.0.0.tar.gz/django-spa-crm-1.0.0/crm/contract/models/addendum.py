import datetime
import warnings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from crm.date.models import Season


warnings.warn("Hide defaults inside the model", PendingDeprecationWarning)
DEFAULT_CHOICE = 0
DEFAULT_DOCUMENT = 0
TYPE_CHOICES = [
    (0, _("Group")),
    (1, _("Date"))]


class Addendum(models.Model):
    season = models.ForeignKey("date.Season", verbose_name=_("Season"), default=Season.current().id)
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, default=DEFAULT_CHOICE, verbose_name=_("Addendum Type"), editable=False)
    contract = models.ForeignKey("contract.Contract", verbose_name=_("Contract"))
    document = models.ForeignKey("contract.Document", default=DEFAULT_DOCUMENT, verbose_name=_("Contract Document"))
    need_verification = models.BooleanField(verbose_name=_("Need verification?"), default=False)
    group = models.ForeignKey("group.Group", verbose_name=_("Group From"), related_name="from")
    gid_to = models.ForeignKey("group.Group", verbose_name=_("Group To"), related_name="to")
    start_date = models.DateField(verbose_name=_("Start Date"), default=datetime.datetime.today)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True)

    @staticmethod
    def autocomplete_search_fields():
        return ["contract__customer__last_name__icontains"]

    def save(self, *args, **kwargs):
        self.contract.group = self.gid_to
        self.contract.save()
        super(Addendum, self).save(*args, **kwargs)

    def __str__(self):
        return "%s" % self.contract

    class Meta:
        app_label = "contract"
        ordering = ["contract"]
        verbose_name = _("Addendum")
        verbose_name_plural = _("Addendums")
