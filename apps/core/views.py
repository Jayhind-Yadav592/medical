from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from apps.pharmacy.models import Category, Product, Review, Brand
from apps.telehealth.models import Doctor, ConsultationRequest
from apps.articles.models import Article, ArticleCategory
from apps.orders.models import Order, Prescription, Cart


def home_view(request):
    """Render the master homepage with dynamic database feeds."""
    categories = Category.objects.filter(is_featured=True)[:6]
    featured_products = Product.objects.filter(is_featured=True).select_related('category')[:8]
    trending_products = Product.objects.filter(is_trending=True).select_related('category')[:4]
    best_sellers = Product.objects.filter(is_best_seller=True).select_related('category')[:4]
    doctors = Doctor.objects.filter(is_featured=True)[:3]
    articles = Article.objects.filter(is_published=True).select_related('category')[:3]
    featured_doctor = Doctor.objects.filter(is_available_online=True).first()

    context = {
        'categories': categories,
        'featured_products': featured_products,
        'trending_products': trending_products,
        'best_sellers': best_sellers,
        'doctors': doctors,
        'articles': articles,
        'featured_doctor': featured_doctor,
    }
    return render(request, 'pages/index.html', context)


def shop_view(request):
    """Full shop catalog with filtering, sorting, and pagination."""
    products = Product.objects.all().select_related('category', 'brand')
    categories = Category.objects.all()

    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(active_ingredient__icontains=search_query) |
            Q(short_description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )

    rx = request.GET.get('rx')
    if rx == '1':
        products = products.filter(prescription_required=True)
    elif rx == '0':
        products = products.filter(prescription_required=False)

    dosage_form = request.GET.get('dosage_form')
    if dosage_form:
        products = products.filter(dosage_form=dosage_form.upper())

    sort = request.GET.get('sort', 'featured')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'rating':
        products = products.order_by('-rating')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    else:
        products = products.order_by('-is_featured', '-rating')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query,
        'current_rx': rx,
        'current_dosage': dosage_form,
        'current_sort': sort,
        'total_count': products.count(),
    }
    return render(request, 'pages/shop.html', context)


def product_detail_view(request, slug):
    """Detailed clinical product page."""
    product = get_object_or_404(Product.objects.select_related('category', 'brand'), slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    reviews = product.reviews.select_related('user').all()

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
    }
    return render(request, 'pages/product_detail.html', context)


def services_view(request):
    """Healthcare and clinical pharmacy services."""
    return render(request, 'pages/services.html')


def telehealth_view(request):
    """Telehealth specialist directory and appointment booking."""
    specialty = request.GET.get('specialty')
    doctors = Doctor.objects.all()
    if specialty:
        doctors = doctors.filter(specialty=specialty.upper())
    return render(request, 'pages/telehealth.html', {'doctors': doctors, 'selected_specialty': specialty})


def prescriptions_portal_view(request):
    """Prescription upload and status verification portal."""
    user_prescriptions = []
    if request.user.is_authenticated:
        user_prescriptions = Prescription.objects.filter(user=request.user)
    return render(request, 'pages/prescriptions.html', {'user_prescriptions': user_prescriptions})


def articles_view(request):
    """Health and clinical wellness knowledge base."""
    category_slug = request.GET.get('category')
    articles = Article.objects.filter(is_published=True).select_related('category')
    if category_slug:
        articles = articles.filter(category__slug=category_slug)
    categories = ArticleCategory.objects.all()
    return render(request, 'pages/articles.html', {'articles': articles, 'categories': categories, 'selected_category': category_slug})


def article_detail_view(request, slug):
    """Single health journal article."""
    article = get_object_or_404(Article.objects.select_related('category'), slug=slug)
    article.views_count += 1
    article.save(update_fields=['views_count'])
    recent_articles = Article.objects.filter(is_published=True).exclude(id=article.id)[:3]
    return render(request, 'pages/article_detail.html', {'article': article, 'recent_articles': recent_articles})


def cart_page_view(request):
    """Full shopping cart review page."""
    return render(request, 'pages/cart.html')


def checkout_page_view(request):
    """Complete checkout & prescription attachment page."""
    return render(request, 'pages/checkout.html')


def order_tracking_view(request):
    """Real-time prescription and order tracker."""
    order_num = request.GET.get('order_number')
    order = None
    if order_num:
        order = Order.objects.filter(order_number__iexact=order_num.strip()).first()
    return render(request, 'pages/order_tracking.html', {'order': order, 'searched_number': order_num})


@login_required(login_url='/')
def user_dashboard_view(request):
    """Patient medical dashboard."""
    orders = Order.objects.filter(user=request.user)
    prescriptions = Prescription.objects.filter(user=request.user)
    consultations = ConsultationRequest.objects.filter(user=request.user)
    return render(request, 'pages/dashboard.html', {
        'orders': orders,
        'prescriptions': prescriptions,
        'consultations': consultations,
    })


def about_view(request):
    return render(request, 'pages/about.html')


def contact_view(request):
    return render(request, 'pages/contact.html')
