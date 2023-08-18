from django.shortcuts import render, redirect
from shopapp.models import Product
from django.core.exceptions import ObjectDoesNotExist
from .models import Cart, CartItem
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

# Helper function to get or create the cart_id in the session
def _cart_id(request):
    cart_id = request.session.get('cart_id')
    if not cart_id:
        cart_id = request.session.session_key  # Use session_key instead of create()
        request.session['cart_id'] = cart_id  # Save the cart_id in the session
        request.session.modified = True
    return cart_id

# ... Rest of the views ...

def add_cart(request, product_id):
    print("Product ID:", product_id)
    cart_id = _cart_id(request)
    print("Cart ID:", cart_id)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        print("Product does not exist")
        return redirect('shopapp:allProdCat')

    cart, created = Cart.objects.get_or_create(cart_id=cart_id)
    print("Cart created:", created)

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity < cart_item.product.stock:
            cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)

    return redirect('cart:cart_detail')


def cart_detail(request):
    total = 0
    counter = 0
    cart_items = None
    cart_id = _cart_id(request)

    try:
        cart = Cart.objects.get(cart_id=cart_id)
        cart_items = CartItem.objects.filter(cart=cart, active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            counter += cart_item.quantity
    except Cart.DoesNotExist:
        # Handle the case when the cart does not exist
        cart_items = []

    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total, 'counter': counter})


def cart_remove(request, product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except CartItem.DoesNotExist:
        # Handle the case when the cart item does not exist
        # You can show a message or redirect the user to the cart page
        return redirect('cart:cart_detail')
    except Product.DoesNotExist:
        # Handle the case when the product does not exist
        # You can show a message or redirect the user to the cart page
        return redirect('cart:cart_detail')

    return redirect('cart:cart_detail')

def full_remove(request,product_id):
    cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    cart_item = CartItem.objects.get(product=product, cart=cart)
    cart_item.delete()
    return redirect('cart:cart_detail')
