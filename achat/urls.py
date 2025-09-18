from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .viewsets.register import RegisterView
from .viewsets.login import LoginView
from .viewsets.logout import LogoutView
from .viewsets.categories import CategoryViewSet, SubCategoryViewSet
from .viewsets.product import ProductViewSet
from .viewsets.wishlist import WishlistViewSet
from .viewsets.notification import NotificationViewSet
from .viewsets.cart import CartViewSet
from .viewsets.orders import OrderViewSet
from .viewsets.reviews import ReviewViewSet
from .viewsets.vendor_dashboard import VendorDashboardViewSet
from .viewsets.customer_dashboard import CustomerDashboardViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'subcategories', SubCategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'wishlists', WishlistViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'vendor-dashboard', VendorDashboardViewSet, basename='vendor-dashboard')
router.register(r'customer-dashboard', CustomerDashboardViewSet, basename='customer-dashboard')

urlpatterns = [
    # Authentication endpoints
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    
    # API Router endpoints (Categories, SubCategories, Products)
    path("", include(router.urls)),
]
