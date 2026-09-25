from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.core.models import User, Address, NewsletterSubscriber, ContactInquiry
from apps.pharmacy.models import Category, Brand, Product, Review, WishlistItem
from apps.orders.models import Prescription, Cart, CartItem, Order, OrderItem, OrderStatusHistory
from apps.telehealth.models import Doctor, ConsultationRequest
from apps.articles.models import Article, ArticleCategory
from .serializers import (
    UserSerializer, RegisterSerializer,
    CategorySerializer, ProductSerializer, ProductDetailSerializer, ReviewSerializer,
    CartSerializer, CartItemSerializer, PrescriptionSerializer,
    OrderSerializer, DoctorSerializer, ConsultationRequestSerializer,
    ArticleSerializer
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
                'message': f'Welcome to AuraHealth, {user.first_name or user.username}!',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthLoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({
                'message': f'Welcome back, {user.first_name or user.username}!',
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid username or password.'}, status=status.HTTP_401_UNAUTHORIZED)


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
