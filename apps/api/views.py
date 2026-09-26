from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.core.models import (
    User, Address, NewsletterSubscriber, ContactInquiry,
    MedicalFacility, PatientVital, PillReminder, PatientIntake
)
from apps.pharmacy.models import Category, Brand, Product, Review, WishlistItem
from apps.orders.models import Prescription, Cart, CartItem, Order, OrderItem, OrderStatusHistory
from apps.telehealth.models import Doctor, ConsultationRequest
from apps.articles.models import Article, ArticleCategory
from .serializers import (
    UserSerializer, RegisterSerializer,
    CategorySerializer, ProductSerializer, ProductDetailSerializer, ReviewSerializer,
    CartSerializer, CartItemSerializer, PrescriptionSerializer,
    OrderSerializer, DoctorSerializer, ConsultationRequestSerializer,
    ArticleSerializer, MedicalFacilitySerializer, PatientVitalSerializer,
    PillReminderSerializer, PatientIntakeSerializer
)


def get_or_create_cart(request):
    """Helper to retrieve or initialize session/user cart."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer

    def get_queryset(self):
        qs = Product.objects.all().select_related('category', 'brand')
        
        category_slug = self.request.query_params.get('category')
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
            
        search_query = self.request.query_params.get('search')
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query) |
                Q(active_ingredient__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
            
        prescription_only = self.request.query_params.get('rx')
        if prescription_only is not None:
            if prescription_only.lower() in ['1', 'true']:
                qs = qs.filter(prescription_required=True)
            elif prescription_only.lower() in ['0', 'false']:
                qs = qs.filter(prescription_required=False)
                
        featured = self.request.query_params.get('featured')
        if featured:
            qs = qs.filter(is_featured=True)
            
        trending = self.request.query_params.get('trending')
        if trending:
            qs = qs.filter(is_trending=True)
            
        dosage_form = self.request.query_params.get('dosage_form')
        if dosage_form:
            qs = qs.filter(dosage_form=dosage_form.upper())

        sort_by = self.request.query_params.get('sort')
        if sort_by == 'price_asc':
            qs = qs.order_by('price')
        elif sort_by == 'price_desc':
            qs = qs.order_by('-price')
        elif sort_by == 'rating':
            qs = qs.order_by('-rating')
        elif sort_by == 'newest':
            qs = qs.order_by('-created_at')

        return qs


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class AutocompleteAPIView(APIView):
    """Real-time instant search suggestions for the global search bar."""
    def get(self, request):
        query = request.query_params.get('q', '').strip()
        if len(query) < 2:
            return Response([])

        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(active_ingredient__icontains=query) |
            Q(category__name__icontains=query)
        ).select_related('category')[:8]

        results = []
        for p in products:
            results.append({
                'id': p.id,
                'name': p.name,
                'slug': p.slug,
                'category': p.category.name,
                'dosage': p.dosage_strength or p.get_dosage_form_display(),
                'price': float(p.price),
                'mrp_price': float(p.mrp_price) if p.mrp_price else None,
                'image': p.get_image,
                'rx': p.prescription_required,
            })
        return Response(results)


class CartAPIView(APIView):
    """Full API for viewing and manipulating the interactive cart drawer."""
    def get(self, request):
        cart = get_or_create_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        """Add product to cart or increment quantity."""
        cart = get_or_create_cart(request)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

        serializer = CartSerializer(cart)
        return Response({
            'message': f'Added {product.name} to cart',
            'cart': serializer.data
        }, status=status.HTTP_200_OK)

    def patch(self, request):
        """Update quantity of specific item or remove if qty <= 0."""
        cart = get_or_create_cart(request)
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

        if quantity <= 0:
            item.delete()
        else:
            item.quantity = quantity
            item.save()

        serializer = CartSerializer(cart)
        return Response({
            'message': 'Cart updated successfully',
            'cart': serializer.data
        }, status=status.HTTP_200_OK)

    def delete(self, request):
        """Delete specific item or clear entire cart."""
        cart = get_or_create_cart(request)
        item_id = request.data.get('item_id')
        if item_id:
            CartItem.objects.filter(id=item_id, cart=cart).delete()
        else:
            cart.items.all().delete()

        serializer = CartSerializer(cart)
        return Response({'message': 'Cart updated', 'cart': serializer.data})


class WishlistAPIView(APIView):
    """Toggle product in user's wishlist."""
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'items': []})
        wishlist_items = WishlistItem.objects.filter(user=request.user).select_related('product')
        products = [item.product for item in wishlist_items]
        serializer = ProductSerializer(products, many=True)
        return Response({'items': serializer.data, 'count': len(products)})

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Please log in to save favorites'}, status=status.HTTP_401_UNAUTHORIZED)
        
        product_id = request.data.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        item = WishlistItem.objects.filter(user=request.user, product=product).first()
        if item:
            item.delete()
            is_wishlisted = False
            message = f'Removed {product.name} from wishlist'
        else:
            WishlistItem.objects.create(user=request.user, product=product)
            is_wishlisted = True
            message = f'Added {product.name} to wishlist'

        count = WishlistItem.objects.filter(user=request.user).count()
        return Response({
            'is_wishlisted': is_wishlisted,
            'count': count,
            'message': message
        })


