from rest_framework import viewsets, filters
from .models import CATEGORY_CHOICES, Category, Product, Rating, Wishlist, CartItem, Cart, DiscountCode
from .serializers import CategorySerializer, ProductSerializer, RatingSerializer, WishlistSerializer, CartItemSerializer, CartSerializer, DiscountCodeSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg
from rest_framework.permissions import IsAuthenticated

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'category']
    
    def get_queryset(self):
        return Product.objects.annotate(
            avg_rating=Avg('ratings__stars')
        ).order_by('-avg_rating')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'key' 

    def retrieve(self, request, key=None):
        try:
            category = Category.objects.get(key=key)
        except Category.DoesNotExist:
            return Response({"detail": "Category not found."}, status=status.HTTP_404_NOT_FOUND)

        products = Product.objects.filter(category=category)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class WishlistViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = WishlistSerializer

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    def get_cart(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart
    
    def list(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        product_id = request.data.get('product')
        quantity = int(request.data.get('quantity', 1))
        if not product_id:
            return Response({'detail': 'Product ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        cart = self.get_cart(request)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def remove_item(self, request, pk=None):
        cart = self.get_cart(request)
        try:
            item = CartItem.objects.get(id=pk, cart=cart)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({'detail': 'Cart item not found.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self.get_cart(request)
        cart.items.all().delete()
        cart.discount_code = None
        cart.save()
        return Response({'detail': 'Cart cleared.'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def apply_discount(self, request):
        code = request.data.get('code')
        if not code:
            return Response({'detail': 'Discount code is required.'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            discount = DiscountCode.objects.get(code=code, active=True)
        except DiscountCode.DoesNotExist:
            return Response({'detail': 'Invalid or inactive discount code.'}, status=status.HTTP_400_BAD_REQUEST)

        cart = self.get_cart(request)
        cart.discount_code = discount
        cart.save()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def increment(self, request, pk=None):
        item = CartItem.objects.get(id=pk, cart__user=request.user)
        item.quantity += 1
        item.save()
        return Response(CartItemSerializer(item).data)

    @action(detail=True, methods=['post'])
    def decrement(self, request, pk=None):
        item = CartItem.objects.get(id=pk, cart__user=request.user)
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
            return Response(CartItemSerializer(item).data)
        else:
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart
    @action(detail=False, methods=['post'])
    def apply_discount(self, request):
        code = request.data.get("code")
        try:
            discount = DiscountCode.objects.get(code=code, active=True)
            cart = self.get_object()
            cart.discount_code = discount
            cart.save()
            return Response(CartSerializer(cart).data)
        except DiscountCode.DoesNotExist:
            return Response({"detail": "Invalid or inactive discount code."}, status=400)

class RatingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = RatingSerializer

    def get_queryset(self):
        return Rating.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)