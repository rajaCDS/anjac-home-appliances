# ------------------------------
# shop/views.py
# ------------------------------

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, get_user_model
from django.core.mail import send_mail
from django.core.cache import cache
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from collections import defaultdict
from django.core.paginator import Paginator
from decimal import Decimal
from .models import Product, Category, Order, CartItem, Cart, SavedAddress, Wishlist, OrderItem
from django.http import HttpResponse
from datetime import datetime
from .forms import RegisterForm
import random
import time

OTP_TTL_SECONDS = 5 * 60
RATE_LIMIT_KEY = "otp_rate_{user_id}"


def home(request):
    products = Product.objects.all()

    # Filtering
    price = request.GET.get("price")
    rating = request.GET.get("rating")
    if price:
        low, high = map(int, price.split("-"))
        products = products.filter(price__gte=low, price__lte=high)
    if rating:
        products = products.filter(static_rating__gte=int(rating))

    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query) 

    # Add dummy static rating and review count
    for p in products:
        p.static_rating = random.randint(3, 5)
        p.review_count = random.randint(20, 120)
        multiplier = Decimal(str(random.uniform(1.1, 1.3)))  # ✅ convert float to Decimal
        p.original_price = (p.price * multiplier).quantize(Decimal('0'))  # Round to nearest ₹
        p.discount_percent = 100 - int((p.price / p.original_price) * 100)

    # Pagination
    paginator = Paginator(products, 4)
    page = request.GET.get("page")
    products = paginator.get_page(page)

    return render(request, 'home.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

def add_to_cart(request, pk):
    product = get_object_or_404(Product, id=pk)

    if request.user.is_authenticated:
        # Get or create the user's cart
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # Check if product already in cart
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
        cart_item.save()
    else:
        # Guest cart (session)
        cart = request.session.get('cart', {})
        cart[str(pk)] = cart.get(str(pk), 0) + 1
        request.session['cart'] = cart

    return redirect('cart')


# @login_required
def cart(request):
    if request.user.is_authenticated:
        # Logged-in user → use DB cart
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart, saved_for_later=False)
        saved_items = Wishlist.objects.filter(user=request.user).select_related('product')

        total = sum(item.product.price * item.quantity for item in cart_items)
        discount = total * Decimal('0.1')
        final_total = total - discount
    else:
        # Guest user → use session cart
        cart_session = request.session.get("cart", {})
        cart_items = []
        total = 0

        for product_id, qty in cart_session.items():
            product = Product.objects.filter(id=product_id).first()
            if product:
                total += product.price * qty
                cart_items.append({
                    "product": product,
                    "quantity": qty,
                })

        saved_items = []  # no wishlist for guests
        discount = total * Decimal('0.1')
        final_total = total - discount

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "wishlist_items": saved_items,
        "total_price": total,
        "discount": discount,
        "final_total": final_total,
    })

def get_cart_summary(user):
    cart = Cart.objects.get(user=user)
    items = []
    for item in CartItem.objects.filter(cart=cart):
        items.append(f"{item.product.name} x {item.quantity}")
    return ", ".join(items)


def get_cart_total(user):
    cart = Cart.objects.get(user=user)
    total = 0
    for item in CartItem.objects.filter(cart=cart):
        total += item.product.price * item.quantity
    return total

@login_required
def checkout(request):
    saved_addresses = SavedAddress.objects.filter(user=request.user)
    cart = Cart.objects.get(user=request.user)

    if request.method == 'POST':
        name = request.POST['name']
        street = request.POST['street']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        delivery_date = request.POST['delivery_date']
        delivery_time = request.POST['delivery_time']
        payment_method = request.POST['payment_method']

        cart_summary_string = get_cart_summary(request.user)
        calculated_cart_total = get_cart_total(request.user)

        # Save address if requested
        if request.POST.get("save_address") == "on":
            SavedAddress.objects.create(
                user=request.user,
                name=name,
                street=street,
                city=city,
                state=state,
                pincode=pincode
            )

        # Create order
        order = Order.objects.create(
            user=request.user,
            customer_name=name,
            customer_email=request.user.email,
            street=street,
            city=city,
            state=state,
            pincode=pincode,
            delivery_date=delivery_date,
            delivery_time=delivery_time,
            payment_method=payment_method,
            ordered_items=cart_summary_string,
            total_amount=calculated_cart_total
        )

        # Create order items
        cart_items = CartItem.objects.filter(cart=cart)
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
                color=getattr(item, 'color', ''),
                size=getattr(item, 'size', '')
            )

        # Clear the cart
        cart_items.delete()

        messages.success(request, 'Order placed successfully! 🎉')
        return redirect('orders')

    return render(request, 'checkout.html', {
        'saved_addresses': saved_addresses
    })

