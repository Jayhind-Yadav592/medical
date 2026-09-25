from apps.pharmacy.models import Category, WishlistItem
from apps.orders.models import Cart


def site_context(request):
    """Global context available to all templates."""
    categories = Category.objects.filter(is_featured=True)[:8]
    
    # Cart calculation
    cart_count = 0
    cart_total = 0.00
    cart_items = []
    cart_obj = None
    
    try:
        if request.user.is_authenticated:
            cart_obj = Cart.objects.filter(user=request.user).first()
        else:
            if not request.session.session_key:
                request.session.create()
            session_key = request.session.session_key
            cart_obj = Cart.objects.filter(session_key=session_key).first()
            
        if cart_obj:
            cart_items = cart_obj.items.select_related('product', 'product__category').all()
            cart_count = cart_obj.total_items
            cart_total = float(cart_obj.grand_total)
    except Exception:
        pass

    # Wishlist count
    wishlist_count = 0
    if request.user.is_authenticated:
        try:
            wishlist_count = WishlistItem.objects.filter(user=request.user).count()
        except Exception:
            pass

    return {
        'site_name': 'AuraHealth™ Precision Pharmacy',
        'site_phone': '+1 (800) 584-AURA',
        'site_emergency_phone': '+1 (800) 911-CARE',
        'site_email': 'care@aurahealth.pharmacy',
        'global_categories': categories,
        'global_cart_count': cart_count,
        'global_cart_total': cart_total,
        'global_cart_items': cart_items,
        'global_cart_obj': cart_obj,
        'global_wishlist_count': wishlist_count,
    }
