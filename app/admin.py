from django.contrib import admin
from .custom_admin import trendify_admin_site
from .models import Customer, Category, Product, Order, OrderItem

# Register your models here.
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)

# need to reregister models to the custom instance of admin portal for them to show up in the view
trendify_admin_site.register(Customer)
trendify_admin_site.register(Category)
trendify_admin_site.register(Product)
trendify_admin_site.register(Order)
trendify_admin_site.register(OrderItem)