def send_login_otp(email, otp):
    subject = "Your MyStore Login OTP"
    message = f"Your OTP is {otp}. Valid for 5 minutes."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

def login_view(request):
    print(f"Login view method: {request.method}")  # Debugging line
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            # OTP rate limit
            rate_key = RATE_LIMIT_KEY.format(user_id=user.pk)
            last_sent = cache.get(rate_key)
            if last_sent and time.time() - last_sent < 60:
                messages.error(request, "OTP already sent. Try again later.")
                return redirect("login")

            otp = str(random.randint(100000, 999999))
            cache.set(f"login_otp_{user.pk}", otp, OTP_TTL_SECONDS)
            cache.set(rate_key, time.time(), 60)  # 1 min block

            send_login_otp(user.email, otp)
            request.session["pre_auth_user_id"] = user.pk

            # Next page after login (checkout or home)
            next_url = request.POST.get("next") or request.GET.get("next", "/")
            return render(request, "otp_verify.html", {"email": user.email, "next": next_url})
        else:
            messages.error(request, "Invalid credentials")

    context = {"next": request.GET.get("next", "")}
    return render(request, "login.html", context)


def otp_verify(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        next_url = request.POST.get("next") or "/"
        user_id = request.session.get("pre_auth_user_id")

        if not user_id:
            messages.error(request, "Session expired. Please login again.")
            return redirect("login")

        cache_key = f"login_otp_{user_id}"
        expected_otp = cache.get(cache_key)

        if otp == expected_otp:
            User = get_user_model()
            user = User.objects.get(pk=user_id)
            login(request, user)

            # Clear OTP and session
            cache.delete(cache_key)
            request.session.pop("pre_auth_user_id", None)

            # Redirect to next page
            return redirect(next_url)
        else:
            messages.error(request, "Invalid or expired OTP")
            return redirect("login")

    # GET request fallback
    next_url = request.GET.get("next", "/")
    return render(request, "otp_verify.html", {"next": next_url}) 

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-order_date')
    orders_with_items = []

    for order in user_orders:
        order_items = OrderItem.objects.filter(order=order)

        items = []
        for item in order_items:
            product = item.product
            items.append({
                'product_name': product.name if product else 'N/A',
                'image_url': product.image.url if product and product.image else '',
                'color': item.color or 'N/A',
                'size': item.size,
                'price': item.price,
                'quantity': item.quantity,
            })

        orders_with_items.append({
            'order_id': order.id,
            'order_date': order.order_date,
            'delivery_date': order.delivery_date,
            'payment_method': order.payment_method,
            'order_status': order.order_status,
            'total_amount': order.total_amount,
            'delivery_message': 'Your item has been shipped.' if order.order_status.lower() in ['shipped', 'on the way'] else 'Your item has been delivered.',
            'items': items
        })

    print(f"Orders with items: {orders_with_items}")  # Debugging line

    return render(request, 'orders.html', {
        'orders': orders_with_items
    })


@login_required
def update_cart(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        product_id = request.POST.get('product_id')

        if product_id and product_id.isdigit():
            product = get_object_or_404(Product, id=product_id)
            cart = get_object_or_404(Cart, user=request.user)

            try:
                item = CartItem.objects.get(cart=cart, product=product)
            except CartItem.DoesNotExist:
                item = None

            if action == 'increase' and item:
                item.quantity += 1
                item.save()
            elif action == 'decrease' and item and item.quantity > 1:
                item.quantity -= 1
                item.save()
            elif action == 'remove' and item:
                item.delete()
            elif action == 'save_for_later' and item:
                Wishlist.objects.get_or_create(user=request.user, product=product)
                item.delete()

    return redirect('cart')


@login_required
def wishlist_action(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')

        if product_id and product_id.isdigit():
            product = get_object_or_404(Product, id=product_id)

            if action == 'remove':
                Wishlist.objects.filter(user=request.user, product=product).delete()
            elif action == 'move_to_cart':
                cart, _ = Cart.objects.get_or_create(user=request.user)
                CartItem.objects.get_or_create(cart=cart, product=product)
                Wishlist.objects.filter(user=request.user, product=product).delete()

    return redirect('cart')