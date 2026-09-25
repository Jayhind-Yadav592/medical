import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from apps.pharmacy.models import Category, Brand, Product, Review
from apps.telehealth.models import Doctor
from apps.articles.models import ArticleCategory, Article
from apps.orders.models import Order, OrderItem, Prescription, OrderStatusHistory

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds initial pharmacy database with products, categories, doctors, articles, and test accounts'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding AuraHealth medical database..."))

        # 1. Create Superuser / Admin & Pharmacist accounts
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@aurahealth.pharmacy',
                password='admin',
                first_name='Chief Pharmacist',
                last_name='Alexander',
                user_type='ADMIN',
                phone_number='+1 (800) 584-2872'
            )
            self.stdout.write(self.style.SUCCESS("Created Superuser: admin / admin"))
        else:
            admin_user = User.objects.get(username='admin')

        # Test Patient user
        if not User.objects.filter(username='patient_sarah').exists():
            patient_user = User.objects.create_user(
                username='patient_sarah',
                email='sarah.miller@example.com',
                password='password123',
                first_name='Sarah',
                last_name='Miller',
                user_type='PATIENT',
                phone_number='+1 (212) 555-0199',
                blood_group='O+',
                medical_allergies='Penicillin (Mild)'
            )
            self.stdout.write(self.style.SUCCESS("Created Test Patient: patient_sarah / password123"))
        else:
            patient_user = User.objects.get(username='patient_sarah')

        # 2. Create Categories
        categories_data = [
            {
                'name': 'Prescription Medicines',
                'icon_class': 'fa-solid fa-prescription',
                'description': 'Verified pharmaceutical medicines requiring valid prescription.',
                'order': 1
            },
            {
                'name': 'Over The Counter (OTC)',
                'icon_class': 'fa-solid fa-tablets',
                'description': 'Daily pain relief, cold & flu, allergy, and digestive aids.',
                'order': 2
            },
            {
                'name': 'Vitamins & Immunity',
                'icon_class': 'fa-solid fa-shield-virus',
                'description': 'Essential vitamins, mineral supplements, and immune defense.',
                'order': 3
            },
            {
                'name': 'Chronic Care & Diabetes',
                'icon_class': 'fa-solid fa-heart-pulse',
                'description': 'Hypertension, glucose management, and cardiovascular support.',
                'order': 4
            },
            {
                'name': 'Skincare & Cosmeceuticals',
                'icon_class': 'fa-solid fa-pump-medical',
                'description': 'Dermatologist-recommended clinical skincare and moisturizers.',
                'order': 5
            },
            {
                'name': 'Medical Devices & Diagnostics',
                'icon_class': 'fa-solid fa-stethoscope',
                'description': 'Blood pressure monitors, glucometers, nebulizers, and pulse oximeters.',
                'order': 6
            },
            {
                'name': 'Mother & Baby Care',
                'icon_class': 'fa-solid fa-baby',
                'description': 'Pediatric essentials, baby nutrition, and maternity care.',
                'order': 7
            },
            {
                'name': 'Orthopedic & Pain Relief',
                'icon_class': 'fa-solid fa-bone',
                'description': 'Joint support braces, heating pads, and topical analgesics.',
                'order': 8
            },
        ]

        categories = {}
        for cdata in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cdata['name'],
                defaults={
                    'icon_class': cdata['icon_class'],
                    'description': cdata['description'],
                    'is_featured': True,
                    'order': cdata['order']
                }
            )
            categories[cdata['name']] = cat

        # 3. Create Brands
        brands_data = [
            {'name': 'AuraBio Pharmaceuticals', 'country': 'Switzerland'},
            {'name': 'Novartis Clinical Care', 'country': 'Switzerland'},
            {'name': 'Bayer Healthcare', 'country': 'Germany'},
            {'name': 'Pfizer Biopharma', 'country': 'United States'},
            {'name': 'Abbott Laboratories', 'country': 'United States'},
            {'name': 'Sanofi Consumer Health', 'country': 'France'},
            {'name': 'La Roche-Posay Dermatological', 'country': 'France'},
            {'name': 'Omron Healthcare', 'country': 'Japan'},
        ]
        brands = {}
        for bdata in brands_data:
            b, _ = Brand.objects.get_or_create(name=bdata['name'], defaults={'country': bdata['country']})
            brands[bdata['name']] = b

        # 4. Create Products
        products_data = [
            {
                'name': 'Paracetamol Forte Extra',
                'category': 'Over The Counter (OTC)',
                'brand': 'AuraBio Pharmaceuticals',
                'sku': 'AUR-PARA-500',
                'short_description': 'Fast-acting relief for fever, headache, toothache, and muscular aches.',
                'full_description': 'Paracetamol 500mg tablets provide clinically proven fast analgesia and antipyretic relief. Formulated with fast-release technology for rapid gastric dissolution.',
                'active_ingredient': 'Paracetamol / Acetaminophen 500mg',
                'dosage_form': 'TABLET',
                'dosage_strength': '500mg',
                'pack_size': '20 Tablets / Blister Pack',
                'price': 4.50,
                'mrp_price': 6.50,
                'stock': 450,
                'prescription_required': False,
                'is_featured': True,
                'is_trending': True,
                'is_best_seller': True,
                'rating': 4.9,
                'total_reviews': 342,
                'image_url': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=600&auto=format&fit=crop&q=80',
                'usage_instructions': 'Adults & children 12+: 1-2 tablets every 4-6 hours as required. Max 8 tablets in 24 hours.',
                'side_effects': 'Extremely well tolerated. Consult physician if fever persists > 3 days.',
            },
            {
                'name': 'Amoxicillin Trihydrate Clinical Rx',
                'category': 'Prescription Medicines',
                'brand': 'Novartis Clinical Care',
                'sku': 'AUR-AMOX-500',
                'short_description': 'Broad-spectrum beta-lactam antibiotic for bacterial infections.',
                'full_description': 'Prescription amoxicillin trihydrate 500mg capsules indicated for respiratory tract, ENT, skin, and urinary bacterial infections. Requires certified pharmacist verification.',
                'active_ingredient': 'Amoxicillin Trihydrate 500mg',
                'dosage_form': 'CAPSULE',
                'dosage_strength': '500mg',
                'pack_size': '15 Capsules Bottle',
                'price': 14.80,
                'mrp_price': 19.99,
                'stock': 180,
                'prescription_required': True,
                'is_featured': True,
                'is_trending': False,
                'is_best_seller': True,
                'rating': 4.85,
                'total_reviews': 128,
                'image_url': 'https://images.unsplash.com/photo-1471864190281-a93a3070b6de?w=600&auto=format&fit=crop&q=80',
                'usage_instructions': 'Take one capsule every 8 hours with water. Complete full course as prescribed.',
                'side_effects': 'Mild nausea, diarrhea. Discontinue and call emergency if rash develops.',
            },
            {
                'name': 'Liposomal Vitamin D3 + K2 Complex',
                'category': 'Vitamins & Immunity',
                'brand': 'AuraBio Pharmaceuticals',
                'sku': 'AUR-VITD3-5000',
                'short_description': 'High-potency bone density, arterial health & immune modulation formula.',
                'full_description': 'Bioavailable Vitamin D3 (5000 IU) paired with Vitamin K2 (MK-7 100mcg) in cold-pressed virgin organic coconut oil carrier for maximum systemic absorption.',
                'active_ingredient': 'Cholecalciferol 5000 IU + Menaquinone-7 100mcg',
                'dosage_form': 'CAPSULE',
                'dosage_strength': '5000 IU',
                'pack_size': '60 Softgels Bottle',
                'price': 18.99,
                'mrp_price': 24.99,
                'stock': 220,
                'prescription_required': False,
                'is_featured': True,
                'is_trending': True,
                'is_best_seller': True,
                'rating': 4.98,
                'total_reviews': 512,
                'image_url': 'https://images.unsplash.com/photo-1550572017-edd951aa8f72?w=600&auto=format&fit=crop&q=80',
                'usage_instructions': 'Take 1 softgel daily with a fat-containing meal for optimum uptake.',
                'side_effects': 'Non-toxic at recommended dosage.',
            },
            {
                'name': 'Ultra Pure Triple Strength Omega-3 Fish Oil',
                'category': 'Vitamins & Immunity',
                'brand': 'Abbott Laboratories',
                'sku': 'AUR-OMEGA-1200',
                'short_description': 'Molecularly distilled EPA 720mg & DHA 480mg for heart & brain vitality.',
                'full_description': 'Wild-caught deep sea fish oil with enteric coating to prevent fishy aftertaste. Supports cholesterol balance, joint flexibility, and cognitive focus.',
                'active_ingredient': 'Omega-3 Fatty Acids (EPA 720mg / DHA 480mg)',
                'dosage_form': 'CAPSULE',
                'dosage_strength': '1200mg',
                'pack_size': '90 Softgels',
                'price': 22.50,
                'mrp_price': 29.99,
                'stock': 310,
                'prescription_required': False,
                'is_featured': True,
                'is_trending': True,
                'is_best_seller': False,
                'rating': 4.92,
                'total_reviews': 280,
                'image_url': 'https://images.unsplash.com/photo-1577401239170-897942555fb3?w=600&auto=format&fit=crop&q=80',
                'usage_instructions': 'Take 2 softgels daily with breakfast or dinner.',
                'side_effects': 'None reported.',
            },
            {
                'name': 'Metformin HCl Prolonged Release 500mg',
                'category': 'Chronic Care & Diabetes',
                'brand': 'Sanofi Consumer Health',
                'sku': 'AUR-MET-500PR',
                'short_description': 'First-line glycemic control medication for Type 2 Diabetes management.',
                'full_description': 'Extended release formulation minimizing gastrointestinal symptoms while maintaining stable 24-hour plasma glucose control.',
                'active_ingredient': 'Metformin Hydrochloride 500mg',
                'dosage_form': 'TABLET',
                'dosage_strength': '500mg',
                'pack_size': '30 Extended-Release Tablets',
                'price': 9.20,
                'mrp_price': 12.50,
                'stock': 190,
                'prescription_required': True,
                'is_featured': True,
                'is_trending': False,
                'is_best_seller': True,
                'rating': 4.88,
                'total_reviews': 96,
                'image_url': 'https://images.unsplash.com/photo-1585435557343-3b092031a831?w=600&auto=format&fit=crop&q=80',
                'usage_instructions': 'Take 1 tablet daily with evening meal. Swallow whole, do not crush.',
                'side_effects': 'Mild metallic taste or GI disturbance during initial 2 weeks.',
            },
            {
                'name': 'Cicaplast Baume B5+ Ultra Repair Barrier Cream',
                'category': 'Skincare & Cosmeceuticals',
                'brand': 'La Roche-Posay Dermatological',
                'sku': 'AUR-CICA-100',
                'short_description': 'Dermatological multi-purpose soothing balm with Madecassoside & 5% Panthenol.',
                'full_description': 'Accelerates skin barrier recovery for irritated, chapped, post-procedure skin. Pediatric & adult safe, non-comedogenic, fragrance-free.',
                'active_ingredient': 'Panthenol 5% + Madecassoside + Tribioma Prebiotic',
                'dosage_form': 'CREAM',
                'dosage_strength': '100ml',
                'pack_size': '100ml Tube',
                'price': 17.50,
                'mrp_price': 21.00,
                'stock': 140,
                'prescription_required': False,
                'is_featured': True,
                'is_trending': True,
                'is_best_seller': True,
                'rating': 4.96,
                'total_reviews': 640,
                'image_url': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=600&auto=format&fit=crop&q=80',
                'usage_instructions': 'Apply twice daily to clean, dry skin on face or body.',
                'side_effects': 'None. Hypoallergenic formula.',
            },
            {
                'name': 'Omron Evolv Wireless Upper Arm BP Monitor',
                'category': 'Medical Devices & Diagnostics',
                'brand': 'Omron Healthcare',
                'sku': 'AUR-OMRON-BP',
                'short_description': 'Clinically validated, all-in-one Bluetooth smart blood pressure machine.',
                'full_description': 'No tubes, no wires. High-precision 360-degree Intelli Wrap cuff fits standard to large adult arms. Syncs instantly to AuraHealth and Apple Health.',
                'active_ingredient': 'Digital Oscillometric Sensor',
                'dosage_form': 'DEVICE',
                'dosage_strength': 'Smart Device',
                'pack_size': '1 Device Unit with Carry Pouch',
                'price': 79.99,
                'mrp_price': 99.99,
                'stock': 45,
                'prescription_required': False,
                'is_featured': True,
                'is_trending': True,
                'is_best_seller': True,
                'rating': 4.94,
                'total_reviews': 188,
                'image_url': 'https://images.unsplash.com/photo-1579684385127-1ef15d508118?w=600&auto=format&fit=crop&q=80',
                'usage_instructions': 'Wrap cuff 1-2cm above elbow bend, sit relaxed and press Start button.',
                'side_effects': 'N/A',
            },
            {
                'name': 'Aspirin Cardio 81mg Low Dose Antiplatelet',
                'category': 'Chronic Care & Diabetes',
                'brand': 'Bayer Healthcare',
                'sku': 'AUR-ASP-81',
                'short_description': 'Enteric coated low-dose aspirin for cardiovascular protection.',
                'full_description': 'Prevents blood clotting and reduces risk of secondary cardiovascular incidents under doctor supervision.',
                'active_ingredient': 'Acetylsalicylic Acid 81mg',
                'dosage_form': 'TABLET',
                'dosage_strength': '81mg',
                'pack_size': '100 Delayed-Release Tablets',
                'price': 8.50,
                'mrp_price': 11.00,
                'stock': 380,
                'prescription_required': False,
                'is_featured': False,
                'is_trending': True,
                'is_best_seller': True,
                'rating': 4.90,
                'total_reviews': 210,
                'image_url': 'https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=600&auto=format&fit=crop&q=80',
                'usage_instructions': 'Take 1 tablet daily with water as directed by your physician.',
                'side_effects': 'Avoid if history of active gastric ulcers.',
            },
            {
                'name': 'Cetirizine 24-Hour Non-Drowsy Allergy Relief',
                'category': 'Over The Counter (OTC)',
                'brand': 'Bayer Healthcare',
                'sku': 'AUR-CET-10',
                'short_description': 'Instant all-day defense against hay fever, pollen, dust & hives.',
                'full_description': 'Potent second-generation antihistamine offering rapid 24-hour relief from runny nose, itchy watery eyes, and sneezing without causing drowsiness.',
                'active_ingredient': 'Cetirizine Hydrochloride 10mg',
                'dosage_form': 'TABLET',
                'dosage_strength': '10mg',
                'pack_size': '30 Film-Coated Tablets',
                'price': 9.99,
                'mrp_price': 14.50,
                'stock': 260,
                'prescription_required': False,
                'is_featured': False,
                'is_trending': True,
                'is_best_seller': True,
                'rating': 4.88,
                'total_reviews': 315,
                'image_url': 'https://images.unsplash.com/photo-1550572017-edd951aa8f72?w=600&auto=format&fit=crop&q=80',
                'usage_instructions': 'Take 1 tablet (10mg) once daily with or without food.',
                'side_effects': 'Occasional dry mouth.',
            },
            {
                'name': 'Hyaluronic Acid + Ceramide Restorative Serum',
                'category': 'Skincare & Cosmeceuticals',
                'brand': 'AuraBio Pharmaceuticals',
                'sku': 'AUR-HA-SERUM',
                'short_description': 'Multi-molecular weight hydration booster with 3 essential ceramides.',
                'full_description': 'Plumps fine lines and reinforces the epidermal barrier with 2% pure hyaluronic acid and clinical grade niacinamide.',
                'active_ingredient': 'Hyaluronic Acid 2% + Niacinamide 4% + Ceramides NP/AP',
                'dosage_form': 'DROPS',
                'dosage_strength': '30ml Dropper',
                'pack_size': '30ml Glass Bottle',
                'price': 24.00,
                'mrp_price': 32.00,
                'stock': 95,
                'prescription_required': False,
                'is_featured': True,
                'is_trending': True,
                'is_best_seller': False,
                'rating': 4.95,
                'total_reviews': 145,
                'image_url': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=600&auto=format&fit=crop&q=80',
                'usage_instructions': 'Apply 3-4 drops morning and night to damp skin prior to moisturizer.',
                'side_effects': 'None. Fragrance & paraben free.',
            },
            {
                'name': 'Infant Liquid Paracetamol Drops with Syringe',
                'category': 'Mother & Baby Care',
                'brand': 'AuraBio Pharmaceuticals',
                'sku': 'AUR-PED-PARA',
                'short_description': 'Gentle fever and teething pain relief formulated for infants 1-24 months.',
                'full_description': 'Dye-free, sugar-free infant oral suspension with calibrated oral dosage syringe for pinpoint pediatric accuracy.',
                'active_ingredient': 'Paracetamol 100mg / ml',
                'dosage_form': 'SYRUP',
                'dosage_strength': '100mg/ml',
                'pack_size': '30ml Bottle with Dropper Syringe',
                'price': 7.99,
                'mrp_price': 10.50,
                'stock': 160,
                'prescription_required': False,
                'is_featured': False,
                'is_trending': False,
                'is_best_seller': True,
                'rating': 4.97,
                'total_reviews': 230,
                'image_url': 'https://images.unsplash.com/photo-1631549916768-4119b2e5f926?w=600&auto=format&fit=crop&q=80',
                'usage_instructions': 'Administer weight-adjusted dosage using enclosed calibrated dropper.',
                'side_effects': 'Safe when dosed according to baby weight guide.',
            },
            {
                'name': 'Ergonomic Compression Knee Brace Support',
                'category': 'Orthopedic & Pain Relief',
                'brand': 'Omron Healthcare',
                'sku': 'AUR-ORTHO-KNEE',
                'short_description': 'Medical-grade 3D knit knee sleeve with silicone patella gel pads.',
                'full_description': 'Provides targeted stabilization, joint relief, and pain mitigation for arthritis, meniscus tears, running, and athletic recovery.',
                'active_ingredient': 'Breathable Neoprene & Spandex Matrix',
                'dosage_form': 'DEVICE',
                'dosage_strength': 'Adjustable L/XL',
                'pack_size': '1 Pair (2 Braces)',
                'price': 28.00,
                'mrp_price': 38.00,
                'stock': 85,
                'prescription_required': False,
                'is_featured': False,
                'is_trending': False,
                'is_best_seller': True,
                'rating': 4.91,
                'total_reviews': 175,
                'image_url': 'https://images.unsplash.com/photo-1584017911766-d451b3d0e843?w=600&auto=format&fit=crop&q=80',
                'usage_instructions': 'Pull sleeve over knee centering the patella ring over kneecap.',
                'side_effects': 'None.',
            }
        ]

        for pdata in products_data:
            cat = categories.get(pdata['category'])
            br = brands.get(pdata['brand'])
            p, created = Product.objects.get_or_create(
                sku=pdata['sku'],
                defaults={
                    'name': pdata['name'],
                    'category': cat,
                    'brand': br,
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
                    'is_trending': pdata['is_trending'],
                    'is_best_seller': pdata['is_best_seller'],
                    'rating': pdata['rating'],
                    'total_reviews': pdata['total_reviews'],
                    'image_url': pdata['image_url'],
                    'usage_instructions': pdata['usage_instructions'],
                    'side_effects': pdata['side_effects'],
                }
            )
            if created:
                # Add sample verified review
                Review.objects.create(
                    product=p,
                    user=patient_user,
                    rating=5,
                    title='Authentic medication & super fast delivery!',
                    comment=f'Received genuine {p.name} in pristine temperature-sealed packaging within 45 minutes.',
                    is_verified_purchase=True
                )

        # 5. Create Doctors & Clinical Pharmacists
        doctors_data = [
            {
                'full_name': 'Dr. Elena Vance, PharmD',
                'title': 'Lead Clinical Pharmacist & Drug Safety Specialist',
                'specialty': 'CLINICAL_PHARMACIST',
                'qualification': 'PharmD (Johns Hopkins), Board Certified Pharmacotherapy Specialist (BCPS)',
                'experience_years': 12,
                'bio': 'Specializes in complex medication therapy management, drug-drug interaction screening, chronic disease prescription optimization, and patient therapeutic counseling.',
                'avatar_url': 'https://images.unsplash.com/photo-1594824813629-6126622830f6?w=600&auto=format&fit=crop&q=80',
                'consultation_fee': 0.00,  # Free triage
                'rating': 4.98,
                'reviews_count': 380,
                'is_available_online': True,
                'next_available_slot': 'Available Now (Queue: 2 mins)',
                'languages_spoken': 'English, French'
            },
            {
                'full_name': 'Dr. Marcus Sterling, MD',
                'title': 'Senior Consultant Physician & Internal Medicine',
                'specialty': 'GENERAL_PHYSICIAN',
                'qualification': 'MD (Harvard Medical School), Fellow of American College of Physicians (FACP)',
                'experience_years': 16,
                'bio': 'Expert in primary preventative health, hypertension, metabolic disorders, acute respiratory infections, and virtual clinical telehealth consults.',
                'avatar_url': 'https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=600&auto=format&fit=crop&q=80',
                'consultation_fee': 25.00,
                'rating': 4.95,
                'reviews_count': 295,
                'is_available_online': True,
                'next_available_slot': 'Today at 3:15 PM',
                'languages_spoken': 'English, Spanish'
            },
            {
                'full_name': 'Dr. Aria Chen, MD, FAAD',
                'title': 'Consultant Dermatologist & Clinical Cosmetologist',
                'specialty': 'DERMATOLOGIST',
                'qualification': 'MD (Stanford University), American Academy of Dermatology Certified',
                'experience_years': 10,
                'bio': 'Specializing in acne vulgaris, eczema barrier restoration, prescription retinoids, psoriasis treatment, and bespoke clinical skincare protocols.',
                'avatar_url': 'https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=600&auto=format&fit=crop&q=80',
                'consultation_fee': 35.00,
                'rating': 4.97,
                'reviews_count': 410,
                'is_available_online': True,
                'next_available_slot': 'Today at 4:30 PM',
                'languages_spoken': 'English, Mandarin'
            },
        ]

        for ddata in doctors_data:
            Doctor.objects.get_or_create(
                full_name=ddata['full_name'],
                defaults=ddata
            )

        # 6. Create Health Articles & Clinical Journal
        art_cat_wellness, _ = ArticleCategory.objects.get_or_create(name='Wellness & Immunity', defaults={'description': 'Evidence-based preventative nutrition and immune biology.'})
        art_cat_clinical, _ = ArticleCategory.objects.get_or_create(name='Medication Safety', defaults={'description': 'Proper drug administration, dosage rules, and safety alerts.'})
        art_cat_lifestyle, _ = ArticleCategory.objects.get_or_create(name='Chronic Care & Longevity', defaults={'description': 'Managing blood pressure, diabetes, and cardiovascular wellness.'})

        articles_data = [
            {
                'title': '5 Essential Vitamins & Micronutrients for a Resilient Immune System',
                'category': art_cat_wellness,
                'excerpt': 'Explore the clinical biochemistry behind Vitamin D3, Zinc, Liposomal Vitamin C, and how synergistic nutrient timing strengthens T-cell defenses.',
                'content': '''### The Immunology of Micronutrients
A strong immune system is not built overnight; it requires a steady supply of micronutrients that regulate cellular immunity, phagocytosis, and antibody production.

#### 1. Vitamin D3 (Cholecalciferol)
Vitamin D is more than a vitamin—it functions as a key immunomodulatory hormone. Receptors for Vitamin D (*VDR*) are present on virtually all immune cells, including B lymphocytes, T lymphocytes, and antigen-presenting cells. Studies show maintaining serum 25(OH)D levels between **40–60 ng/mL** significantly reduces susceptibility to acute upper respiratory tract infections.

#### 2. Zinc Picolinate / Bisglycinate
Zinc is essential for enzymatic activity that controls DNA replication and normal development of natural killer (NK) cells. Taking elemental zinc within 24 hours of cold symptoms has been clinically shown to reduce symptom duration by up to 33%.

#### 3. Liposomal Vitamin C
Unlike standard ascorbic acid, which has low bioavailability at high oral doses due to intestinal transporter saturation, liposomal encapsulation shields Vitamin C in phospholipid spheres, delivering up to 3x higher intracellular concentrations directly to leukocyte reserves.

#### Clinical Recommendation
Always pair fat-soluble vitamins (D3, K2, E) with dietary lipids for optimal bioavailability.''',
                'cover_image_url': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=800&auto=format&fit=crop&q=80',
                'author_name': 'Dr. Marcus Sterling, MD',
                'author_title': 'Senior Consultant Physician',
                'medical_reviewer': 'Dr. Elena Vance, PharmD (BCPS Certified)',
                'read_time_minutes': 5,
                'tags': 'Immunity, Vitamin D, Zinc, Preventive Health',
                'is_featured': True,
            },
            {
                'title': 'How to Manage Chronic Stress: Cortisol, Heart Health & Sleep Hygiene',
                'category': art_cat_lifestyle,
                'excerpt': 'Clinical insights into how chronic hypothalamic-pituitary-adrenal axis activation affects vascular elasticity, blood sugar, and evidence-based relaxation strategies.',
                'content': '''### The Physiology of Chronic Cortisol Elevation
When life stressors become persistent, the adrenal cortex continues to secrete cortisol and catecholamines. Over time, elevated systemic cortisol levels lead to insulin resistance, endothelial inflammation, elevated resting blood pressure, and suppressed nocturnal melatonin synthesis.

#### Key Strategies for Adrenal Resilience
1. **Circadian Entrainment**: View 10–15 minutes of natural sunlight within 30 minutes of waking to trigger healthy cortisol morning spikes and set the 14-hour melatonin timer.
2. **Magnesium Glycinate Supplementation**: Magnesium acts as a natural NMDA receptor blocker and GABA agonist, promoting deep slow-wave restorative sleep without morning grogginess.
3. **Controlled Breathwork**: Practicing resonant frequency breathing (5.5 seconds inhale, 5.5 seconds exhale) stimulates the vagus nerve and activates parasympathetic tone within 3 minutes.''',
                'cover_image_url': 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&auto=format&fit=crop&q=80',
                'author_name': 'Dr. Elena Vance, PharmD',
                'author_title': 'Lead Clinical Pharmacist',
                'medical_reviewer': 'Dr. Sophia Chen, MD (Board Certified Cardiologist)',
                'read_time_minutes': 6,
                'tags': 'Mental Health, Sleep, Cortisol, Magnesium',
                'is_featured': True,
            },
            {
                'title': 'Simple Daily Habits for Long-Term Cardiovascular & Metabolic Vitality',
                'category': art_cat_clinical,
                'excerpt': 'Actionable, doctor-approved lifestyle modifications: from post-meal glucose walks to omega-3 index optimization.',
                'content': '''### Preserving Endothelial Integrity
The human vascular system spans over 60,000 miles of blood vessels lined by a delicate monolayer of endothelial cells. Protecting this barrier is the single most critical factor in longevity.

#### 1. The 10-Minute Postprandial Walk
A brief, relaxed 10-minute walk immediately following your highest-carbohydrate meal uses the GLUT4 glucose transporter mechanism in skeletal muscle, pulling glucose from circulation without requiring excess insulin spikes.

#### 2. Omega-3 to Omega-6 Balance
Modern diets often feature a 1:20 ratio of Omega-3 to Omega-6 fatty acids, creating systemic pro-inflammatory cascades. Target an **Omega-3 Index > 8%** by consuming wild oily fish or taking high-potency molecularly distilled EPA/DHA softgels daily.''',
                'cover_image_url': 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800&auto=format&fit=crop&q=80',
                'author_name': 'Dr. Aria Chen, MD',
                'author_title': 'Consultant Physician',
                'medical_reviewer': 'Dr. Marcus Sterling, MD',
                'read_time_minutes': 4,
                'tags': 'Cardiology, Nutrition, Longevity, Daily Habits',
                'is_featured': False,
            }
        ]

        for adata in articles_data:
            Article.objects.get_or_create(
                title=adata['title'],
                defaults=adata
            )

        self.stdout.write(self.style.SUCCESS("Successfully seeded AuraHealth database with complete medical catalogue, specialists, and clinical articles!"))
