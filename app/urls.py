from django.urls import path
from.import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('about/', views.about, name = 'about'),
    path('products/', views.products, name = 'products'),
    path('cart/', views.cart, name = 'cart'),
    path('cart/add', views.cart_add, name = 'cart_add'),
    path('cart/delete', views.cart_delete, name = 'cart_delete'),
    path('cart/update', views.cart_update, name = 'cart_update'),
    path('register/', views.register, name = 'register'),
    path('login/', views.login_user, name = 'login'),
    path('logout/', views.logout_user, name = 'logout'),    
    path('product/<int:pk>', views.product, name = 'product'),
    path('payment/success', views.payment, name = 'payment'),
]