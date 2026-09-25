from django.db import models
from django.utils.text import slugify
from django.utils import timezone


class ArticleCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Article Categories"
        ordering = ['name']
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=270, unique=True, blank=True)
    category = models.ForeignKey(ArticleCategory, on_delete=models.CASCADE, related_name='articles')
    
    excerpt = models.TextField(max_length=400, help_text="Brief summary for cards and meta description")
    content = models.TextField(help_text="Full markdown or HTML content")
    
    cover_image = models.ImageField(upload_to='articles/', blank=True, null=True)
    cover_image_url = models.URLField(max_length=500, blank=True, null=True)
    
    author_name = models.CharField(max_length=150, default='Dr. Marcus Vance')
    author_title = models.CharField(max_length=150, default='Lead Clinical Pharmacologist')
    author_avatar = models.URLField(max_length=500, blank=True, null=True)
    medical_reviewer = models.CharField(max_length=150, default='Dr. Sophia Chen, MD (Board Certified)')
    
    read_time_minutes = models.PositiveIntegerField(default=5)
    tags = models.CharField(max_length=255, default='Immunity, Vitamins, Prevention, Clinical')
    views_count = models.PositiveIntegerField(default=120)
    
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_featured', '-published_at']
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
    @property
    def get_cover_image(self):
        if self.cover_image:
            return self.cover_image.url
        if self.cover_image_url:
            return self.cover_image_url
        return '/static/images/placeholder_article.jpg'
        
    def __str__(self):
        return self.title
