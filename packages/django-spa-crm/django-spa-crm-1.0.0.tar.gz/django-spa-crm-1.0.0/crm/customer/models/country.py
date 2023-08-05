from django.db import models
from django.utils.translation import ugettext_lazy as _


class Country(models.Model):
    CONTINENTS = [
        (0, _("Africa")),
        (1, _("Antarctica")),
        (2, _("Asia")),
        (3, _("Australia")),
        (4, _("Europe")),
        (5, _("North America")),
        (6, _("South America"))]

    name = models.CharField(unique=True, max_length=50, verbose_name=_("Name"))
    iso_alpha_2 = models.CharField(unique=True, max_length=2, verbose_name=_("ISO Alpha 2"))
    iso_alpha_3 = models.CharField(unique=True, max_length=3, verbose_name=_("ISO Alpha 3"))
    continent = models.PositiveSmallIntegerField(choices=CONTINENTS, verbose_name=_("Continent"))
    need_verification = models.BooleanField(verbose_name=_("Need verification?"), default=False)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.name = self.name.strip().title()
        super(Country, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "customer"
        ordering = ["name"]
        verbose_name = _("Country")
        verbose_name_plural = _("Countries")
