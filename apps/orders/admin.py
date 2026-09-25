from django.contrib import admin
from .models import Prescription, Cart, CartItem, Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'unit_price', 'quantity', 'subtotal']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 1


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_name', 'patient_phone', 'doctor_name', 'status', 'verified_by', 'uploaded_at']
    list_filter = ['status', 'uploaded_at']
    search_fields = ['patient_name', 'patient_phone', 'doctor_name', 'clinic_hospital']
    list_editable = ['status']
    readonly_fields = ['uploaded_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'total_items', 'subtotal', 'created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'full_name', 'phone', 'final_amount',
        'payment_method', 'payment_status', 'order_status', 'created_at'
    ]
    list_filter = ['order_status', 'payment_status', 'payment_method', 'created_at']
    list_editable = ['order_status', 'payment_status']
    search_fields = ['order_number', 'full_name', 'email', 'phone', 'tracking_number']
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    readonly_fields = ['order_number', 'created_at', 'updated_at']
