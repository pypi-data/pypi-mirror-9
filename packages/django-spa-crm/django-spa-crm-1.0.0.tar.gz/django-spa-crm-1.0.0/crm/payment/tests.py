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
            "/payment/",
            "/payment/report/",
            "/payment/report/date-range/?start=2013-09-01&end=2013-09-01",
            "/payment/report/monthly-statement/?season=2013-2014&month=9",
            "/payment/report/missing/?season=2013-2014&month=9"]

        for url in urls:
            response = self.client.get(url)
            log.info("%s, %s" % (response.status_code, url))
            self.assertEqual(response.status_code, 200)
