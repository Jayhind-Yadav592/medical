from django.test import TestCase, Client
from django.urls import reverse


class APIDocumentationTests(TestCase):
    """Test suite for OpenAPI 3.0 / Swagger / Redoc generation and endpoints."""

    def setUp(self):
        self.client = Client()

    def test_openapi_schema_endpoint(self):
        """Verify OpenAPI JSON/YAML schema generates successfully."""
        response = self.client.get('/api/schema/')
        self.assertEqual(response.status_code, 200)

    def test_swagger_ui_endpoint(self):
        """Verify Swagger UI renders successfully."""
        response = self.client.get('/api/docs/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'swagger-ui')

    def test_redoc_endpoint(self):
        """Verify Redoc UI renders successfully."""
        response = self.client.get('/api/redoc/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'redoc')
