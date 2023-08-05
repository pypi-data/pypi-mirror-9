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
            "/group/",
            "/group/category/",
            "/group/category/add/",
            "/group/category/1/",
            "/group/entry/",
            "/group/entry/add/",
            "/group/group/",
            "/group/group/add/",
            "/group/group/95/",
            "/group/instructor/",
            "/group/instructor/add/",
            "/group/instructor/1/",
            "/group/level/",
            "/group/level/add/",
            "/group/pool/",
            "/group/pool/add/",
            "/group/pool/1/",
            "/group/type/",
            "/group/type/add/",
            "/group/type/1/",
            "/group/variant/",
            "/group/variant/add/",
            "/group/timetable/current-season/",
            "/group/timetable/next-season/",
            "/group/show/95/",
            "/group/show/100/",
            "/group/json/cost/214/?_=1399209947642",
            "/group/json/document/214/?_=1399209947643"]

        for url in urls:
            response = self.client.get(url)
            log.info("%s, %s" % (response.status_code, url))
            self.assertEqual(response.status_code, 200)
