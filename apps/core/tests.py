from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from apps.pharmacy.models import Category, Product, Brand
from apps.telehealth.models import Doctor, ConsultationRequest
from apps.orders.models import Order, Prescription, Cart, CartItem
from apps.articles.models import Article, ArticleCategory

User = get_user_model()


class AuraHealthIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test_patient',
            email='test@aurahealth.com',
            password='securepassword123',
            first_name='Arthur',
            last_name='Morgan'
        )

        self.category = Category.objects.create(
            name='Prescription Antibiotics',
            slug='prescription-antibiotics',
            icon_class='fa-solid fa-pills'
        )

        self.brand = Brand.objects.create(name='AuraBio Labs', country='Switzerland')

        self.product = Product.objects.create(
            name='Amoxicillin Trihydrate 500mg',
            slug='amoxicillin-500mg-test',
            sku='TEST-AMOX-500',
            category=self.category,
            brand=self.brand,
            short_description='Broad-spectrum antibiotic.',
            full_description='Complete clinical antibiotic description.',
            active_ingredient='Amoxicillin 500mg',
            dosage_form='CAPSULE',
            dosage_strength='500mg',
            price=15.00,
            mrp_price=20.00,
            stock=100,
            prescription_required=True,
            is_featured=True
        )

        self.doctor = Doctor.objects.create(
            full_name='Dr. Elena Vance, PharmD',
            specialty='CLINICAL_PHARMACIST',
            qualification='PharmD, BCPS',
            experience_years=12,
            bio='Expert clinical pharmacist.',
            consultation_fee=0.00,
            is_available_online=True
        )

    def test_homepage_render(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AuraHealth')
        self.assertContains(response, 'Amoxicillin Trihydrate 500mg')

    def test_shop_page_render_and_filter(self):
        response = self.client.get(reverse('shop') + f'?category={self.category.slug}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Amoxicillin Trihydrate 500mg')

    def test_autocomplete_search_api(self):
        response = self.client.get(reverse('api-autocomplete') + '?q=amox')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(len(data) >= 1)
        self.assertEqual(data[0]['name'], 'Amoxicillin Trihydrate 500mg')

    def test_cart_api_flow(self):
        # 1. Add to cart
        add_res = self.client.post(
            reverse('api-cart'),
            data={'product_id': self.product.id, 'quantity': 2},
            content_type='application/json'
        )
        self.assertEqual(add_res.status_code, 200)
        cart_data = add_res.json()['cart']
        self.assertEqual(cart_data['total_items'], 2)
        self.assertEqual(float(cart_data['subtotal']), 30.00)
        self.assertTrue(cart_data['requires_prescription'])

        # 2. Get cart
        get_res = self.client.get(reverse('api-cart'))
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()['total_items'], 2)

    def test_prescription_upload_api(self):
        fake_file = SimpleUploadedFile("rx_scan.pdf", b"%PDF-1.4 fake prescription content", content_type="application/pdf")
        res = self.client.post(reverse('api-prescription-upload'), {
            'patient_name': 'Eleanor Vance',
            'patient_phone': '+1 (555) 019-2834',
            'doctor_name': 'Dr. Arthur Miller, MD',
            'notes': 'Please dispense 30 day supply.',
            'prescription_file': fake_file
        })
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data['prescription']['patient_name'], 'Eleanor Vance')
        self.assertEqual(data['prescription']['status'], 'PENDING')

    def test_consultation_booking_api(self):
        res = self.client.post(reverse('api-consultation-book'), data={
            'doctor_id': self.doctor.id,
            'patient_name': 'Sarah Miller',
            'patient_email': 'sarah@example.com',
            'patient_phone': '+1 (555) 012-3456',
            'preferred_date': '2026-09-30',
            'preferred_time': '10:00 AM',
            'symptoms': 'Mild recurring migraine symptoms.'
        }, content_type='application/json')
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data['booking']['doctor_name'], 'Dr. Elena Vance, PharmD')

    def test_checkout_and_order_tracking_api(self):
        # Put item in cart first
        self.client.post(
            reverse('api-cart'),
            data={'product_id': self.product.id, 'quantity': 1},
            content_type='application/json'
        )

        # Checkout
        checkout_res = self.client.post(reverse('api-checkout'), data={
            'full_name': 'Arthur Morgan',
            'email': 'arthur@example.com',
            'phone': '+1 (555) 019-9999',
            'street_address': '450 Lexington Ave, Suite 1200',
            'city': 'New York',
            'postal_code': '10017',
            'payment_method': 'COD'
        }, content_type='application/json')
        self.assertEqual(checkout_res.status_code, 201)
        order_data = checkout_res.json()['order']
        order_num = order_data['order_number']
        self.assertTrue(order_num.startswith('AUR-'))

        # Track order via API
        track_res = self.client.get(f'/api/orders/track/{order_num}/')
        self.assertEqual(track_res.status_code, 200)
        self.assertEqual(track_res.json()['order_number'], order_num)
        self.assertEqual(track_res.json()['full_name'], 'Arthur Morgan')
