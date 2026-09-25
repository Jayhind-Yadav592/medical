from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    icon_class = models.CharField(max_length=100, default='fa-solid fa-pills', help_text='FontAwesome icon class')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_featured = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    country = models.CharField(max_length=100, default='United States')
    description = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name


class Product(models.Model):
    DOSAGE_FORM_CHOICES = (
        ('TABLET', 'Tablet'),
        ('CAPSULE', 'Capsule'),
        ('SYRUP', 'Oral Liquid / Syrup'),
        ('INJECTION', 'Injection'),
        ('CREAM', 'Topical Cream / Ointment'),
        ('DROPS', 'Eye / Ear Drops'),
        ('INHALER', 'Inhaler / Respiratory'),
        ('DEVICE', 'Medical Device & Diagnostic'),
        ('SUPPLEMENT', 'Wellness Supplement / Powder'),
        ('OTHER', 'Healthcare Product'),
    )
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=265, unique=True, blank=True)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    short_description = models.CharField(max_length=300)
    full_description = models.TextField()
    active_ingredient = models.CharField(max_length=200, blank=True, null=True, help_text="e.g. Paracetamol / Acetaminophen")
    dosage_form = models.CharField(max_length=30, choices=DOSAGE_FORM_CHOICES, default='TABLET')
    dosage_strength = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. 500mg, 1000 IU, 10ml")
    pack_size = models.CharField(max_length=100, default="10 Tablets / Strip", help_text="e.g. 30 Capsules Bottle")
    
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Current Selling Price in USD")
    mrp_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Original / MRP Price")
    discount_percent = models.PositiveIntegerField(default=0, help_text="Calculated or manual discount %")
    stock = models.PositiveIntegerField(default=100)
    
    prescription_required = models.BooleanField(default=False, help_text="Is Rx Prescription mandatory?")
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00, validators=[MinValueValidator(1.0), MaxValueValidator(5.0)])
    total_reviews = models.PositiveIntegerField(default=0)
    
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Direct CDN/high-res image URL fallback")
    
    usage_instructions = models.TextField(blank=True, null=True, default="Take as prescribed by certified physician or as indicated on packaging.")
    side_effects = models.TextField(blank=True, null=True, default="Consult your doctor if you experience any mild nausea or allergic reaction.")
    storage_condition = models.CharField(max_length=200, default="Store in a cool, dry place below 25°C. Keep away from direct sunlight.")
    manufacturer = models.CharField(max_length=200, default="AuraBio Pharmaceuticals Ltd.")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-rating', '-created_at']
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.dosage_strength or ''}-{self.sku}")
        if self.mrp_price and self.mrp_price > self.price:
            self.discount_percent = int(((self.mrp_price - self.price) / self.mrp_price) * 100)
        super().save(*args, **kwargs)
        
    @property
    def get_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return '/static/images/placeholder_medicine.png'
        
    @property
    def in_stock(self):
        return self.stock > 0
        
    def __str__(self):
        return f"{self.name} ({self.dosage_strength or self.get_dosage_form_display()})"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True, null=True)
    is_cover = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Gallery for {self.product.name}"


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=150)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update product average rating
        reviews = self.product.reviews.all()
        if reviews.exists():
            avg = sum([r.rating for r in reviews]) / reviews.count()
            self.product.rating = round(avg, 2)
            self.product.total_reviews = reviews.count()
            self.product.save()

    def __str__(self):
        return f"{self.user.username} on {self.product.name} ({self.rating}★)"


class WishlistItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.user.username} -> {self.product.name}"
