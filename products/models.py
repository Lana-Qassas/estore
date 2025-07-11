from django.db import models
from django.conf import settings

CATEGORY_CHOICES = [
    ('sport', 'Sport'),
    ('furniture', 'Furniture'),
    ('electronic', 'Electronic'),
    ('clothes', 'Clothes'),
    ('shoes', 'Shoes'),
    ('jewelry', 'Jewelry'),
    ('cosmetics', 'Cosmetics'),
]

class Category(models.Model):
    key = models.SlugField(max_length=50, unique=True)  
    name = models.CharField(max_length=100)             

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')  
    price = models.DecimalField(max_digits=10, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    image1 = models.ImageField(upload_to='products/')
    image2 = models.ImageField(upload_to='products/', blank=True)
    image3 = models.ImageField(upload_to='products/', blank=True)
    image4 = models.ImageField(upload_to='products/', blank=True)

class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

class DiscountCode(models.Model):
    code = models.CharField(max_length=50, unique=True)
    percentage = models.PositiveIntegerField(help_text="Enter value like 10 for 10% off")
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} ({self.percentage}% off)"
    
class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    discount_code = models.ForeignKey(DiscountCode, null=True, blank=True, on_delete=models.SET_NULL)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stars = models.PositiveIntegerField()

    class Meta:
        unique_together = ['product', 'user'] 

    def __str__(self):
        return f'{self.user} rated {self.product} {self.stars} stars'
