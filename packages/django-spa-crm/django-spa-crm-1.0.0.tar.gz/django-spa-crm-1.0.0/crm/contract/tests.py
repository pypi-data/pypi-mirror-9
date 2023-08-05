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
            "/contract/",
            "/contract/addendum/",
            "/contract/addendum/add/",
            "/contract/contract/",
            "/contract/contract/add/",
            "/contract/contract/48/",
            "/contract/document/",
            "/contract/document/add/",
            "/contract/document/2/",
            "/contract/ticket/",
            "/contract/ticket/add/",
            "/contract/print/sample/2/",
            "/contract/print/contract/223/"]

        for url in urls:
            response = self.client.get(url)
            log.info("%s, %s" % (response.status_code, url))
            self.assertEqual(response.status_code, 200)
