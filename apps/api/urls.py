from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, CategoryViewSet, DoctorViewSet, ArticleViewSet,
    AutocompleteAPIView, CartAPIView, WishlistAPIView,
    PrescriptionUploadAPIView, ConsultationBookingAPIView,
    CheckoutAPIView, OrderTrackingAPIView, ReviewCreateAPIView,
    NewsletterAPIView, ContactAPIView,
    AuthRegisterAPIView, AuthLoginAPIView, AuthLogoutAPIView, AuthStatusAPIView,
    FacilityNearestAPIView, EmergencySOSAPIView, SafetyAllergyCheckAPIView,
    PatientVitalsAPIView, PillReminderToggleAPIView, PatientIntakeSubmitAPIView
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='api-products')
router.register(r'categories', CategoryViewSet, basename='api-categories')
router.register(r'doctors', DoctorViewSet, basename='api-doctors')
router.register(r'articles', ArticleViewSet, basename='api-articles')

urlpatterns = [
    # Router endpoints
    path('', include(router.urls)),
    
    # Search & Autocomplete
    path('search/autocomplete/', AutocompleteAPIView.as_view(), name='api-autocomplete'),
    
    # Cart & Wishlist
    path('cart/', CartAPIView.as_view(), name='api-cart'),
    path('wishlist/', WishlistAPIView.as_view(), name='api-wishlist'),
    
    # Prescriptions & Telehealth
    path('prescriptions/upload/', PrescriptionUploadAPIView.as_view(), name='api-prescription-upload'),
    path('consultations/book/', ConsultationBookingAPIView.as_view(), name='api-consultation-book'),
    
    # Orders & Tracking
    path('orders/checkout/', CheckoutAPIView.as_view(), name='api-checkout'),
    path('orders/track/<str:order_number>/', OrderTrackingAPIView.as_view(), name='api-order-track'),
    
    # Reviews & Interactive Feedbacks
    path('products/<slug:product_slug>/reviews/', ReviewCreateAPIView.as_view(), name='api-product-review'),
    
    # Newsletter & Contact
    path('newsletter/subscribe/', NewsletterAPIView.as_view(), name='api-newsletter'),
    path('contact/submit/', ContactAPIView.as_view(), name='api-contact'),
    
    # Authentication & User Profile
    path('auth/status/', AuthStatusAPIView.as_view(), name='api-auth-status'),
    path('auth/register/', AuthRegisterAPIView.as_view(), name='api-auth-register'),
    path('auth/login/', AuthLoginAPIView.as_view(), name='api-auth-login'),
    path('auth/logout/', AuthLogoutAPIView.as_view(), name='api-auth-logout'),
    
    # Geolocation & Facilities Allocation
    path('facilities/nearest/', FacilityNearestAPIView.as_view(), name='api-facility-nearest'),
    path('emergency/sos/', EmergencySOSAPIView.as_view(), name='api-emergency-sos'),
    
    # Clinical Safety & Patient Records
    path('safety/check-allergy/', SafetyAllergyCheckAPIView.as_view(), name='api-safety-allergy'),
    path('patient/vitals/', PatientVitalsAPIView.as_view(), name='api-patient-vitals'),
    path('patient/pill-reminders/<int:reminder_id>/toggle/', PillReminderToggleAPIView.as_view(), name='api-pill-reminder-toggle'),
    path('patient/intake/submit/', PatientIntakeSubmitAPIView.as_view(), name='api-patient-intake-submit'),
]

