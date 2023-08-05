from django.db import models
from django.utils.translation import ugettext_lazy as _


class Pool(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name=_("Name"))
    capacity = models.PositiveSmallIntegerField(verbose_name=_("Capacity"))
    need_verification = models.BooleanField(verbose_name=_("Need verification?"), default=False)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "group"
        ordering = ["name"]
        verbose_name = _("Pool")
        verbose_name_plural = _("Pools")
