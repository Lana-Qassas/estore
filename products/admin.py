from django.contrib import admin
from .models import Category, Product, Wishlist, DiscountCode, Cart, CartItem, Rating

admin.site.register(Product)
admin.site.register(Wishlist)
admin.site.register(DiscountCode)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Rating)
admin.site.register(Category)

