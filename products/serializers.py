from decimal import Decimal
from rest_framework import serializers
from .models import Cart, Category, Product, Rating, Wishlist, CartItem, DiscountCode

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'key', 'name']

class ProductSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.email')
    average_rating = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True)
    class Meta:
        model = Product
        fields = '__all__'
    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if not ratings.exists():
            return None
        return round(sum(r.stars for r in ratings) / ratings.count(), 1)

class WishlistSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Wishlist
        fields = ["id", "user", "product"]

class CartItemSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'user', 'product', 'quantity', 'total_price']

    def get_total_price(self, obj):
        return obj.product.price * obj.quantity

class DiscountCodeSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = DiscountCode
        fields = ['code', 'percentage']

class CartSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    items = CartItemSerializer(many=True)
    total_before_discount = serializers.SerializerMethodField()
    total_after_discount = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id','user', 'items', 'total_before_discount', 'discount', 'total_after_discount']

    def get_total_before_discount(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())

    def get_discount(self, obj):
        if obj.discount_code and obj.discount_code.active:
            return obj.discount_code.percentage
        return 0

    def get_total_after_discount(self, obj):
        total = self.get_total_before_discount(obj)
        discount = self.get_discount(obj)
        return total * (Decimal('1') - Decimal(str(discount)) / Decimal('100'))
class RatingSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    class Meta:
        model = Rating
        fields = ['id','user', 'product', 'stars']

    def validate_stars(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Stars must be between 1 and 5.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data['product']
        stars = validated_data['stars']

        rating, created = Rating.objects.update_or_create(
            user=user,
            product=product,
            defaults={'stars': stars}
        )
        return rating