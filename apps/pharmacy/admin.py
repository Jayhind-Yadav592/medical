from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, Review, WishlistItem


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 2


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_featured', 'order', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_featured', 'order']
    search_fields = ['name']


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'country']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'dosage_form', 'dosage_strength', 'price',
        'mrp_price', 'discount_percent', 'stock', 'prescription_required',
        'is_featured', 'is_trending', 'rating'
    ]
    list_filter = ['category', 'dosage_form', 'prescription_required', 'is_featured', 'is_trending', 'is_best_seller']
    list_editable = ['price', 'stock', 'prescription_required', 'is_featured', 'is_trending']
    search_fields = ['name', 'active_ingredient', 'sku', 'short_description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ReviewInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['title', 'comment', 'product__name', 'user__username']


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
