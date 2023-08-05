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
            "/date/",
            "/date/month/",
            "/date/month/add/",
            "/date/month/1/",
            "/date/season/",
            "/date/season/add/",
            "/date/season/5/",
            "/date/weekday/",
            "/date/weekday/add/",
            "/date/weekday/1/"]

        for url in urls:
            response = self.client.get(url)
            log.info("%s, %s" % (response.status_code, url))
            self.assertEqual(response.status_code, 200)
