from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import (
    home_view, shop_view, product_detail_view, services_view,
    telehealth_view, prescriptions_portal_view, articles_view,
    article_detail_view, cart_page_view, checkout_page_view,
    order_tracking_view, user_dashboard_view, about_view, contact_view,
    login_view, register_view, logout_view
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # REST API Root
    path('api/', include('apps.api.urls')),
    
    # Authentication
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    
    # Frontend Pages
    path('', home_view, name='home'),
    path('shop/', shop_view, name='shop'),
    path('product/<slug:slug>/', product_detail_view, name='product-detail'),
    path('services/', services_view, name='services'),
    path('telehealth/', telehealth_view, name='telehealth'),
    path('prescriptions/', prescriptions_portal_view, name='prescriptions'),
    path('articles/', articles_view, name='articles'),
    path('articles/<slug:slug>/', article_detail_view, name='article-detail'),
    path('cart/', cart_page_view, name='cart'),
    path('checkout/', checkout_page_view, name='checkout'),
    path('track/', order_tracking_view, name='order-track'),
    path('dashboard/', user_dashboard_view, name='dashboard'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
