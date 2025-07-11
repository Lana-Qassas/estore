from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, RatingViewSet, WishlistViewSet, CartViewSet

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('wishlist', WishlistViewSet,basename='wishlist')
router.register('ratings', RatingViewSet, basename='rating')
router.register('category', CategoryViewSet, basename='category')
router.register('cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
    # path('cart/', CartViewSet.as_view({'get': 'list'}), name='cart'),
    # path('cart/<int:pk>/increment/', CartViewSet.as_view({'post': 'increment'})),
    # path('cart/<int:pk>/decrement/', CartViewSet.as_view({'post': 'decrement'})),
    # path('cart/apply_discount/', CartViewSet.as_view({'post': 'apply_discount'})),
   
]
