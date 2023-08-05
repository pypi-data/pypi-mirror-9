import warnings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from crm.date.models import Season


warnings.warn("Hide defaults inside the model", PendingDeprecationWarning)
TYPE_CONTRACT = 0
TYPE_ADDENDUM = 1
TYPE_CHOICES = [
    (0, _("Contract")),
    (1, _("Addendum"))]
DEFAULT_CHOICE = TYPE_CONTRACT


class Document(models.Model):
    season = models.ForeignKey("date.Season", verbose_name=_("Season"), default=Season.current().id)
    name = models.CharField(unique=False, max_length=50, verbose_name=_("Name"))
    type = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, default=DEFAULT_CHOICE, verbose_name=_("Document type"))
    need_verification = models.BooleanField(verbose_name=_("Need verification?"), default=False)
    content = models.TextField(verbose_name=_("Document body"))
    html = models.TextField(editable=False)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        self.html = self.content
        super(Document, self).save(*args, **kwargs)

    def __str__(self):
        return "%s %s" % (self.season, self.name)

    class Meta:
        app_label = "contract"
        ordering = ["season", "name"]
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
