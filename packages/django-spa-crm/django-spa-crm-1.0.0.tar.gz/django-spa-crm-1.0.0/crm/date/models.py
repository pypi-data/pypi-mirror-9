import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Month(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name=_("Name"))
    order = models.PositiveSmallIntegerField(verbose_name=_("Order"))
    need_verification = models.BooleanField(verbose_name=_("Need verification?"), default=False)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True)

    @staticmethod
    def previous():
        month = datetime.date.today().month - 1
        if month < 1:
            month = 12
        if month > 12:
            month = 1
        return Month.objects.get(id=month)

    @staticmethod
    def current():
        return Month.objects.get(id=datetime.date.today().month)

    @staticmethod
    def next():
        month = datetime.date.today().month + 1
        if month < 1:
            month = 12
        if month > 12:
            month = 1
        return Month.objects.get(id=month)

    def __str__(self):
        return str(_(self.name))

    class Meta:
        app_label = "date"
        ordering = ["order"]
        verbose_name = _("Month")
        verbose_name_plural = _("Months")


class Weekday(models.Model):
    name = models.CharField(max_length=20, verbose_name=_("Name"))
    order = models.PositiveSmallIntegerField(verbose_name=_("Order"))
    need_verification = models.BooleanField(verbose_name=_("Need verification?"), default=False)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True)

    def __str__(self):
        return str(_(self.name))

    class Meta:
        app_label = "date"
        ordering = ["id"]
        verbose_name = _("Week day")
        verbose_name_plural = _("Week days")


class Season(models.Model):
    name = models.CharField(max_length=9, unique=True, verbose_name=_("Name"))
    subscription_start = models.DateField(verbose_name=_("Subscription start date"))
    start = models.DateField(verbose_name=_("Start date"))
    end = models.DateField(verbose_name=_("End date"))
    need_verification = models.BooleanField(verbose_name=_("Need verification?"), default=False)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True)

    @staticmethod
    def current():
        try:
            return Season.objects.filter(start__lte=datetime.date.today()).order_by("-subscription_start")[:1][0]
        except IndexError:
            raise Season.DoesNotExist("There is no current season in database")

    @staticmethod
    def next():
        try:
            return Season.objects.filter(start__gte=datetime.date.today()).order_by("subscription_start")[:1][0]
        except IndexError:
            raise Season.DoesNotExist("There is no next season in database")

    def __str__(self):
        return self.name

    class Meta:
        app_label = "date"
        ordering = ["start"]
        verbose_name = _("Season")
        verbose_name_plural = _("Seasons")
