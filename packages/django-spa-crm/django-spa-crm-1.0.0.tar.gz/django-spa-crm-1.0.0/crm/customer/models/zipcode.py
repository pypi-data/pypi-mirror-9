from django.db import models
from django.utils.translation import ugettext_lazy as _


class ZipCode(models.Model):
    DEFAULT_CITY = None

    zip_code = models.CharField(unique=False, max_length=8, verbose_name=_("Zip code"))
    city = models.ForeignKey("customer.City", verbose_name=_("City"), default=DEFAULT_CITY)
    need_verification = models.BooleanField(verbose_name=_("Need verification?"), default=False)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True)

    @staticmethod
    def autocomplete_search_fields():
        return ["zip_code__startswith", "city__name__icontains"]

    def __str__(self):
        return "%s %s" % (self.zip_code, self.city.name)

    class Meta:
        app_label = "customer"
        ordering = ["city", "zip_code"]
        verbose_name = _("Zip code")
        verbose_name_plural = _("Zip codes")
