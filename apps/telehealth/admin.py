from django.contrib import admin
from .models import Doctor, ConsultationRequest


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'specialty', 'qualification', 'experience_years', 'consultation_fee', 'rating', 'is_available_online', 'is_featured']
    list_filter = ['specialty', 'is_available_online', 'is_featured']
    list_editable = ['is_available_online', 'is_featured', 'consultation_fee']
    search_fields = ['full_name', 'qualification', 'bio']


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_name', 'doctor', 'preferred_date', 'preferred_time_slot', 'consultation_type', 'status', 'created_at']
    list_filter = ['status', 'consultation_type', 'preferred_date']
    list_editable = ['status']
    search_fields = ['patient_name', 'patient_email', 'patient_phone', 'symptoms']
