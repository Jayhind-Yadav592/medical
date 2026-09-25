from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('PATIENT', 'Patient / Customer'),
        ('PHARMACIST', 'Certified Pharmacist'),
        ('DOCTOR', 'Doctor / Healthcare Specialist'),
        ('ADMIN', 'Administrator'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='PATIENT')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True)
    medical_allergies = models.TextField(blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username


class Address(models.Model):
    ADDRESS_TYPE_CHOICES = (
        ('HOME', 'Home'),
        ('WORK', 'Work'),
        ('OTHER', 'Other'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', null=True, blank=True)
    full_name = models.CharField(max_length=150)
    phone_number = models.CharField(max_length=20)
    street_address = models.CharField(max_length=255)
    apartment_suite = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='United States')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='HOME')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ['-is_default', '-created_at']
        
    def __str__(self):
        return f"{self.full_name}, {self.street_address}, {self.city}"


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.email


class HealthNotification(models.Model):
    NOTIFICATION_TYPES = (
        ('ORDER', 'Order Update'),
        ('PRESCRIPTION', 'Prescription Verification'),
        ('CONSULTATION', 'Doctor Consultation'),
        ('REFILL', 'Medication Refill Reminder'),
        ('SYSTEM', 'System Alert'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='SYSTEM')
    link_url = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.user.username}"


class ContactInquiry(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Contact Inquiries"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.subject} by {self.name}"
