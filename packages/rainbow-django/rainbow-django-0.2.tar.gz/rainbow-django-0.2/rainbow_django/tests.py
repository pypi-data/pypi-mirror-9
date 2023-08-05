from django.test import TestCase

# Create your tests here.

class ApiTest(TestCase):
    def test_get_handler(self):
        from rainbow_django import get_handler
        print get_handler(0)