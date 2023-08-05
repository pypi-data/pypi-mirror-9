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
            "/customer/",
            "/customer/city/",
            "/customer/city/add/",
            "/customer/city/2251/",
            "/customer/country/",
            "/customer/country/add/",
            "/customer/country/1/",
            "/customer/customer/",
            "/customer/customer/add/",
            "/customer/customer/2/",
            "/customer/document/",
            "/customer/document/add/",
            "/customer/document/2/",
            "/customer/state/",
            "/customer/state/add/",
            "/customer/state/1/",
            "/customer/zipcode/",
            "/customer/zipcode/add/",
            "/customer/zipcode/8242/"]

        for url in urls:
            response = self.client.get(url)
            log.info("%s, %s" % (response.status_code, url))
            self.assertEqual(response.status_code, 200)
