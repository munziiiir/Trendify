from .models import Product, Customer
from django.contrib import messages
import json
# adds data to a user session to store cart data as a python dictionary
# if no dictionary, creates it for the current user session

class Cart():
    def __init__(self, request) -> None:
        self.request = request
        self.session = request.session
        self.cart = self.session.setdefault('session_key', {})

    # saves cart to database
    def dbsave(self):
        customer = Customer.objects.get(user__id=self.request.user.id)
        customer.cart = json.dumps(self.cart)
        customer.save()

    # retrieves previously saved cart from db and loads it into session
    def login(self, cart):
        for key, value in cart.items():
            if str(key) not in self.cart:
                self.cart[str(key)] = value
        self.session.modified = True

    def add(self, product, quantity):
        product_id = str(product.id)
        if product_id in self.cart:
            messages.success(self.request, ("Product already in cart!"))
        else:
            self.cart[product_id] = quantity
            messages.success(self.request, ("Product added to cart!"))
        self.dbsave()
        self.session.modified = True
    
    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)
        self.cart[product_id] = product_qty
        self.dbsave()
        self.session.modified = True
    
    def delete(self, product):
        if str(product) in self.cart:
            del self.cart[str(product)]
        self.dbsave()
        self.session.modified = True
    
    def paymentDelete(self):
        # can add functionality to save the ordered items to db
        # [code]
        # clears cart after checkout
        self.cart.clear()
        self.dbsave()
        self.session.modified = True

    def total(self):
        total = 0
        products = Product.objects.filter(id__in = self.cart.keys())
        # for key, value in self.cart.items():
        #     for product in products:
        #         if product.id == int(key):
        #             total += (product.price * value)
        total = sum(product.price * value for key, value in self.cart.items() for product in products if product.id == int(key))
        return total
        # return sum(item['quantity'] for item in self.cart.values())
    
    def getProd(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in = product_ids)
        return products
    
    def getQty(self):
        return self.cart
    
    def __len__(self):
        return len(self.cart)