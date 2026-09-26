from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required

User = get_user_model()

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


@login_required(login_url='/login/')
def user_dashboard_view(request):
    """Advanced Patient Medical Dashboard (EHR, Vitals, Pill Reminders & Order Timeline)."""
    orders = Order.objects.filter(user=request.user).prefetch_related('items', 'status_history')
    prescriptions = Prescription.objects.filter(user=request.user)
    consultations = ConsultationRequest.objects.filter(user=request.user)
    
    from apps.core.models import PatientVital, PillReminder, PatientIntake, MedicalFacility
    vitals = PatientVital.objects.filter(user=request.user)
    latest_vital = vitals.first()
    pill_reminders = PillReminder.objects.filter(user=request.user)
    intakes = PatientIntake.objects.filter(user=request.user)
    nearest_facilities = MedicalFacility.objects.filter(is_active=True)[:4]

    return render(request, 'pages/dashboard.html', {
        'orders': orders,
        'prescriptions': prescriptions,
        'consultations': consultations,
        'vitals': vitals,
        'latest_vital': latest_vital,
        'pill_reminders': pill_reminders,
        'intakes': intakes,
        'nearest_facilities': nearest_facilities,
    })


def facilities_locator_view(request):
    """Interactive Nearest Hospital & Pharmacy GPS locator with Leaflet map."""
    from apps.core.models import MedicalFacility
    facilities = MedicalFacility.objects.filter(is_active=True)
    facility_type = request.GET.get('type')
    if facility_type and facility_type != 'ALL':
        facilities = facilities.filter(facility_type=facility_type)
    return render(request, 'pages/facilities.html', {
        'facilities': facilities,
        'selected_type': facility_type or 'ALL'
    })


def patient_intake_view(request):
    """Smart multi-step symptom checker & prescription upload page."""
    from apps.core.models import MedicalFacility
    facilities = MedicalFacility.objects.filter(is_active=True, facility_type='PHARMACY')
    return render(request, 'pages/intake.html', {
        'facilities': facilities
    })


def order_invoice_view(request, order_number):
    """Printable official pharmacy tax invoice & prescription dispense certificate."""
    order = get_object_or_404(Order.objects.prefetch_related('items'), order_number__iexact=order_number)
    return render(request, 'pages/invoice.html', {
        'order': order
    })


@login_required(login_url='/login/')
def digital_health_card_view(request):
    """Printable / Downloadable Digital Patient Health ID Card with QR Stamp."""
    from apps.core.models import PatientVital
    latest_vital = PatientVital.objects.filter(user=request.user).first()
    return render(request, 'pages/health_card.html', {
        'user': request.user,
        'latest_vital': latest_vital
    })


def consultation_room_view(request, room_id):
    """Simulated Telehealth consultation room with video, prescription pad, and chat."""
    doctor = Doctor.objects.first()
    return render(request, 'pages/consultation_room.html', {
        'room_id': room_id,
        'doctor': doctor
    })


def about_view(request):
    return render(request, 'pages/about.html')



def contact_view(request):
    return render(request, 'pages/contact.html')


def login_view(request):
    """Full-page and POST handler for user login."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    next_url = request.GET.get('next') or request.POST.get('next') or 'home'
    error_message = None

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username_or_email or not password:
            error_message = "Please enter both username/email and password."
        else:
            username = username_or_email
            if '@' in username_or_email:
                user_obj = User.objects.filter(email__iexact=username_or_email).first()
                if user_obj:
                    username = user_obj.username

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect(next_url)
            else:
                error_message = "Invalid username/email or password. Please check your credentials."

    return render(request, 'pages/login.html', {
        'error_message': error_message,
        'next_url': next_url
    })


def register_view(request):
    """Full-page and POST handler for new patient registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')

        if not username or not password:
            error_message = "Username and password are required."
        elif password != confirm_password:
            error_message = "Passwords do not match."
        elif len(password) < 6:
            error_message = "Password must be at least 6 characters long."
        elif User.objects.filter(username__iexact=username).exists():
            error_message = f"Username '{username}' is already taken. Please choose another."
        elif email and User.objects.filter(email__iexact=email).exists():
            error_message = f"An account with email '{email}' already exists."
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                user_type='PATIENT'
            )
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome to Antixor Pharmacy, {user.first_name or user.username}.")
            return redirect('home')

    return render(request, 'pages/register.html', {
        'error_message': error_message
    })


def logout_view(request):
    """Sign out user and redirect to home."""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    return redirect('home')

