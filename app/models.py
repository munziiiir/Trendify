from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Customer(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    cart = models.CharField(max_length=2000, default='', null=True)

    def __str__(self) -> str:
        return f'{self.user}'

# creates a customer model object automatically when a user registers (only for non-staff, non-superuser accounts)
def create_customer(sender, instance, created, **kwargs):
    if created and not instance.is_staff and not instance.is_superuser:
        Customer.objects.create(user=instance)

post_save.connect(create_customer, sender=User)

class Category(models.Model):
    class Meta:
        verbose_name_plural = "Categories"

    name = models.CharField(max_length=40)

    def __str__(self) -> str:
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=40)
    categories = models.ManyToManyField(Category)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    description = models.CharField(default='', max_length=300)
    image = models.ImageField(upload_to='uploads/products/', null=True)

    def __str__(self) -> str:
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} by {self.customer}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
