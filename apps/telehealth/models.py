from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Doctor(models.Model):
    SPECIALTY_CHOICES = (
        ('CLINICAL_PHARMACIST', 'Lead Clinical Pharmacist (PharmD)'),
        ('GENERAL_PHYSICIAN', 'General Physician & Family Medicine'),
        ('PEDIATRICIAN', 'Pediatrics & Child Health Specialist'),
        ('DERMATOLOGIST', 'Dermatology & Cosmetology'),
        ('CARDIOLOGIST', 'Cardiology & Hypertension Specialist'),
        ('NUTRITIONIST', 'Clinical Dietitian & Nutritionist'),
        ('ENDOCRINOLOGIST', 'Endocrinology & Diabetes Specialist'),
    )
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='doctor_profile', null=True, blank=True)
    full_name = models.CharField(max_length=150)
    title = models.CharField(max_length=100, default='PharmD, Lead Clinical Pharmacist')
    specialty = models.CharField(max_length=40, choices=SPECIALTY_CHOICES, default='CLINICAL_PHARMACIST')
    license_number = models.CharField(max_length=50, default='LIC-US-98432')
    qualification = models.CharField(max_length=200, default='PharmD, Board Certified Pharmacotherapy Specialist')
    experience_years = models.PositiveIntegerField(default=10)
    bio = models.TextField()
    
    avatar = models.ImageField(upload_to='doctors/', blank=True, null=True)
    avatar_url = models.URLField(max_length=500, blank=True, null=True)
    
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text="0 for Free Triage")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.95, validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    reviews_count = models.PositiveIntegerField(default=140)
    
    is_available_online = models.BooleanField(default=True)
    next_available_slot = models.CharField(max_length=100, default='Today at 2:30 PM')
    languages_spoken = models.CharField(max_length=200, default='English, Spanish')
    
    is_featured = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-rating']
        
    @property
    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        if self.avatar_url:
            return self.avatar_url
        return '/static/images/placeholder_doctor.png'
        
    def __str__(self):
        return f"{self.full_name} ({self.get_specialty_display()})"


class ConsultationRequest(models.Model):
    CONSULTATION_TYPE_CHOICES = (
        ('VIDEO', 'High-Definition Video Call'),
        ('AUDIO', 'Direct Phone Call'),
        ('CHAT', 'Encrypted Instant Chat'),
        ('IN_PERSON', 'In-Clinic Priority Appointment'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending Doctor Confirmation'),
        ('CONFIRMED', 'Confirmed & Slot Reserved'),
        ('IN_PROGRESS', 'Consultation Live'),
        ('COMPLETED', 'Completed & Prescription Issued'),
        ('CANCELLED', 'Cancelled'),
    )
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='consultations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='consultations')
    
    patient_name = models.CharField(max_length=150)
    patient_email = models.EmailField()
    patient_phone = models.CharField(max_length=30)
    patient_age = models.PositiveIntegerField(default=30)
    patient_gender = models.CharField(max_length=20, default='Not Specified')
    
    preferred_date = models.DateField()
    preferred_time_slot = models.CharField(max_length=50)
    consultation_type = models.CharField(max_length=20, choices=CONSULTATION_TYPE_CHOICES, default='VIDEO')
    
    symptoms = models.TextField(help_text="Describe primary health symptoms or medication questions")
    medical_history = models.TextField(blank=True, null=True)
    prescription_attachment = models.FileField(upload_to='consultations/rx/', blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    meeting_link = models.URLField(max_length=500, blank=True, null=True)
    doctor_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Consultation with {self.doctor.full_name} for {self.patient_name} on {self.preferred_date}"
