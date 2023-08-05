from django.db import models
from django.utils.translation import ugettext_lazy as _


class Category(models.Model):
    name = models.CharField(unique=True, max_length=50, verbose_name=_("Name"))
    need_verification = models.BooleanField(verbose_name=_("Need verification?"), default=False)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        app_label = "group"
        ordering = ["name"]
        verbose_name = _("Category")
        verbose_name_plural = _("Category")
