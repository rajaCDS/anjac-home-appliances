# ------------------------------
# shop/urls.py
# ------------------------------
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),  # ✅ Add this
    path('register/', views.register, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True,
        next_page='home'
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('orders/', views.orders, name='orders'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('wishlist-action/', views.wishlist_action, name='wishlist_action'),
]
