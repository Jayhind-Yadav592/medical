from rest_framework import serializers
from apps.core.models import (
    User, Address, NewsletterSubscriber, HealthNotification, ContactInquiry,
    MedicalFacility, PatientVital, PillReminder, PatientIntake
)
from apps.pharmacy.models import Category, Brand, Product, Review, WishlistItem
from apps.orders.models import Prescription, Cart, CartItem, Order, OrderItem, OrderStatusHistory
from apps.telehealth.models import Doctor, ConsultationRequest
from apps.articles.models import Article, ArticleCategory


# User Serializers
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name', 
            'user_type', 'digital_health_id', 'phone_number', 'blood_group', 
            'medical_allergies', 'chronic_conditions', 'emergency_contact', 'emergency_phone'
        ]


class MedicalFacilitySerializer(serializers.ModelSerializer):
    facility_type_display = serializers.CharField(source='get_facility_type_display', read_only=True)
    distance_km = serializers.FloatField(read_only=True, default=1.2)

    class Meta:
        model = MedicalFacility
        fields = [
            'id', 'name', 'facility_type', 'facility_type_display', 'license_number',
            'address', 'city', 'state', 'postal_code', 'latitude', 'longitude',
            'phone', 'emergency_hotline', 'email', 'is_24_7', 'ambulance_available',
            'available_beds', 'rating', 'total_reviews', 'services_offered', 'distance_km'
        ]


class PatientVitalSerializer(serializers.ModelSerializer):
    recorded_at_formatted = serializers.DateTimeField(source='recorded_at', format='%b %d, %Y %I:%M %p', read_only=True)

    class Meta:
        model = PatientVital
        fields = [
            'id', 'systolic_bp', 'diastolic_bp', 'blood_sugar', 'heart_rate',
            'spo2', 'weight_kg', 'bmi', 'notes', 'recorded_at', 'recorded_at_formatted'
        ]


class PillReminderSerializer(serializers.ModelSerializer):
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)

    class Meta:
        model = PillReminder
        fields = [
            'id', 'medicine_name', 'dosage', 'frequency', 'frequency_display',
            'time_slot', 'is_taken', 'streak_days', 'notes', 'updated_at'
        ]


class PatientIntakeSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    facility_name = serializers.CharField(source='allocated_facility.name', read_only=True)

    class Meta:
        model = PatientIntake
        fields = [
            'id', 'patient_name', 'patient_email', 'patient_phone', 'patient_age',
            'patient_gender', 'primary_symptom', 'symptoms_list', 'pain_severity',
            'symptom_duration', 'allocated_facility', 'facility_name', 'status',
            'status_display', 'pharmacist_notes', 'safety_warning', 'created_at'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone_number']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
        )
        return user


# Pharmacy Serializers
class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(source='products.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon_class', 'product_count', 'is_featured', 'order']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'country']


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.full_name', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user_name', 'rating', 'title', 'comment', 'is_verified_purchase', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, default="AuraBio Labs")
    image_display = serializers.CharField(source='get_image', read_only=True)
    dosage_form_display = serializers.CharField(source='get_dosage_form_display', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'category', 'category_name', 'category_slug',
            'brand_name', 'short_description', 'active_ingredient', 'dosage_form',
            'dosage_form_display', 'dosage_strength', 'pack_size', 'price', 'mrp_price',
            'discount_percent', 'stock', 'in_stock', 'prescription_required',
            'is_featured', 'is_trending', 'is_best_seller', 'rating', 'total_reviews',
            'image_display'
        ]


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    image_display = serializers.CharField(source='get_image', read_only=True)
    dosage_form_display = serializers.CharField(source='get_dosage_form_display', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'category', 'brand', 'short_description',
            'full_description', 'active_ingredient', 'dosage_form', 'dosage_form_display',
            'dosage_strength', 'pack_size', 'price', 'mrp_price', 'discount_percent',
            'stock', 'in_stock', 'prescription_required', 'is_featured', 'is_trending',
            'is_best_seller', 'rating', 'total_reviews', 'image_display',
            'usage_instructions', 'side_effects', 'storage_condition', 'manufacturer',
            'reviews', 'created_at'
        ]


# Orders & Cart Serializers
class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'unit_price', 'subtotal']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    shipping_fee = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    grand_total = serializers.FloatField(read_only=True)
    requires_prescription = serializers.BooleanField(read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'subtotal', 'shipping_fee', 'grand_total', 'requires_prescription']


class PrescriptionSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Prescription
        fields = [
            'id', 'patient_name', 'patient_phone', 'doctor_name', 'clinic_hospital',
            'prescription_file', 'notes', 'status', 'status_display', 'pharmacist_notes',
            'uploaded_at', 'verified_at'
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'unit_price', 'quantity', 'subtotal']


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'status_display', 'notes', 'updated_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    order_status_display = serializers.CharField(source='get_order_status_display', read_only=True)
    prescription = PrescriptionSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'full_name', 'email', 'phone', 'shipping_address',
            'city', 'postal_code', 'prescription', 'total_amount', 'shipping_fee',
            'discount_amount', 'final_amount', 'payment_method', 'payment_method_display',
            'payment_status', 'order_status', 'order_status_display', 'tracking_number',
            'estimated_delivery', 'delivery_notes', 'items', 'status_history', 'created_at'
        ]


# Telehealth Serializers
class DoctorSerializer(serializers.ModelSerializer):
    avatar_display = serializers.CharField(source='get_avatar', read_only=True)
    specialty_display = serializers.CharField(source='get_specialty_display', read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id', 'full_name', 'title', 'specialty', 'specialty_display', 'qualification',
            'experience_years', 'bio', 'avatar_display', 'consultation_fee', 'rating',
            'reviews_count', 'is_available_online', 'next_available_slot', 'languages_spoken'
        ]


class ConsultationRequestSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    doctor_specialty = serializers.CharField(source='doctor.get_specialty_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ConsultationRequest
        fields = [
            'id', 'doctor', 'doctor_name', 'doctor_specialty', 'patient_name',
            'patient_email', 'patient_phone', 'patient_age', 'patient_gender',
            'preferred_date', 'preferred_time_slot', 'consultation_type',
            'symptoms', 'medical_history', 'prescription_attachment',
            'status', 'status_display', 'meeting_link', 'created_at'
        ]


# Articles Serializers
class ArticleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleCategory
        fields = ['id', 'name', 'slug']


class ArticleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    cover_image_display = serializers.CharField(source='get_cover_image', read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'category', 'category_name', 'excerpt', 'content',
            'cover_image_display', 'author_name', 'author_title', 'author_avatar',
            'medical_reviewer', 'read_time_minutes', 'tags', 'views_count',
            'is_featured', 'published_at'
        ]


# Advanced Medical Facility & Patient Biometrics Serializers
from apps.core.models import MedicalFacility, PatientVital, PillReminder, PatientIntake

class MedicalFacilitySerializer(serializers.ModelSerializer):
    facility_type_display = serializers.CharField(source='get_facility_type_display', read_only=True)

    class Meta:
        model = MedicalFacility
        fields = [
            'id', 'name', 'facility_type', 'facility_type_display', 'license_number',
            'address', 'city', 'state', 'postal_code', 'latitude', 'longitude',
            'phone', 'emergency_hotline', 'email', 'is_24_7', 'ambulance_available',
            'available_beds', 'rating', 'total_reviews', 'services_offered'
        ]


class PatientVitalSerializer(serializers.ModelSerializer):
    blood_pressure = serializers.CharField(read_only=True)

    class Meta:
        model = PatientVital
        fields = [
            'id', 'systolic_bp', 'diastolic_bp', 'blood_pressure', 'blood_sugar',
            'heart_rate', 'spo2', 'weight_kg', 'bmi', 'notes', 'recorded_at'
        ]


class PillReminderSerializer(serializers.ModelSerializer):
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)

    class Meta:
        model = PillReminder
        fields = [
            'id', 'medicine_name', 'dosage', 'frequency', 'frequency_display',
            'time_slot', 'is_taken', 'streak_days', 'notes', 'created_at'
        ]


class PatientIntakeSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    allocated_facility_name = serializers.CharField(source='allocated_facility.name', read_only=True)

    class Meta:
        model = PatientIntake
        fields = [
            'id', 'patient_name', 'patient_email', 'patient_phone', 'patient_age',
            'patient_gender', 'primary_symptom', 'symptoms_list', 'pain_severity',
            'symptom_duration', 'allocated_facility', 'allocated_facility_name',
            'status', 'status_display', 'pharmacist_notes', 'safety_warning', 'created_at'
        ]

