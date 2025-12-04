from django.shortcuts import render, redirect
from django.http import Http404
from .models import Product
from mongoengine.errors import DoesNotExist, ValidationError
from .forms import OrderForm   
from .utils import send_telegram_order

def index(request):
    products = Product.objects.all()
    
    name_query = request.GET.get('name')
    store_query = request.GET.get('store')
    max_price = request.GET.get('max_price')

    if name_query:
        products = products.filter(title__icontains=name_query)
    
    if store_query:
        products = products.filter(store=store_query)
    
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    return render(request, "products/index.html", {"products": products})

def product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except (DoesNotExist, ValidationError):
        raise Http404("Товар не найден")

    return render(request, "products/product_detail.html", {"product": product})

def add_to_cart(request, product_id):
    cart = request.session.get('cart', [])
    
    str_id = str(product_id)
    
    if str_id not in cart:
        cart.append(str_id)
        
    request.session['cart'] = cart
    return redirect('cart')

def cart_view(request):
    cart_ids = request.session.get('cart', [])
    
    if cart_ids:
        cart_products = Product.objects.filter(id__in=cart_ids)
    else:
        cart_products = []

    total_price = sum(p.price for p in cart_products) if cart_products else 0

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data['phone']
            address = form.cleaned_data['address']

            send_telegram_order(cart_products, phone, address, total_price)

            request.session['cart'] = []
            
            return render(request, "products/order_success.html")
    else:
        form = OrderForm()

    return render(request, "products/cart.html", {
        "cart_products": cart_products,
        "total_price": total_price,
        "form": form
    })
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', [])
    str_id = str(product_id)
    if str_id in cart:
        cart.remove(str_id)
        request.session['cart'] = cart
    return redirect('cart')

def about(request):
    return render(request, "products/about.html")