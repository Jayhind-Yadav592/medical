from django.contrib import admin
from .models import ArticleCategory, Article


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'author_name', 'medical_reviewer', 'read_time_minutes', 'views_count', 'is_featured', 'is_published', 'published_at']
    list_filter = ['category', 'is_featured', 'is_published', 'published_at']
    list_editable = ['is_featured', 'is_published']
    search_fields = ['title', 'excerpt', 'content', 'author_name', 'tags']
    prepopulated_fields = {'slug': ('title',)}
