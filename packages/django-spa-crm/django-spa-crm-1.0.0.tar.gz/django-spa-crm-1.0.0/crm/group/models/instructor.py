import warnings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import models as auth

warnings.warn("Add multiple instructors", Warning)


class Instructor(models.Model):
    user = models.ForeignKey(auth.User, verbose_name=_("Instructor"))
    user2 = models.ForeignKey(auth.User, verbose_name=_("Instructor 2"), related_name="user2", null=True, blank=True)
    need_verification = models.BooleanField(verbose_name=_("Need verification?"), default=False)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True)

    def __str__(self):
        if self.user2:
            return "%s %s, %s %s" % (self.user.first_name, self.user.last_name, self.user2.first_name, self.user2.last_name)
        else:
            return "%s %s" % (self.user.first_name, self.user.last_name)

    class Meta:
        app_label = "group"
        ordering = ["user"]
        verbose_name = _("Instructor")
        verbose_name_plural = _("Instructors")
