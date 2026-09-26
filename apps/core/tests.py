from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from apps.pharmacy.models import Category, Product, Brand
from apps.telehealth.models import Doctor, ConsultationRequest
from apps.orders.models import Order, Prescription, Cart, CartItem
from apps.articles.models import Article, ArticleCategory
from apps.core.models import MedicalFacility, PatientVital, PillReminder, PatientIntake

User = get_user_model()


class AuraHealthIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test_patient',
            email='test@antixor.com',
            password='securepassword123',
            first_name='Arthur',
            last_name='Morgan',
            digital_health_id='ANT-P-991823',
            blood_group='O+',
            medical_allergies='Penicillin, Sulfa',
            chronic_conditions='Hypertension',
            emergency_contact='Dr. Robert Vance',
            emergency_phone='+1 (800) 555-0199'
        )

        self.category = Category.objects.create(
            name='Prescription Antibiotics',
            slug='prescription-antibiotics',
            icon_class='fa-solid fa-pills'
        )

        self.brand = Brand.objects.create(name='Antixor Labs', country='Switzerland')

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

        self.facility = MedicalFacility.objects.create(
            name='Antixor Flagship Central Hub',
            facility_type='PHARMACY',
            address='100 Wall Street, New York, NY 10005',
            phone='+1 (800) 584-2689',
            latitude=40.7060,
            longitude=-74.0088,
            is_24_7=True,
            ambulance_available=True
        )

    def test_homepage_render(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Antixor')
        self.assertContains(response, 'Paracetamol 500mg')

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

    def test_auth_views_and_flow(self):
        # 1. Login page render
        login_page_res = self.client.get(reverse('login'))
        self.assertEqual(login_page_res.status_code, 200)
        self.assertContains(login_page_res, 'Antixor')

        # 2. Login POST with credentials
        login_post = self.client.post(reverse('login'), {
            'username': 'test_patient',
            'password': 'securepassword123'
        })
        self.assertEqual(login_post.status_code, 302)

        # 3. Logout
        logout_res = self.client.get(reverse('logout'))
        self.assertEqual(logout_res.status_code, 302)

        # 4. Register page render & POST
        reg_page_res = self.client.get(reverse('register'))
        self.assertEqual(reg_page_res.status_code, 200)

        reg_post = self.client.post(reverse('register'), {
            'username': 'new_patient_test',
            'email': 'newpatient@antixor.com',
            'first_name': 'Clara',
            'last_name': 'Oswald',
            'phone_number': '+1 (555) 777-8899',
            'password': 'password12345',
            'confirm_password': 'password12345'
        })
        self.assertEqual(reg_post.status_code, 302)
        self.assertTrue(User.objects.filter(username='new_patient_test').exists())

    def test_medical_facilities_api_and_page(self):
        # 1. Facilities Page View
        page_res = self.client.get(reverse('facilities'))
        self.assertEqual(page_res.status_code, 200)
        self.assertContains(page_res, 'Antixor Flagship Central Hub')

        # 2. Nearest Facilities API with Geolocation
        api_res = self.client.get('/api/facilities/nearest/?lat=40.7128&lng=-74.0060')
        self.assertEqual(api_res.status_code, 200)
        data = api_res.json()
        facilities = data['facilities']
        self.assertTrue(len(facilities) >= 1)
        self.assertEqual(facilities[0]['name'], 'Antixor Flagship Central Hub')
        self.assertIn('distance_km', facilities[0])

    def test_emergency_sos_api(self):
        sos_res = self.client.post('/api/emergency/sos/', data={
            'patient_name': 'Arthur Morgan',
            'phone': '+1 (800) 555-0199',
            'lat': '40.7128',
            'lng': '-74.0060',
            'emergency_type': 'Severe Acute Chest Pain'
        }, content_type='application/json')
        self.assertEqual(sos_res.status_code, 201)
        data = sos_res.json()
        self.assertTrue(data['success'])
        self.assertIn('sos_id', data)
        self.assertIn('allocated_hospital', data)

    def test_drug_allergy_safety_checker_api(self):
        # 1. Conflict detected (Amoxicillin vs Penicillin allergy)
        conflict_res = self.client.post('/api/safety/check-allergy/', data={
            'medicine_name': 'Amoxicillin Trihydrate 500mg',
            'allergies': 'Penicillin, Sulfa'
        }, content_type='application/json')
        self.assertEqual(conflict_res.status_code, 200)
        self.assertFalse(conflict_res.json()['is_safe'])
        self.assertEqual(conflict_res.json()['severity'], 'HIGH')

        # 2. Safe medication
        safe_res = self.client.post('/api/safety/check-allergy/', data={
            'medicine_name': 'Vitamin D3 5000 IU',
            'allergies': 'Penicillin'
        }, content_type='application/json')
        self.assertEqual(safe_res.status_code, 200)
        self.assertTrue(safe_res.json()['is_safe'])

    def test_patient_vitals_api_and_dashboard(self):
        self.client.login(username='test_patient', password='securepassword123')
        
        # 1. Post vitals
        post_vital = self.client.post('/api/patient/vitals/', data={
            'systolic_bp': 125,
            'diastolic_bp': 82,
            'blood_sugar': 98.0,
            'heart_rate': 74,
            'spo2': 99,
            'weight_kg': 72.0,
            'bmi': 23.1,
            'notes': 'Post-exercise biometric check'
        }, content_type='application/json')
        self.assertEqual(post_vital.status_code, 201)

        # 2. Get vitals
        get_vital = self.client.get('/api/patient/vitals/')
        self.assertEqual(get_vital.status_code, 200)
        self.assertEqual(len(get_vital.json()), 1)

        # 3. View Dashboard
        dash_res = self.client.get(reverse('dashboard'))
        self.assertEqual(dash_res.status_code, 200)
        self.assertContains(dash_res, '125/82')

    def test_pill_reminder_toggle_api(self):
        self.client.login(username='test_patient', password='securepassword123')
        pill = PillReminder.objects.create(
            user=self.user,
            medicine_name='Vitamin D3 5000 IU',
            dosage='1 Softgel',
            time_slot='morning',
            streak_days=10,
            is_taken=False
        )

        toggle_res = self.client.post(f'/api/patient/pill-reminders/{pill.id}/toggle/')
        self.assertEqual(toggle_res.status_code, 200)
        data = toggle_res.json()
        self.assertTrue(data['reminder']['is_taken'])
        self.assertEqual(data['reminder']['streak_days'], 11)

    def test_patient_intake_page_and_submit(self):
        self.client.login(username='test_patient', password='securepassword123')
        
        # 1. Intake Page
        page_res = self.client.get(reverse('intake'))
        self.assertEqual(page_res.status_code, 200)
        self.assertContains(page_res, 'Smart Patient Symptom Intake')

        # 2. Intake API submit
        intake_res = self.client.post('/api/patient/intake/submit/', data={
            'patient_name': 'Arthur Morgan',
            'patient_phone': '+1 (800) 555-0199',
            'primary_symptom': 'High Fever, Severe Headache',
            'pain_severity': 5
        }, content_type='application/json')
        self.assertEqual(intake_res.status_code, 201)
        self.assertIn('intake', intake_res.json())

    def test_health_card_and_invoice_views(self):
        self.client.login(username='test_patient', password='securepassword123')
        
        # Health Card View
        card_res = self.client.get(reverse('health-card'))
        self.assertEqual(card_res.status_code, 200)
        self.assertContains(card_res, 'ANT-P-991823')

        # Consultation Room View
        room_res = self.client.get(reverse('consultation-room', kwargs={'room_id': 'ROOM-TEST-100'}))
        self.assertEqual(room_res.status_code, 200)
        self.assertContains(room_res, 'ROOM-TEST-100')
