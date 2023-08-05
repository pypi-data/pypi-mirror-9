import re
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Customer(models.Model):
    DEFAULT_DOCUMENT = 3
    DEFAULT_SSN = ""

    last_name = models.CharField(max_length=50, verbose_name=_("Last Name"))
    first_name = models.CharField(max_length=50, verbose_name=_("First Name"))
    child_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Children Name"))
    birth_date = models.DateField(blank=True, null=True, verbose_name=_("Birth date"))
    ssn = models.CharField(null=True, blank=True, max_length=11, verbose_name=_("SSN"), default=DEFAULT_SSN)
    document = models.ForeignKey("customer.Document", verbose_name=_("Document"), default=DEFAULT_DOCUMENT)
    doc_id = models.CharField(null=True, blank=True, max_length=20, verbose_name=_("Document ID"))
    phone = models.CharField(max_length=20, verbose_name=_("Phone"))
    email = models.EmailField(unique=False, null=True, blank=True, verbose_name=_("E-mail"))
    address = models.CharField(max_length=60, verbose_name=_("Address"), null=True, blank=True)
    zip_code = models.ForeignKey("customer.ZipCode", verbose_name=_("Zip code"), help_text=_("You can also search by city name"), null=True, blank=True)
    need_verification = models.BooleanField(verbose_name=_("Need verification?"), default=False)
    comment = models.TextField(verbose_name=_("Comment"), unique=False, null=True, blank=True)

    @staticmethod
    def autocomplete_search_fields():
        return ["ssn__iexact", "last_name__icontains"]

    def clean_phone(self):
        try:
            list = re.findall(r"\d", self.phone)
            number = int("".join(list))
            return number
        except Exception:
            return self.phone

    def clean_fields(self, exclude=None):
        self.first_name = self.first_name.strip().lower().title()
        self.last_name = self.last_name.strip().lower().title()
        self.doc_id = self.doc_id.strip().lower().title()
        self.email = self.email.strip().lower()
        self.phone = self.clean_phone()
        self.address = self.address.strip().lower().title()

    def save(self, *args, **kwargs):
        self.clean_fields()
        super(Customer, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return "/customer/customer/%s/" % self.id

    def __str__(self):
        ret = "%s %s" % (
            self.last_name,
            self.first_name)
        if self.address and self.zip_code:
            ret += " (%s, %s)" % (self.address, self.zip_code.city.name)
        elif self.address:
            ret += " (%s)" % self.address
        elif self.zip_code:
            ret += " (%s)" % self.zip_code.city.name
        return ret

    class Meta:
        app_label = "customer"
        ordering = ["last_name", "first_name", "address"]
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
