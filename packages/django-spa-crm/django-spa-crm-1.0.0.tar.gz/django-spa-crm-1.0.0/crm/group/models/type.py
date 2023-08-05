import warnings
from django.db import models
from django.utils.translation import ugettext_lazy as _


warnings.warn("Hide defaults to model", Warning)
DEFAULT_COST = 0
DEFAULT_TEMP = 32
DEFAULT_TEMP_TYPE = 0
DEFAULT_CAPACITY = 15
warnings.warn("Remove colors", PendingDeprecationWarning)
DEFAULT_COLOR = "#ffffff"
TEMP_TYPE = [
    (0, _("Celcius")),
    (1, _("Farenheit")),
    (2, _("Kelvin"))]


class Type(models.Model):
    short_name = models.CharField(unique=True, max_length=50, verbose_name=_("Short Name"))
    full_name = models.CharField(blank=True, null=True, max_length=100, verbose_name=_("Full Name"))
    cost = models.DecimalField(decimal_places=2, max_digits=5, null=True, blank=True, verbose_name=_("Cost"), default=DEFAULT_COST, help_text=_("use . (Dot) for separating decimal values"))
    display_color = models.CharField(max_length=7, default=DEFAULT_COLOR, blank=True, verbose_name=_("Display Color"))
    temp = models.PositiveSmallIntegerField(default=DEFAULT_TEMP, blank=True, null=True,)
    temp_type = models.PositiveSmallIntegerField(blank=True, choices=TEMP_TYPE, default=DEFAULT_TEMP_TYPE, verbose_name=_("Temperature type"))
    capacity = models.PositiveSmallIntegerField(blank=True, null=True, default=DEFAULT_CAPACITY, verbose_name=_("Capacity"))
    category = models.ForeignKey("group.Category", verbose_name=_("Category"))
    variant = models.ForeignKey("group.Variant", blank=True, null=True, verbose_name=_("Variant"))
    level = models.ForeignKey("group.Level", blank=True, null=True, verbose_name=_("Level"))
    need_verification = models.BooleanField(verbose_name=_("Need verification?"), default=False)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True)

    def __str__(self):
        return self.short_name

    class Meta:
        app_label = "group"
        ordering = ["short_name"]
        verbose_name = _("Type")
        verbose_name_plural = _("Type")