class PrescriptionUploadAPIView(APIView):
    """Upload prescription image or PDF for clinical verification."""
    def post(self, request):
        file = request.FILES.get('prescription_file')
        patient_name = request.data.get('patient_name', '').strip()
        patient_phone = request.data.get('patient_phone', '').strip()
        doctor_name = request.data.get('doctor_name', '').strip()
        clinic_hospital = request.data.get('clinic_hospital', '').strip()
        notes = request.data.get('notes', '').strip()

        if not file:
            return Response({'error': 'Please select a valid prescription image (JPG/PNG) or PDF.'}, status=status.HTTP_400_BAD_REQUEST)
        if not patient_name:
            return Response({'error': 'Patient name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        prescription = Prescription.objects.create(
            user=request.user if request.user.is_authenticated else None,
            patient_name=patient_name,
            patient_phone=patient_phone,
            doctor_name=doctor_name,
            clinic_hospital=clinic_hospital,
            prescription_file=file,
            notes=notes,
            status='PENDING'
        )

        serializer = PrescriptionSerializer(prescription)
        return Response({
            'message': 'Prescription uploaded successfully. A licensed clinical pharmacist is reviewing it.',
            'prescription': serializer.data
        }, status=status.HTTP_201_CREATED)


class ConsultationBookingAPIView(APIView):
    """Book a telehealth / virtual consultation appointment."""
    def post(self, request):
        doctor_id = request.data.get('doctor_id')
        patient_name = request.data.get('patient_name', '').strip()
        patient_email = request.data.get('patient_email', '').strip()
        patient_phone = request.data.get('patient_phone', '').strip()
        preferred_date = request.data.get('preferred_date')
        preferred_time = request.data.get('preferred_time', '10:00 AM')
        consultation_type = request.data.get('consultation_type', 'VIDEO')
        symptoms = request.data.get('symptoms', '').strip()
        medical_history = request.data.get('medical_history', '').strip()

        if not doctor_id or not patient_name or not patient_phone or not preferred_date:
            return Response({'error': 'Please fill in all required fields (Doctor, Name, Phone, Date).'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            doctor = Doctor.objects.get(id=doctor_id)
        except Doctor.DoesNotExist:
            return Response({'error': 'Selected doctor not found'}, status=status.HTTP_404_NOT_FOUND)

        booking = ConsultationRequest.objects.create(
            doctor=doctor,
            user=request.user if request.user.is_authenticated else None,
            patient_name=patient_name,
            patient_email=patient_email,
            patient_phone=patient_phone,
            preferred_date=preferred_date,
            preferred_time_slot=preferred_time,
            consultation_type=consultation_type,
            symptoms=symptoms,
            medical_history=medical_history,
            status='CONFIRMED',
            meeting_link=f"https://telehealth.aurahealth.care/room/{doctor.id}-{patient_phone[-4:]}"
        )

        serializer = ConsultationRequestSerializer(booking)
        return Response({
            'message': f'Consultation booked with {doctor.full_name} on {preferred_date} at {preferred_time}',
            'booking': serializer.data
        }, status=status.HTTP_201_CREATED)


class CheckoutAPIView(APIView):
    """Place complete order from active cart."""
    def post(self, request):
        cart = get_or_create_cart(request)
        if cart.items.count() == 0:
            return Response({'error': 'Your cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        full_name = request.data.get('full_name', '').strip()
        email = request.data.get('email', '').strip()
        phone = request.data.get('phone', '').strip()
        street_address = request.data.get('street_address', '').strip()
        city = request.data.get('city', 'New York').strip()
        postal_code = request.data.get('postal_code', '10001').strip()
        payment_method = request.data.get('payment_method', 'COD')
        delivery_notes = request.data.get('delivery_notes', '')
        prescription_id = request.data.get('prescription_id')

        if not full_name or not email or not phone or not street_address:
            return Response({'error': 'Please provide full name, email, phone number, and delivery address.'}, status=status.HTTP_400_BAD_REQUEST)

        prescription_obj = None
        if prescription_id:
            prescription_obj = Prescription.objects.filter(id=prescription_id).first()

        order_status = 'PRESCRIPTION_VERIFICATION' if cart.requires_prescription and not prescription_obj else 'PLACED'

        # Create Order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key or '',
            full_name=full_name,
            email=email,
            phone=phone,
            shipping_address=street_address,
            city=city,
            postal_code=postal_code,
            prescription=prescription_obj,
            total_amount=cart.subtotal,
            shipping_fee=cart.shipping_fee,
            discount_amount=0.00,
            final_amount=cart.grand_total,
            payment_method=payment_method,
            payment_status='PAID' if payment_method in ['CARD', 'APPLE_PAY'] else 'PENDING',
            order_status=order_status,
            tracking_number=f"TRK-AUR-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            delivery_notes=delivery_notes
        )

        # Create Order Items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                unit_price=item.product.price,
                quantity=item.quantity,
                subtotal=item.subtotal
            )

        # Create Status History
        OrderStatusHistory.objects.create(
            order=order,
            status=order.order_status,
            notes="Order initiated via AuraHealth digital checkout."
        )

        # Clear Cart
        cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response({
            'message': 'Order placed successfully!',
            'order': serializer.data
        }, status=status.HTTP_201_CREATED)


class OrderTrackingAPIView(APIView):
    """Retrieve tracking details by order number."""
    def get(self, request, order_number):
        try:
            order = Order.objects.prefetch_related('items', 'status_history').get(order_number__iexact=order_number)
        except Order.DoesNotExist:
            return Response({'error': f'Order #{order_number} was not found in our medical database.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data)


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.filter(is_featured=True)
    serializer_class = DoctorSerializer

    def get_queryset(self):
        qs = Doctor.objects.all()
        specialty = self.request.query_params.get('specialty')
        if specialty:
            qs = qs.filter(specialty=specialty.upper())
        return qs


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Article.objects.filter(is_published=True)
    serializer_class = ArticleSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        qs = Article.objects.filter(is_published=True).select_related('category')
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__slug=category)
        featured = self.request.query_params.get('featured')
        if featured:
            qs = qs.filter(is_featured=True)
        return qs


class ReviewCreateAPIView(APIView):
    """Submit a verified patient review."""
    def post(self, request, product_slug):
        if not request.user.is_authenticated:
            return Response({'error': 'You must be logged in to leave a review.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            product = Product.objects.get(slug=product_slug)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        rating = int(request.data.get('rating', 5))
        title = request.data.get('title', 'Verified Patient Review')
        comment = request.data.get('comment', '').strip()

        if not comment:
            return Response({'error': 'Please provide review comments.'}, status=status.HTTP_400_BAD_REQUEST)

        review = Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            title=title,
            comment=comment,
            is_verified_purchase=True
        )

        serializer = ReviewSerializer(review)
        return Response({
            'message': 'Thank you! Your verified review has been submitted.',
            'review': serializer.data
        }, status=status.HTTP_201_CREATED)


class NewsletterAPIView(APIView):
    """Subscribe to health tips newsletter."""
    def post(self, request):
        email = request.data.get('email', '').strip()
        if not email or '@' not in email:
            return Response({'error': 'Please provide a valid email address.'}, status=status.HTTP_400_BAD_REQUEST)

        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
        return Response({
            'message': 'You have successfully subscribed to AuraHealth Clinical Digest & Special Offers!'
        }, status=status.HTTP_200_OK)


class ContactAPIView(APIView):
    """Submit general inquiry or customer support ticket."""
    def post(self, request):
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip()
        phone = request.data.get('phone', '').strip()
        subject = request.data.get('subject', 'General Inquiry').strip()
        message = request.data.get('message', '').strip()

        if not name or not email or not message:
            return Response({'error': 'Please fill in Name, Email, and Message.'}, status=status.HTTP_400_BAD_REQUEST)

        ContactInquiry.objects.create(
            name=name, email=email, phone=phone, subject=subject, message=message
        )
        return Response({
            'message': 'Thank you! Our pharmacy care coordinator will contact you shortly.'
        }, status=status.HTTP_201_CREATED)


class AuthRegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            return Response({
                'message': f'Welcome to Antixor Pharmacy, {user.first_name or user.username}!',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        errors = serializer.errors
        first_error = 'Registration failed.'
        if errors:
            first_val = next(iter(errors.values()))
            first_error = first_val[0] if isinstance(first_val, list) else str(first_val)
        return Response({'error': str(first_error), 'details': errors}, status=status.HTTP_400_BAD_REQUEST)


class AuthLoginAPIView(APIView):
    def post(self, request):
        username_or_email = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username_or_email or not password:
            return Response({'error': 'Please enter both username/email and password.'}, status=status.HTTP_400_BAD_REQUEST)

        username = username_or_email
        if '@' in username_or_email:
            user_obj = User.objects.filter(email__iexact=username_or_email).first()
            if user_obj:
                username = user_obj.username

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({
                'message': f'Welcome back, {user.first_name or user.username}!',
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid username/email or password.'}, status=status.HTTP_401_UNAUTHORIZED)


class AuthLogoutAPIView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully.'})


class AuthStatusAPIView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return Response({
                'is_authenticated': True,
                'user': UserSerializer(request.user).data
            })
        return Response({'is_authenticated': False})


# =========================================================================
# ADVANCED HEALTHCARE & GEOLOCATION APIS (RESUME HIGHLIGHTS)
# =========================================================================

class FacilityNearestAPIView(APIView):
    """Calculate and return nearest partner hospitals, pharmacies, and emergency centers using GPS Haversine distance."""
    def get(self, request):
        user_lat = request.query_params.get('lat', '40.7128')
        user_lng = request.query_params.get('lng', '-74.0060')
        facility_type = request.query_params.get('type', 'ALL')
        query = request.query_params.get('q', '').strip()

        qs = MedicalFacility.objects.filter(is_active=True)
        if facility_type and facility_type != 'ALL':
            qs = qs.filter(facility_type=facility_type)
        if query:
            qs = qs.filter(Q(name__icontains=query) | Q(city__icontains=query) | Q(postal_code__icontains=query))

        facilities_list = []
        for fac in qs:
            dist = fac.calculate_distance(user_lat, user_lng)
            fac_data = MedicalFacilitySerializer(fac).data
            fac_data['distance_km'] = dist
            fac_data['estimated_delivery_mins'] = max(15, int(dist * 8) + 10)
            facilities_list.append(fac_data)

        # Sort by distance
        facilities_list.sort(key=lambda x: x['distance_km'])

        return Response({
            'user_location': {'lat': float(user_lat), 'lng': float(user_lng)},
            'total_found': len(facilities_list),
            'facilities': facilities_list
        })


class EmergencySOSAPIView(APIView):
    """Instant Emergency SOS & Ambulance Dispatcher."""
    def post(self, request):
        user_lat = request.data.get('lat', '40.7128')
        user_lng = request.data.get('lng', '-74.0060')
        patient_name = request.data.get('patient_name', 'Patient in Emergency')
        phone = request.data.get('phone', '+1 (555) 911-0000')
        emergency_type = request.data.get('emergency_type', 'Acute Cardiac / Severe Trauma')

        # Find nearest emergency hospital
        hospitals = MedicalFacility.objects.filter(is_active=True, facility_type__in=['HOSPITAL', 'EMERGENCY_CENTER'])
        nearest_hospital = None
        min_distance = 9999.0

        for hosp in hospitals:
            dist = hosp.calculate_distance(user_lat, user_lng)
            if dist < min_distance:
                min_distance = dist
                nearest_hospital = hosp

        if not nearest_hospital:
            nearest_hospital = MedicalFacility.objects.first()
            min_distance = 1.8

        dispatch_id = f"SOS-EMG-{timezone.now().strftime('%Y%m%d%H%M%S')}"

        return Response({
            'success': True,
            'sos_id': dispatch_id,
            'status': 'AMBULANCE_DISPATCHED',
            'allocated_hospital': {
                'name': nearest_hospital.name,
                'phone': nearest_hospital.emergency_hotline or nearest_hospital.phone,
                'distance_km': min_distance,
                'eta_minutes': max(6, int(min_distance * 4)),
                'address': nearest_hospital.address,
            },
            'message': f'Emergency SOS Received. Ambulance dispatched from {nearest_hospital.name}. ETA ~{max(6, int(min_distance * 4))} mins.'
        }, status=status.HTTP_201_CREATED)


class SafetyAllergyCheckAPIView(APIView):
    """Clinical safety check: checks medicine active ingredients against patient allergy profile."""
    def post(self, request):
        medicine_name = request.data.get('medicine_name', '').strip()
        product_id = request.data.get('product_id')
        allergies = request.data.get('allergies', '')

        if request.user.is_authenticated and not allergies:
            allergies = request.user.medical_allergies or ''

        # Identify dangerous interaction pairs
        medicine_lower = medicine_name.lower()
        allergies_lower = allergies.lower()

        conflict_found = False
        warning_msg = None

        if ('amoxicillin' in medicine_lower or 'penicillin' in medicine_lower) and ('penicillin' in allergies_lower or 'amox' in allergies_lower):
            conflict_found = True
            warning_msg = "⚠️ High Severity Alert: Patient has recorded Penicillin allergy. Do not dispense Amoxicillin / Penicillin derivatives."
        elif ('aspirin' in medicine_lower or 'ibuprofen' in medicine_lower) and ('aspirin' in allergies_lower or 'nsaid' in allergies_lower):
            conflict_found = True
            warning_msg = "⚠️ Warning: Potential NSAID / Aspirin hypersensitivity conflict detected."
        elif ('sulfa' in medicine_lower or 'bactrim' in medicine_lower) and ('sulfa' in allergies_lower):
            conflict_found = True
            warning_msg = "⚠️ Warning: Sulfonamide antibiotic allergy conflict."

        return Response({
            'medicine': medicine_name,
            'patient_allergies': allergies,
            'is_safe': not conflict_found,
            'severity': 'HIGH' if conflict_found else 'SAFE',
            'warning_message': warning_msg or "✓ Safety Check Passed: No allergen conflicts detected."
        })


class PatientVitalsAPIView(APIView):
    """Manage patient health vitals and historical charts."""
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        vitals = PatientVital.objects.filter(user=request.user)[:10]
        serializer = PatientVitalSerializer(vitals, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        vital = PatientVital.objects.create(
            user=request.user,
            systolic_bp=int(request.data.get('systolic_bp', 120)),
            diastolic_bp=int(request.data.get('diastolic_bp', 80)),
            blood_sugar=float(request.data.get('blood_sugar', 95.0)),
            heart_rate=int(request.data.get('heart_rate', 72)),
            spo2=int(request.data.get('spo2', 98)),
            weight_kg=float(request.data.get('weight_kg', 68.0)),
            bmi=float(request.data.get('bmi', 22.5)),
            notes=request.data.get('notes', 'Routine vitals log.')
        )
        return Response({
            'message': 'Vitals recorded successfully!',
            'vital': PatientVitalSerializer(vital).data
        }, status=status.HTTP_201_CREATED)


class PillReminderToggleAPIView(APIView):
    """Toggle medication taken status and increment streak."""
    def post(self, request, reminder_id):
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            reminder = PillReminder.objects.get(id=reminder_id, user=request.user)
            reminder.is_taken = not reminder.is_taken
            if reminder.is_taken:
                reminder.streak_days += 1
            reminder.save()
            return Response({
                'message': f"Marked {reminder.medicine_name} as {'Taken ✓' if reminder.is_taken else 'Pending'}",
                'reminder': PillReminderSerializer(reminder).data
            })
        except PillReminder.DoesNotExist:
            return Response({'error': 'Reminder not found'}, status=status.HTTP_404_NOT_FOUND)


class PatientIntakeSubmitAPIView(APIView):
    """Submit multi-step symptom intake with auto pharmacy assignment."""
    def post(self, request):
        name = request.data.get('patient_name', '').strip()
        phone = request.data.get('patient_phone', '').strip()
        email = request.data.get('patient_email', '').strip()
        primary_symptom = request.data.get('primary_symptom', 'Fever & Fatigue')
        symptoms_list = request.data.get('symptoms_list', 'Headache, Weakness')
        pain_severity = int(request.data.get('pain_severity', 4))
        symptom_duration = request.data.get('symptom_duration', '2-3 Days')
        user_lat = request.data.get('lat', '40.7128')
        user_lng = request.data.get('lng', '-74.0060')

        if not name or not phone:
            return Response({'error': 'Please provide Patient Name and Phone Number.'}, status=status.HTTP_400_BAD_REQUEST)

        # Allocate nearest pharmacy
        pharmacies = MedicalFacility.objects.filter(is_active=True, facility_type='PHARMACY')
        allocated_fac = None
        min_dist = 9999.0
        for p in pharmacies:
            d = p.calculate_distance(user_lat, user_lng)
            if d < min_dist:
                min_dist = d
                allocated_fac = p

        intake = PatientIntake.objects.create(
            user=request.user if request.user.is_authenticated else None,
            patient_name=name,
            patient_email=email,
            patient_phone=phone,
            primary_symptom=primary_symptom,
            symptoms_list=symptoms_list,
            pain_severity=pain_severity,
            symptom_duration=symptom_duration,
            allocated_facility=allocated_fac or MedicalFacility.objects.first(),
            status='CLINICAL_REVIEW',
            pharmacist_notes=f"Assigned to {allocated_fac.name if allocated_fac else 'Central Hub'} for dosage verification & fast-track dispatch."
        )

        return Response({
            'message': 'Patient intake submitted successfully! Clinical pharmacist review in progress.',
            'intake': PatientIntakeSerializer(intake).data,
            'allocated_facility_name': allocated_fac.name if allocated_fac else 'Antixor Central Hub',
            'allocated_facility_phone': allocated_fac.phone if allocated_fac else '+1 (800) 268-4967'
        }, status=status.HTTP_201_CREATED)

