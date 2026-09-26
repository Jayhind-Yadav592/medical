import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.pharmacy.models import Category, Brand, Product, Review
from apps.telehealth.models import Doctor
from apps.articles.models import ArticleCategory, Article
from apps.orders.models import Order, OrderItem, Prescription

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds Antixor Pharmacy database with medicines, categories, articles, and reviews'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding Antixor Pharmacy database..."))

        # 1. Create Superuser / Admin & Patient accounts
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@antixorpharmacy.com',
                password='admin',
                first_name='Lead Pharmacist',
                last_name='Antixor',
                user_type='ADMIN',
                phone_number='+880 1234 567890'
            )
            self.stdout.write(self.style.SUCCESS("Created Superuser: admin / admin"))

        if not User.objects.filter(username='sarah_ahmed').exists():
            patient = User.objects.create_user(
                username='sarah_ahmed',
                email='sarah.ahmed@example.com',
                password='password123',
                first_name='Sarah',
                last_name='Ahmed',
                user_type='PATIENT',
                phone_number='+880 1711 000111',
            )
        else:
            patient = User.objects.get(username='sarah_ahmed')

        # 2. Categories
        categories_data = [
            {'name': 'Pain Relief', 'icon_class': 'fa-solid fa-tablets', 'description': 'Fast-acting pain and fever relief.'},
            {'name': 'Bone & Immunity', 'icon_class': 'fa-solid fa-shield-virus', 'description': 'Essential vitamins and minerals.'},
            {'name': 'Heart Health', 'icon_class': 'fa-solid fa-heart-pulse', 'description': 'Omega fatty acids and cardiovascular care.'},
            {'name': 'Healthy & Glowing Skin', 'icon_class': 'fa-solid fa-spa', 'description': 'Clinical dermatological skincare.'},
            {'name': 'Prescription Medicines', 'icon_class': 'fa-solid fa-prescription', 'description': 'Rx medicines requiring pharmacist validation.'},
            {'name': 'Over The Counter (OTC)', 'icon_class': 'fa-solid fa-pills', 'description': 'Everyday family health essentials.'},
        ]
        categories = {}
        for cdata in categories_data:
            cat, _ = Category.objects.get_or_create(name=cdata['name'], defaults=cdata)
            categories[cdata['name']] = cat

        # 3. Brand
        brand, _ = Brand.objects.get_or_create(name='Antixor Healthcare Ltd.', defaults={'country': 'United States'})

        # 4. Products matching approved UI
        products_data = [
            {
                'name': 'Paracetamol 500mg',
                'category': 'Pain Relief',
                'sku': 'ANT-PARA-500',
                'short_description': 'Fast acting pain relief and fever reduction tablets.',
                'full_description': 'Clinically verified Paracetamol 500mg tablets for effective relief from headaches, body aches, toothaches, and high temperature.',
                'active_ingredient': 'Paracetamol 500mg',
                'dosage_form': 'TABLET',
                'dosage_strength': '500mg',
                'pack_size': '30 Tablets / Box',
                'price': 2.50,
                'mrp_price': 3.50,
                'stock': 500,
                'prescription_required': False,
                'is_featured': True,
                'rating': 5.0,
                'total_reviews': 120,
                'image_url': '/static/images/product_paracetamol.jpg',
            },
            {
                'name': 'Vitamin D3 1000 IU',
                'category': 'Bone & Immunity',
                'sku': 'ANT-VITD3-1000',
                'short_description': 'High-potency bone density and immune support supplement.',
                'full_description': 'Supports strong bone development, calcium metabolism, and healthy immune modulation.',
                'active_ingredient': 'Cholecalciferol 1000 IU',
                'dosage_form': 'CAPSULE',
                'dosage_strength': '1000 IU',
                'pack_size': '60 Softgels Bottle',
                'price': 8.99,
                'mrp_price': 12.00,
                'stock': 350,
                'prescription_required': False,
                'is_featured': True,
                'rating': 4.9,
                'total_reviews': 95,
                'image_url': '/static/images/product_vitamind3.jpg',
            },
            {
                'name': 'Omega 3 Fish Oil',
                'category': 'Heart Health',
                'sku': 'ANT-OMEGA3-1000',
                'short_description': 'Purified EPA & DHA essential fatty acids for cardiovascular and brain health.',
                'full_description': 'Molecularly distilled deep-sea wild fish oil offering maximum omega-3 purity without fishy burps.',
                'active_ingredient': 'Omega-3 EPA/DHA 1000mg',
                'dosage_form': 'CAPSULE',
                'dosage_strength': '1000mg',
                'pack_size': '90 Softgels Bottle',
                'price': 12.99,
                'mrp_price': 16.50,
                'stock': 280,
                'prescription_required': False,
                'is_featured': True,
                'rating': 4.95,
                'total_reviews': 140,
                'image_url': '/static/images/product_omega3.jpg',
            },
            {
                'name': 'Skin Care Cream',
                'category': 'Healthy & Glowing Skin',
                'sku': 'ANT-SKIN-CREAM',
                'short_description': 'Dermatologist formulated barrier moisturizing and repair cream.',
                'full_description': 'Restores natural hydration, soothes dry sensitive skin, and provides deep epidermal nourishment with ceramides.',
                'active_ingredient': 'Ceramides NP/AP + Hyaluronic Acid',
                'dosage_form': 'CREAM',
                'dosage_strength': '50ml Jar',
                'pack_size': '50ml Cream Jar',
                'price': 14.50,
                'mrp_price': 19.00,
                'stock': 190,
                'prescription_required': False,
                'is_featured': True,
                'rating': 4.88,
                'total_reviews': 88,
                'image_url': '/static/images/product_skincare.jpg',
            },
        ]

        for pdata in products_data:
            cat = categories.get(pdata['category'])
            p, _ = Product.objects.get_or_create(
                sku=pdata['sku'],
                defaults={
                    'name': pdata['name'],
                    'category': cat,
                    'brand': brand,
                    'short_description': pdata['short_description'],
                    'full_description': pdata['full_description'],
                    'active_ingredient': pdata['active_ingredient'],
                    'dosage_form': pdata['dosage_form'],
                    'dosage_strength': pdata['dosage_strength'],
                    'pack_size': pdata['pack_size'],
                    'price': pdata['price'],
                    'mrp_price': pdata['mrp_price'],
                    'stock': pdata['stock'],
                    'prescription_required': pdata['prescription_required'],
                    'is_featured': pdata['is_featured'],
                    'rating': pdata['rating'],
                    'total_reviews': pdata['total_reviews'],
                    'image_url': pdata['image_url'],
                }
            )

        # 5. Articles
        art_cat_nutrition, _ = ArticleCategory.objects.get_or_create(name='Nutrition')
        art_cat_wellness, _ = ArticleCategory.objects.get_or_create(name='Wellness')
        art_cat_lifestyle, _ = ArticleCategory.objects.get_or_create(name='Lifestyle')

        articles_data = [
            {
                'title': '5 Essential Vitamins for a Stronger Immune System',
                'category': art_cat_nutrition,
                'excerpt': 'Discover the top micronutrients that bolster cellular immunity and keep your defense system resilient.',
                'content': 'Full evidence-based article detailing Vitamin C, Vitamin D3, Zinc, Selenium, and Vitamin B-Complex.',
                'cover_image_url': '/static/images/article_vitamins.jpg',
                'read_time_minutes': 5,
                'medical_reviewer': 'Dr. Marcus Sterling, MD',
            },
            {
                'title': 'How to Manage Stress for Better Mental Health',
                'category': art_cat_wellness,
                'excerpt': 'Evidence-based strategies to regulate cortisol levels, improve sleep quality, and practice restorative wellness.',
                'content': 'Comprehensive guide on circadian alignment, magnesium supplementation, and vagus nerve breathing techniques.',
                'cover_image_url': '/static/images/article_stress.jpg',
                'read_time_minutes': 6,
                'medical_reviewer': 'Dr. Elena Vance, PharmD',
            },
            {
                'title': 'Simple Daily Habits for a Healthier You',
                'category': art_cat_lifestyle,
                'excerpt': 'Actionable daily health routines for enhanced metabolic vitality and cardiovascular wellness.',
                'content': 'Daily walking after meals, optimal hydration, omega-3 fatty acid intake, and sleep hygiene.',
                'cover_image_url': '/static/images/article_habits.jpg',
                'read_time_minutes': 4,
                'medical_reviewer': 'Dr. Aria Chen, MD',
            },
        ]

        for adata in articles_data:
            Article.objects.get_or_create(title=adata['title'], defaults=adata)

        # 6. Doctor
        Doctor.objects.get_or_create(
            full_name='Dr. Marcus Sterling, MD',
            defaults={
                'title': 'Senior Consultant Physician',
                'specialty': 'GENERAL_PHYSICIAN',
                'qualification': 'MD (Internal Medicine), Board Certified',
                'experience_years': 15,
                'bio': 'Certified clinical consultant ready to provide expert telemedicine evaluations.',
                'avatar_url': '/static/images/hero_doctor.jpg',
                'consultation_fee': 0.00,
                'is_available_online': True,
                'next_available_slot': 'Available Now (24/7)',
            }
        )

        Doctor.objects.get_or_create(
            full_name='Dr. Elena Vance, PharmD',
            defaults={
                'title': 'Lead Clinical Pharmacist & Toxicologist',
                'specialty': 'CLINICAL_PHARMACIST',
                'qualification': 'PharmD, BCPS Board Certified',
                'experience_years': 12,
                'bio': 'Specialist in prescription safety verification, complex drug-allergy interactions, and chronic disease medication management.',
                'avatar_url': '/static/images/pharmacist_female.jpg',
                'consultation_fee': 0.00,
                'is_available_online': True,
                'next_available_slot': 'Available Today 3:00 PM',
            }
        )

        # 7. Seed Medical Facilities (Hospitals, Pharmacies, Labs, Emergency Centers)
        from apps.core.models import MedicalFacility, PatientVital, PillReminder, PatientIntake

        # Update Sarah Ahmed patient profile
        patient.blood_group = 'A+'
        patient.medical_allergies = 'Penicillin, Amoxicillin'
        patient.chronic_conditions = 'Mild Seasonal Asthma'
        patient.emergency_contact = 'Karim Ahmed (Husband)'
        patient.emergency_phone = '+1 (555) 998-0112'
        patient.save()

        facilities_data = [
            {
                'name': 'Antixor Central Flagship Pharmacy & Dispensing Hub',
                'facility_type': 'PHARMACY',
                'license_number': 'LIC-NY-PH-8801',
                'address': '350 5th Avenue, Suite 100',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10118',
                'latitude': 40.7484,
                'longitude': -73.9857,
                'phone': '+1 (800) 268-4967',
                'emergency_hotline': '+1 (800) 268-9999',
                'email': 'central.store@antixorpharmacy.com',
                'is_24_7': True,
                'ambulance_available': False,
                'rating': 4.9,
                'total_reviews': 340,
                'services_offered': '2-Hour Express Delivery, Cold-chain insulin storage, Prescription verification, Blood pressure check'
            },
            {
                'name': 'Mount Sinai Comprehensive Medical Center & Trauma Hospital',
                'facility_type': 'HOSPITAL',
                'license_number': 'HOSP-NY-7721',
                'address': '1 Gustave L. Levy Place',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10029',
                'latitude': 40.7903,
                'longitude': -73.9529,
                'phone': '+1 (212) 241-6500',
                'emergency_hotline': '+1 (212) 241-9111',
                'email': 'er.dispatch@mountsinai.org',
                'is_24_7': True,
                'ambulance_available': True,
                'available_beds': 48,
                'rating': 4.8,
                'total_reviews': 1250,
                'services_offered': 'Level 1 Trauma Emergency, ICU, Cardiac Care, Stroke Unit, In-patient Pharmacy, 24/7 Ambulance'
            },
            {
                'name': 'Antixor Express Pharmacy & Telehealth Clinic (Downtown)',
                'facility_type': 'PHARMACY',
                'license_number': 'LIC-NY-PH-8802',
                'address': '120 Broadway, Financial District',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10271',
                'latitude': 40.7081,
                'longitude': -74.0113,
                'phone': '+1 (212) 555-0144',
                'emergency_hotline': '+1 (212) 555-0199',
                'email': 'downtown@antixorpharmacy.com',
                'is_24_7': True,
                'ambulance_available': False,
                'rating': 4.9,
                'total_reviews': 185,
                'services_offered': 'Walk-in prescription pickup, Telehealth kiosk, Clinical dosage review, Vaccination'
            },
            {
                'name': 'Bellevue NYC Emergency Trauma & General Hospital',
                'facility_type': 'EMERGENCY_CENTER',
                'license_number': 'HOSP-NY-9914',
                'address': '462 1st Avenue',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10016',
                'latitude': 40.7390,
                'longitude': -73.9754,
                'phone': '+1 (212) 562-4141',
                'emergency_hotline': '+1 (212) 562-9911',
                'email': 'emergency@bellevuehealth.org',
                'is_24_7': True,
                'ambulance_available': True,
                'available_beds': 32,
                'rating': 4.7,
                'total_reviews': 890,
                'services_offered': '24/7 Trauma Surgery, Pediatric Emergency, Intensive Care, Fast-Track Triage, Emergency Dispatch'
            },
            {
                'name': 'Antixor BioLab & Diagnostic Pathology Center',
                'facility_type': 'DIAGNOSTIC_LAB',
                'license_number': 'LAB-NY-3301',
                'address': '550 1st Avenue, Suite 400',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10016',
                'latitude': 40.7420,
                'longitude': -73.9740,
                'phone': '+1 (212) 555-0177',
                'email': 'diagnostics@antixorpharmacy.com',
                'is_24_7': False,
                'ambulance_available': False,
                'rating': 4.9,
                'total_reviews': 210,
                'services_offered': 'Complete Blood Panel, Lipid & Thyroid Testing, Urine Pathology, Digital Same-Day PDF Reports'
            }
        ]

        created_facilities = []
        for fac_data in facilities_data:
            fac, _ = MedicalFacility.objects.get_or_create(name=fac_data['name'], defaults=fac_data)
            created_facilities.append(fac)

        # 8. Seed Patient Vitals for Sarah
        PatientVital.objects.get_or_create(
            user=patient,
            systolic_bp=118,
            diastolic_bp=78,
            blood_sugar=94.5,
            heart_rate=72,
            spo2=99,
            weight_kg=64.0,
            bmi=21.8,
            notes='Optimal resting blood pressure & fasting glucose.'
        )

        # 9. Seed Pill Reminders for Sarah
        PillReminder.objects.get_or_create(
            user=patient,
            medicine_name='Vitamin D3 1000 IU',
            dosage='1 Softgel Capsule with breakfast',
            frequency='MORNING',
            time_slot='08:30 AM',
            defaults={'is_taken': True, 'streak_days': 7, 'notes': 'Supports bone density and immune defense.'}
        )

        PillReminder.objects.get_or_create(
            user=patient,
            medicine_name='Omega-3 Fish Oil 1200mg',
            dosage='1 Capsule with dinner',
            frequency='NIGHT',
            time_slot='08:30 PM',
            defaults={'is_taken': False, 'streak_days': 5, 'notes': 'Cardiovascular and cholesterol balance.'}
        )

        # 10. Seed Patient Intake
        if created_facilities:
            PatientIntake.objects.get_or_create(
                user=patient,
                patient_name='Sarah Ahmed',
                patient_phone='+1 (555) 998-0112',
                primary_symptom='Throat Irritation & Low Fever',
                defaults={
                    'patient_email': patient.email,
                    'patient_age': 29,
                    'patient_gender': 'Female',
                    'symptoms_list': 'Sore Throat, Dry Cough, Mild Body Ache',
                    'pain_severity': 3,
                    'symptom_duration': '2 Days',
                    'allocated_facility': created_facilities[0],
                    'status': 'CLINICAL_REVIEW',
                    'pharmacist_notes': 'Prescription verified. Suggested OTC Lozenges and hydration. No penicillin compounds assigned.',
                    'safety_warning': 'Patient has recorded Penicillin allergy. Avoid Amoxicillin / Ampicillin.'
                }
            )

        self.stdout.write(self.style.SUCCESS("Antixor Pharmacy database seeded successfully with Facilities, Vitals & Intake!"))

