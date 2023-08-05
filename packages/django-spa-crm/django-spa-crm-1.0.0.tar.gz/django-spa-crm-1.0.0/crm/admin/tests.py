import logging
from django.conf import settings
from django.test import TestCase
from django.test.client import Client


log = logging.getLogger(__name__)


class URLTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.client.login(
            username=settings.TEST_USERNAME,
            password=settings.TEST_PASSWORD)

    def test_urls(self):
        urls = [
            "/",
            "/grappelli/lookup/autocomplete/?term=%C5%9Bro&app_label=group&model_name=group&query_string=t=id",
            "/grappelli/lookup/related/?object_id=2230&app_label=customer&model_name=customer",
            "/grappelli/lookup/related/?object_id=214&app_label=group&model_name=group",
            "/grappelli/lookup/autocomplete/?term=ada&app_label=customer&model_name=customer&query_string=t=id",
            "/grappelli/lookup/autocomplete/?term=daw&app_label=customer&model_name=customer&query_string=t=id",
            "/grappelli/lookup/autocomplete/?term=2013-2014%20-%20%5Bponiedzia%C5%82ek%2011%3A45%5D%20NIEMOWL%C4%98TA%203-6%20--%20Um%C3%B3w%3A%208%20-%20Rezerwacji%3A%202%20-%20Karnet%C3%B3w%3A%200%20-%20Oczekuj%C4%85cych%3A%200&app_label=group&model_name=group&query_string=t=id",
            "/grappelli/lookup/autocomplete/?term=%C5%9Brod&app_label=group&model_name=group&query_string=t=id",
            "/grappelli/lookup/autocomplete/?term=wto&app_label=group&model_name=group&query_string=t=id",
            "/grappelli/lookup/autocomplete/?term=czwa&app_label=group&model_name=group&query_string=t=id",
            "/grappelli/lookup/autocomplete/?term=pi%C4%85&app_label=group&model_name=group&query_string=t=id",
            "/grappelli/lookup/autocomplete/?term=aqu&app_label=group&model_name=group&query_string=t=id",
            "/grappelli/lookup/autocomplete/?term=18%3A00&app_label=group&model_name=group&query_string=t=id",
            "/grappelli/lookup/autocomplete/?term=19%3A00&app_label=group&model_name=group&query_string=t=id",
            "/grappelli/lookup/autocomplete/?term=8%3A00&app_label=group&model_name=group&query_string=t=id",
            "/grappelli/lookup/autocomplete/?term=08%3A00&app_label=group&model_name=group&query_string=t=id"]

        for url in urls:
            response = self.client.get(url)
            log.info("%s, %s" % (response.status_code, url))
            self.assertEqual(response.status_code, 200)
