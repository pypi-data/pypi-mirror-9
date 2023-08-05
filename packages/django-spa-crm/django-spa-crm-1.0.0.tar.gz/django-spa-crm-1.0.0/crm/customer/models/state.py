from django.db import models
from django.utils.translation import ugettext_lazy as _


class State(models.Model):
    DEFAULT_COUNTRY = 1

    name = models.CharField(unique=True, max_length=20, verbose_name=_("Name"))
    country = models.ForeignKey("customer.Country", verbose_name=_("Country"), default=DEFAULT_COUNTRY)
    need_verification = models.BooleanField(verbose_name=_("Need verification?"), default=False)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.name = self.name.strip().title()
        super(State, self).save(*args, **kwargs)

    def __str__(self):
        return "%s, %s" % (
            self.name,
            self.country.name)

    class Meta:
        app_label = "customer"
        ordering = ["country", "name"]
        verbose_name = _("State")
        verbose_name_plural = _("States")
