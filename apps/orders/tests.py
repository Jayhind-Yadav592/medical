from django.test import TestCase, Client
from django.utils import timezone
from apps.orders.models import Order, OrderItem, Prescription
from apps.pharmacy.models import Category, Product
from apps.orders.pdf_generator import generate_order_invoice_pdf, generate_prescription_pdf


class PDFInvoiceAndPrescriptionTests(TestCase):
    """Test suite for ReportLab PDF generation engines and download endpoints."""

    def setUp(self):
        self.client = Client()
        
        # Setup Category & Product
        self.category = Category.objects.create(name="Cardiovascular Care", slug="cardiovascular-care")
        self.product = Product.objects.create(
            name="Atorvastatin Calcium Tablets",
            slug="atorvastatin-calcium-tablets",
            sku="CARD-ATOR-20",
            category=self.category,
            short_description="Cholesterol reduction medication",
            full_description="FDA approved statin medication.",
            dosage_strength="20mg",
            dosage_form="TABLET",
            price=24.50,
            stock=100
        )
        
        # Setup Order
        self.order = Order.objects.create(
            full_name="Alexander Hamilton",
            email="alexander@antixorpharmacy.com",
            phone="+1 555-019-2831",
            shipping_address="55 Wall Street, Suite 400",
            city="New York",
            postal_code="10005",
            total_amount=49.00,
            shipping_fee=0.00,
            discount_amount=5.00,
            final_amount=44.00,
            payment_method="CARD",
            payment_status="PAID",
            order_status="PROCESSING"
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name=self.product.name,
            unit_price=24.50,
            quantity=2,
            subtotal=49.00
        )
        
        # Setup Prescription
        self.prescription = Prescription.objects.create(
            patient_name="Alexander Hamilton",
            patient_phone="+1 555-019-2831",
            doctor_name="Dr. Sarah Jenkins, MD",
            clinic_hospital="Antixor Telehealth Center",
            notes="Dispense 30 days dosage. Take 1 tablet daily with evening meals.",
            status="VERIFIED"
        )

    def test_generate_order_invoice_pdf_buffer(self):
        """Verify generate_order_invoice_pdf returns valid PDF bytes starting with %PDF."""
        pdf_buf = generate_order_invoice_pdf(self.order)
        content = pdf_buf.getvalue()
        self.assertGreater(len(content), 1000)
        self.assertTrue(content.startswith(b'%PDF'))

    def test_generate_prescription_pdf_buffer(self):
        """Verify generate_prescription_pdf returns valid PDF bytes starting with %PDF."""
        pdf_buf = generate_prescription_pdf(self.prescription)
        content = pdf_buf.getvalue()
        self.assertGreater(len(content), 1000)
        self.assertTrue(content.startswith(b'%PDF'))

    def test_order_invoice_pdf_web_endpoint(self):
        """Verify GET /order/invoice/<order_no>/pdf/ returns 200 with application/pdf."""
        url = f'/order/invoice/{self.order.order_number}/pdf/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn(self.order.order_number, response['Content-Disposition'])

    def test_prescription_pdf_web_endpoint(self):
        """Verify GET /prescription/<id>/pdf/ returns 200 with application/pdf."""
        url = f'/prescription/{self.prescription.id}/pdf/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('Antixor_Rx_', response['Content-Disposition'])

    def test_api_order_invoice_pdf_endpoint(self):
        """Verify API endpoint GET /api/orders/<order_no>/invoice/pdf/ returns 200 with PDF."""
        url = f'/api/orders/{self.order.order_number}/invoice/pdf/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_api_prescription_pdf_endpoint(self):
        """Verify API endpoint GET /api/prescriptions/<id>/pdf/ returns 200 with PDF."""
        url = f'/api/prescriptions/{self.prescription.id}/pdf/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')


class PaymentGatewayTests(TestCase):
    """Test suite for Stripe, Razorpay and Multi-Payment Gateway engines."""

    def setUp(self):
        self.client = Client()
        self.order = Order.objects.create(
            full_name="Eleanor Vance",
            email="eleanor@example.com",
            phone="+1 555-492-9102",
            shipping_address="742 Evergreen Terrace",
            city="New York",
            postal_code="10001",
            total_amount=58.50,
            shipping_fee=0.00,
            discount_amount=0.00,
            final_amount=58.50,
            payment_method="CARD",
            payment_status="PENDING",
            order_status="PLACED"
        )

    def test_stripe_payment_intent_creation(self):
        """Verify POST /api/orders/payment/create-intent/ returns valid Stripe payload."""
        response = self.client.post('/api/orders/payment/create-intent/', {
            'order_number': self.order.order_number,
            'gateway': 'STRIPE'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('gateway'), 'STRIPE')
        self.assertIn('client_secret', data)
        self.assertEqual(data.get('amount_usd'), 58.50)

    def test_razorpay_payment_order_creation(self):
        """Verify POST /api/orders/payment/create-intent/ returns valid Razorpay payload."""
        response = self.client.post('/api/orders/payment/create-intent/', {
            'order_number': self.order.order_number,
            'gateway': 'RAZORPAY'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertEqual(data.get('gateway'), 'RAZORPAY')
        self.assertIn('razorpay_order_id', data)

    def test_payment_verify_updates_order_status(self):
        """Verify POST /api/orders/payment/verify/ marks order as PAID."""
        response = self.client.post('/api/orders/payment/verify/', {
            'order_number': self.order.order_number,
            'gateway': 'STRIPE',
            'payment_id': 'txn_stripe_sandbox_12345'
        }, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'PAID')

    def test_stripe_webhook_listener(self):
        """Verify POST /api/webhooks/stripe/ reconciles payment."""
        payload = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'id': 'evt_stripe_test_100',
                    'client_reference_id': self.order.order_number
                }
            }
        }
        response = self.client.post('/api/webhooks/stripe/', payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'PAID')

    def test_razorpay_webhook_listener(self):
        """Verify POST /api/webhooks/razorpay/ reconciles payment."""
        payload = {
            'event': 'payment.captured',
            'payload': {
                'payment': {
                    'entity': {
                        'id': 'pay_rzp_test_200',
                        'notes': {
                            'order_number': self.order.order_number
                        }
                    }
                }
            }
        }
        response = self.client.post('/api/webhooks/razorpay/', payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'PAID')

