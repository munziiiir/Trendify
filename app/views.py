from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import resolve, Resolver404
from django.http import JsonResponse
from .forms import createUserForm, loginForm
from .models import Product, Customer, Category
from .cart import Cart
import json

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def products(request):
    query = request.GET.get('query', '') # search
    selected_categories = request.GET.getlist('categories') # filter
    products = Product.objects.all()
    # narrow products list to display based on search and filters selected
    if query: products = products.filter(name__icontains=query)
    if selected_categories: products = products.filter(categories__name__in=selected_categories).distinct()
    categories = Category.objects.all()
    return render(request, 'products.html', {'products': products, 'categories': categories, 'selected_categories': selected_categories})

@login_required
def cart(request):
    products = Cart(request).getProd()
    quantities = Cart(request).getQty()
    total = Cart(request).total()
    return render(request, 'cart.html', {'products': products, 'quantities': quantities, 'total': total})

@login_required
def cart_add(request):
    if request.method == "POST":
        if request.POST.get('action') == 'post':
            pid = int(request.POST.get('pid'))
            qty = int(request.POST.get('qty'))
            product = get_object_or_404(Product, id=pid)
            # save to session
            Cart(request).add(product=product, quantity=qty)
            quantity = Cart(request).__len__()
            response = JsonResponse({'pid': pid, 'qty': qty, 'cartQty': quantity})
            return response
    else:
        messages.error(request, 'You must be logged in to add items to your cart')
        return redirect('login')

@login_required
def cart_delete(request):
    if request.POST.get('action') == 'post':
        pid = int(request.POST.get('pid'))
        Cart(request).delete(product=pid)
        response = JsonResponse("action successful", safe=False)
        messages.success(request, ("Item Deleted!"))
        return response

@login_required
def cart_update(request):
    if request.POST.get('action') == 'post':
        pid = int(request.POST.get('pid'))
        qty = int(request.POST.get('qty'))
        Cart(request).update(product=pid, quantity=qty)
        response = JsonResponse({'qty':qty})
        messages.success(request, ("Cart Updated!"))
        return response

def login_user(request):
    if request.method == "POST":
        form = loginForm(request.POST)
        next_url = request.POST.get('next', 'index')
        try: resolve(next_url)
        except Resolver404: next_url = 'index'
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                # get which object from customer model links to user
                customer = Customer.objects.filter(user__id = request.user.id).first()
                cart = json.loads(customer.cart) if customer and customer.cart else None
                if cart:
                    Cart(request).login(cart)
                messages.success(request, ("Log in Succesfull!"))
                return redirect(next_url)
            else:
                # form.add_error(None, 'Invalid username or password.')
                messages.error(request, 'Invalid username or password.')
                return render(request, 'login.html', {'next': next_url, 'form': form})
                # return redirect('login')
        else:
            # print(form.errors)
            return render(request, 'login.html', {'next': next_url, 'form': form})
    else:
        form = loginForm()
        next_url = request.GET.get('next', 'index')
        return render(request, 'login.html', {'next': next_url, 'form': form})

def logout_user(request):
    next_url = request.GET.get('next', 'index')
    try:
        view = resolve(next_url)
        if view.func.__name__ in ['cart', 'cart_add', 'cart_delete', 'cart_update', 'payment']:
            next_url = 'index'
    except Resolver404:
        next_url = 'index'
    logout(request)
    messages.success(request, ("Logged out Succesfully!"))
    return redirect(next_url)

def register(request):
    if request.method  == "POST":
        form = createUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            login(request, user)
            messages.success(request, ("Registered and Logged In Succesfully!"))
            return redirect('products')
        else:
            error_messages = [error for errors in form.errors.values() for error in errors]
            for message in error_messages:
                if message != "This field is required.":
                    messages.error(request, message)
                else:
                    messages.error(request, "Please fill in all fields.")
    else:
        form = createUserForm()
    return render(request, 'register.html', {'form' : form})

def product(request, pk):
    product = Product.objects.get(id=pk)
    return render(request, 'product.html', {'product': product, 'request': request})

@login_required
def payment(request):
    Cart(request).paymentDelete()
    return render(request, 'payment.html')