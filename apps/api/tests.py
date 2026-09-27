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


class PrescriptionAIOCRTests(TestCase):
    """Test suite for Clinical AI Vision and Prescription OCR parser."""

    def setUp(self):
        self.client = Client()

    def test_ai_ocr_scan_api_endpoint(self):
        """Verify POST /api/prescriptions/ai-ocr/ parses medications successfully."""
        response = self.client.post('/api/prescriptions/ai-ocr/', {}, format='multipart')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertIn('detected_medications', data)
        self.assertGreater(len(data['detected_medications']), 0)
        self.assertIn('doctor_info', data)
        self.assertIn('patient_info', data)

    def test_ai_ocr_allergy_safety_alert(self):
        """Verify allergy profile triggers clinical safety contraindication alert."""
        response = self.client.post('/api/prescriptions/ai-ocr/', {'allergies': 'Penicillin, Amoxicillin'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check if amoxicillin is flagged with safety conflict
        meds = data['detected_medications']
        amox_med = next((m for m in meds if 'amox' in m['extracted_name'].lower()), None)
        self.assertIsNotNone(amox_med)
        self.assertFalse(amox_med['safety_check']['is_safe'])
        self.assertIn('Penicillin', amox_med['safety_check']['alert'])

