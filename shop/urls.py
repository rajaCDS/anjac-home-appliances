# shop/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home & Products
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),

    # Cart & Checkout
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('razorpay/success/', views.razorpay_success, name='razorpay_success'),
    path('razorpay/success', views.razorpay_success),

    # User Registration
    path('register/', views.register, name='register'),

    # OTP / Login
    path('accounts/login/', views.login_view, name='login'),
    path('verify-otp/', views.otp_verify, name='verify_otp'),

    # Logout
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # Orders & Cart Actions
    path('orders/', views.orders, name='orders'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('wishlist-action/', views.wishlist_action, name='wishlist_action'),

    # Optional alternative OTP login URL
    path('otp-login/', views.login_view, name='otp_login'),
]
