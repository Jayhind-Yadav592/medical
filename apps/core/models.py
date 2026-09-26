import math
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
    digital_health_id = models.CharField(max_length=30, blank=True, null=True, unique=True, help_text="Unique Digital Health ID like ANT-P-882194")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    blood_group = models.CharField(max_length=10, blank=True, null=True, default='O+')
    medical_allergies = models.TextField(blank=True, null=True, help_text="e.g. Penicillin, Sulfa drugs, Aspirin")
    chronic_conditions = models.TextField(blank=True, null=True, help_text="e.g. Type 2 Diabetes, Hypertension, Asthma")
    emergency_contact = models.CharField(max_length=100, blank=True, null=True, help_text="Contact Person Name")
    emergency_phone = models.CharField(max_length=30, blank=True, null=True, help_text="Emergency Phone Number")
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    @property
    def full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username

    def save(self, *args, **kwargs):
        if not self.digital_health_id:
            import random
            rand_id = random.randint(100000, 999999)
            self.digital_health_id = f"ANT-P-{rand_id}"
        super().save(*args, **kwargs)


class MedicalFacility(models.Model):
    """Hospital, Pharmacy, or Diagnostic Center for Geo-Location Allocation."""
    FACILITY_TYPE_CHOICES = (
        ('PHARMACY', 'Antixor Certified Pharmacy & Store'),
        ('HOSPITAL', 'Partner Multi-Specialty Hospital'),
        ('EMERGENCY_CENTER', '24/7 Trauma & Emergency Center'),
        ('DIAGNOSTIC_LAB', 'Certified Diagnostic & Pathology Lab'),
    )

    name = models.CharField(max_length=200)
    facility_type = models.CharField(max_length=30, choices=FACILITY_TYPE_CHOICES, default='PHARMACY')
    license_number = models.CharField(max_length=100, blank=True, null=True)
    
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, default='New York')
    state = models.CharField(max_length=100, default='NY')
    postal_code = models.CharField(max_length=20, default='10001')
    
    # GPS Coordinates
    latitude = models.FloatField(default=40.7128)
    longitude = models.FloatField(default=-74.0060)
    
    phone = models.CharField(max_length=30)
    emergency_hotline = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    is_24_7 = models.BooleanField(default=True)
    ambulance_available = models.BooleanField(default=False)
    available_beds = models.IntegerField(default=0, help_text="Applicable for hospitals")
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.9)
    total_reviews = models.IntegerField(default=120)
    
    services_offered = models.TextField(blank=True, null=True, help_text="Comma-separated: Cold-chain storage, ICU, 24/7 Dispensing, Lab Sampling")
    image = models.ImageField(upload_to='facilities/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Medical Facilities"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_facility_type_display()}) - {self.city}"

    def calculate_distance(self, user_lat, user_lng):
        """Haversine formula to compute geodesic distance in kilometers."""
        try:
            lat1, lon1 = math.radians(float(user_lat)), math.radians(float(user_lng))
            lat2, lon2 = math.radians(self.latitude), math.radians(self.longitude)
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
            c = 2 * math.asin(math.sqrt(a))
            r = 6371  # Earth radius in km
            return round(c * r, 2)
        except Exception:
            return 1.5


class PatientVital(models.Model):
    """Historical health vitals tracking for patient dashboard."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vitals')
    systolic_bp = models.IntegerField(default=120, help_text="Systolic Blood Pressure (mmHg)")
    diastolic_bp = models.IntegerField(default=80, help_text="Diastolic Blood Pressure (mmHg)")
    blood_sugar = models.FloatField(default=95.0, help_text="Fasting Blood Sugar (mg/dL)")
    heart_rate = models.IntegerField(default=72, help_text="Heart Rate (BPM)")
    spo2 = models.IntegerField(default=98, help_text="Oxygen Saturation (%)")
    weight_kg = models.FloatField(default=68.5, help_text="Weight in KG")
    bmi = models.FloatField(default=22.4, help_text="Body Mass Index")
    notes = models.CharField(max_length=255, blank=True, null=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-recorded_at']

    @property
    def blood_pressure(self):
        return f"{self.systolic_bp}/{self.diastolic_bp}"

    def __str__(self):
        return f"Vitals for {self.user.username} at {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"


class PillReminder(models.Model):
    """Daily medication schedule & reminder tracker."""
    FREQUENCY_CHOICES = (
        ('MORNING', 'Morning (8:00 AM)'),
        ('AFTERNOON', 'Afternoon (1:00 PM)'),
        ('NIGHT', 'Night (9:00 PM)'),
        ('TWICE_DAILY', 'Twice Daily (Morning & Night)'),
        ('THRICE_DAILY', 'Thrice Daily'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pill_reminders')
    medicine_name = models.CharField(max_length=150)
    dosage = models.CharField(max_length=50, default="1 Tablet after meal")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='MORNING')
    time_slot = models.CharField(max_length=50, default="08:00 AM")
    is_taken = models.BooleanField(default=False)
    streak_days = models.IntegerField(default=5)
    notes = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['time_slot', 'medicine_name']

    @property
    def medication_name(self):
        return self.medicine_name

    def __str__(self):
        return f"{self.medicine_name} ({self.frequency}) for {self.user.username}"


class PatientIntake(models.Model):
    """Smart Multi-step Patient Symptom Intake & Pharmacy Allocation."""
    STATUS_CHOICES = (
        ('SUBMITTED', 'Intake Submitted'),
        ('PHARMACIST_ALLOCATED', 'Assigned to Nearest Pharmacy'),
        ('CLINICAL_REVIEW', 'Clinical Pharmacist Reviewing'),
        ('PRESCRIPTION_APPROVED', 'Prescription & Dosage Approved'),
        ('DISPATCHED', 'Dispatched for 2-Hour Delivery'),
        ('COMPLETED', 'Completed'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='intakes')
    patient_name = models.CharField(max_length=150)
    patient_email = models.EmailField(blank=True, null=True)
    patient_phone = models.CharField(max_length=30)
    patient_age = models.IntegerField(default=28)
    patient_gender = models.CharField(max_length=20, default='Female')
    
    primary_symptom = models.CharField(max_length=200, default='Severe Headache & Low Fever')
    symptoms_list = models.TextField(blank=True, null=True, help_text="Comma-separated symptoms selected by patient")
    pain_severity = models.IntegerField(default=4, help_text="Scale from 1 (mild) to 10 (emergency)")
    symptom_duration = models.CharField(max_length=100, default="2-3 Days")
    
    prescription_attachment = models.FileField(upload_to='intake_prescriptions/%Y/%m/', blank=True, null=True)
    allocated_facility = models.ForeignKey(MedicalFacility, on_delete=models.SET_NULL, null=True, blank=True, related_name='allocated_intakes')
    
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='SUBMITTED')
    pharmacist_notes = models.TextField(blank=True, null=True)
    safety_warning = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def symptoms(self):
        return self.symptoms_list or self.primary_symptom

    def __str__(self):
        return f"Intake #{self.id} for {self.patient_name} ({self.get_status_display()})"


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

