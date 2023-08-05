import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Entry(models.Model):
    ticket = models.ForeignKey("contract.Ticket", verbose_name=_("Ticket"))
    date = models.DateField(verbose_name=_("Date"))
    time = models.TimeField(verbose_name=_("Time"))
    was_present = models.BooleanField(verbose_name=_("Was present?"))

    @staticmethod
    def count(weekday, time):
        today = datetime.date.today()
        endweek = today + datetime.timedelta(days=6)
        return Entry.objects.filter(time=time, date__range=(today, endweek), date__week_day=weekday).count()

    def __str__(self):
        return "%(ticket)s - %(date)s %(time)s" % {
            "ticket": self.ticket,
            "date": self.date,
            "time": self.time}

    class Meta:
        app_label = "group"
        ordering = ["date"]
        verbose_name = _("Entry")
        verbose_name_plural = _("Entries")
