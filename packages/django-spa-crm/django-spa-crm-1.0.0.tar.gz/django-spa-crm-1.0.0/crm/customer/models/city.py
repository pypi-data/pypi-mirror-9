from django.db import models
from django.utils.translation import ugettext_lazy as _


class City(models.Model):
    DEFAULT_STATE = 1

    name = models.CharField(max_length=30, verbose_name=_("Name"))
    state = models.ForeignKey("customer.State", verbose_name=_("State"), default=DEFAULT_STATE)
    need_verification = models.BooleanField(verbose_name=_("Need verification?"), default=False)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True)

    @staticmethod
    def autocomplete_search_fields():
        return ["name__icontains"]

    def save(self, *args, **kwargs):
        self.name = self.name.strip().title()
        super(City, self).save(*args, **kwargs)

    def __str__(self):
        return "%s, %s" % (
            self.name,
            self.state.name)

    class Meta:
        app_label = "customer"
        ordering = ["state", "name"]
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
