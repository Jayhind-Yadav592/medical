from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address, NewsletterSubscriber, HealthNotification, ContactInquiry


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'user_type', 'phone_number', 'is_staff']
    list_filter = ['user_type', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('AuraHealth Profile', {'fields': ('user_type', 'phone_number', 'avatar', 'date_of_birth', 'blood_group', 'medical_allergies', 'emergency_contact')}),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'user', 'street_address', 'city', 'state', 'postal_code', 'address_type', 'is_default']
    list_filter = ['address_type', 'is_default', 'city']
    search_fields = ['full_name', 'street_address', 'phone_number']


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    search_fields = ['email']


@admin.register(HealthNotification)
class HealthNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'subject', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
