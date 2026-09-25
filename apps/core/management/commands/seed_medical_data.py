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
                'avatar_url': '/static/images/doctor_male.jpg',
                'consultation_fee': 0.00,
                'is_available_online': True,
                'next_available_slot': 'Available Now (24/7)',
            }
        )

        self.stdout.write(self.style.SUCCESS("Antixor Pharmacy database seeded successfully!"))
