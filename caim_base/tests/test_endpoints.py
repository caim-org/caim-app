from unittest import TestCase as unitTestCase

from django.test import Client, TestCase


# simple endpoint tests. Can the pages render?
class EndpointTesting(unitTestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page(self):
        response = self.client.post("")
        self.assertEqual(response.status_code, 200)

    def test_browse_page(self):
        response = self.client.post("/browse")
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        response = self.client.post("/register")
        self.assertEqual(response.status_code, 200)

    def test_fosterer_page_redirects(self):
        response = self.client.post("/fosterer")
        self.assertEqual(response.status_code, 302)

    def test_fosterer_edit_page_redirects_to_login_if_not_logged_in(self):
        response = self.client.post("/fosterer/about-you")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], "/login?next=/fosterer/about-you")
