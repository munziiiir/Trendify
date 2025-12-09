import types
from django.contrib import admin
from .custom_admin import trendify_admin_site
from .models import Customer, Category, Product, Order, OrderItem

# Lock down the default admin site so only superusers can access /superadmin.
def _superuser_only_permission(self, request):
    return request.user.is_active and request.user.is_superuser

admin.site.has_permission = types.MethodType(_superuser_only_permission, admin.site)

# Register your models here for the superuser admin.
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
