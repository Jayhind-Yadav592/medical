import uuid
from django.db import models
from django.conf import settings
from apps.pharmacy.models import Product


class Prescription(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Pharmacist Review'),
        ('VERIFIED', 'Verified by Clinical Pharmacist'),
        ('REJECTED', 'Requires Doctor Clarification / Rejected'),
        ('DISPENSED', 'Medication Dispensed'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions', null=True, blank=True)
    patient_name = models.CharField(max_length=150)
    patient_phone = models.CharField(max_length=25, blank=True, null=True)
    doctor_name = models.CharField(max_length=150, blank=True, null=True)
    clinic_hospital = models.CharField(max_length=200, blank=True, null=True)
    prescription_file = models.FileField(upload_to='prescriptions/%Y/%m/')
    notes = models.TextField(blank=True, null=True, help_text="Patient symptoms or specific medication instructions")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_prescriptions')
    pharmacist_notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"Rx #{self.id} for {self.patient_name} ({self.get_status_display()})"


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
        
    @property
    def subtotal(self):
        return sum(item.subtotal for item in self.items.all())
        
    @property
    def shipping_fee(self):
        # Free delivery over $35
        if self.subtotal >= 35 or self.subtotal == 0:
            return 0.0
        return 4.99
        
    @property
    def grand_total(self):
        return float(self.subtotal) + float(self.shipping_fee)
        
    @property
    def requires_prescription(self):
        return any(item.product.prescription_required for item in self.items.all())
        
    def __str__(self):
        return f"Cart {self.id} (User: {self.user or self.session_key})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def unit_price(self):
        return self.product.price
        
    @property
    def subtotal(self):
        return self.unit_price * self.quantity
        
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"


class Order(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('COD', 'Cash on Express Delivery'),
        ('CARD', 'Credit / Debit Card (Online)'),
        ('APPLE_PAY', 'Apple Pay / Google Pay'),
        ('INSURANCE', 'Health Insurance Co-Pay'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Payment Pending'),
        ('PAID', 'Payment Completed'),
        ('REFUNDED', 'Refunded'),
        ('FAILED', 'Failed'),
    )
    
    ORDER_STATUS_CHOICES = (
        ('PLACED', 'Order Placed & Received'),
        ('PRESCRIPTION_VERIFICATION', 'Rx Prescription Under Pharmacist Review'),
        ('PROCESSING', 'Pharmacist Dispensing & Quality Check'),
        ('PACKED', 'Temperature-Controlled Packaged'),
        ('OUT_FOR_DELIVERY', 'Out for Express Courier Delivery'),
        ('DELIVERED', 'Delivered to Doorstep'),
        ('CANCELLED', 'Order Cancelled'),
    )
    
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    session_key = models.CharField(max_length=100, blank=True, null=True)
    
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=25)
    shipping_address = models.TextField()
    city = models.CharField(max_length=100, default='New York')
    postal_code = models.CharField(max_length=20, default='10001')
    
    prescription = models.ForeignKey(Prescription, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='COD')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    order_status = models.CharField(max_length=30, choices=ORDER_STATUS_CHOICES, default='PLACED')
    
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    estimated_delivery = models.CharField(max_length=100, default='Same-Day Express (Within 2 Hours)')
    delivery_notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"AUR-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Order #{self.order_number} ({self.full_name})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} in {self.order.order_number}"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=30, choices=Order.ORDER_STATUS_CHOICES)
    notes = models.CharField(max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-updated_at']
        
    def __str__(self):
        return f"{self.order.order_number} -> {self.status}"
