from typing import Counter
from django import forms
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from .models import Customer, Product, Cart, OrderPlaced
from . forms import CustomerRegistrationForm, CustomerProfileForm
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
# def home(request):
#  return render(request, 'app/home.html')


class ProductView(View):

    def get(self, request):
        topwears = Product.objects.filter(category='TW')
        bottomwears = Product.objects.filter(category='BW')
        mobiles = Product.objects.filter(category='M')

        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user)
            return render(request, 'app/home.html', {'topwears': topwears, 'bottomwears': bottomwears, 'mobiles': mobiles, 'tcart': cart})
        else:
            return render(request, 'app/home.html', {'topwears': topwears, 'bottomwears': bottomwears, 'mobiles': mobiles})


# def product_detail(request):
#     return render(request, 'app/productdetail.html')

class ProductDetailView(View):
    def get(self, request, pk):

        product = Product.objects.get(pk=pk)
        item_already_cart = False
        if request.user.is_authenticated:
            item_already_cart = Cart.objects.filter(
                Q(product=product.id) & Q(user=request.user)).exists()

        return render(request, 'app/productdetail.html', {'product': product, 'item_already_cart': item_already_cart})


@login_required
def add_to_cart(request):
    user = request.user

    product_id = request.GET.get('prod_id')

    product = Product.objects.get(id=product_id)

    Cart(user=user, product=product).save()

    return redirect('/cart')


@login_required
def show_cart(request):

    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)

        amount = 0.0
        shiping_amount = 70.0
        total_amount = 0.0
        cart = Cart.objects.filter(user=request.user)
        empty_cart = "You Have No Product In Your Cart"
        buy_now = "Buy Now"
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        print(cart_product)
        if cart_product:
            for p in cart_product:
                tempamount = (p.quantity * p.product.discounted_price)
                amount += tempamount
                total_amount = amount + shiping_amount
        else:
            return render(request, 'app/addtocart.html', {'carts_empty': empty_cart, 'buy_now': buy_now, 'totalamount': total_amount, 'amount': amount})

        return render(request, 'app/addtocart.html', {'carts': cart, 'totalamount': total_amount, 'amount': amount, 'tcart': cart})


@login_required
def plus_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity += 1
        c.save()
        amount = 0.0
        shiping_amount = 70.0

        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
            total_amount = amount + shiping_amount
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': total_amount
        }

        return JsonResponse(data)


@login_required
def minus_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.quantity -= 1
        c.save()
        amount = 0.0
        shiping_amount = 70.0

        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        data = {
            'quantity': c.quantity,
            'amount': amount,
            'totalamount': amount + shiping_amount
        }

        return JsonResponse(data)


@login_required
def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shiping_amount = 70.0

        cart_product = [p for p in Cart.objects.all() if p.user ==
                        request.user]
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount

        data = {

            'amount': amount,
            'totalamount': amount + shiping_amount
        }

        return JsonResponse(data)


def buy_now(request):
    return render(request, 'app/buynow.html')


@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)

    return render(request, 'app/address.html', {'add': add,  'active': 'btn-primary'})


@login_required
def orders(request):
    op = OrderPlaced.objects.filter(user=request.user)

    return render(request, 'app/orders.html', {'order_placed': op})


def mobile(request, data=None):

    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data == 'Redmi' or data == 'Samsung':
        mobiles = Product.objects.filter(category="M").filter(brand=data)
    elif data == "below":
        mobiles = Product.objects.filter(
            category="M").filter(discounted_price__lt=10000)
    elif data == "above":
        mobiles = Product.objects.filter(
            category="M").filter(discounted_price__gt=10000)

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        return render(request, 'app/mobile.html', {'mobiles': mobiles, 'tcart': cart})

    return render(request, 'app/mobile.html', {'mobiles': mobiles})


def laptob(request, data=None):

    if data == None:
        laptob = Product.objects.filter(category='L')
    elif data == 'HP' or data == 'MAC' or data == "Lenevo":
        laptob = Product.objects.filter(category="L").filter(brand=data)
    elif data == "below":
        laptob = Product.objects.filter(
            category="L").filter(discounted_price__lt=40000)
    elif data == "above":
        laptob = Product.objects.filter(
            category="L").filter(discounted_price__gt=40000)
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        return render(request, 'app/laptob.html', {'laptob': laptob, 'tcart': cart})
    return render(request, 'app/laptob.html', {'laptob': laptob})


def topwear(request, data=None):
    if data == None:
        topwear = Product.objects.filter(category='TW')
    elif data == 'Nike' or data == 'Reebook' or data == "Gucci":
        topwear = Product.objects.filter(category="TW").filter(brand=data)
    elif data == "below":
        topwear = Product.objects.filter(
            category="TW").filter(discounted_price__lt=1000)
    elif data == "above":
        topwear = Product.objects.filter(
            category="TW").filter(discounted_price__gt=1000)
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        return render(request, 'app/topwear.html', {'topwear': topwear, 'tcart': cart})
    return render(request, 'app/topwear.html', {'topwear': topwear})


def bottomwear(request, data=None):
    if data == None:
        bottomwear = Product.objects.filter(category='BW')
    elif data == 'Spiker' or data == 'Anzara' or data == "Infinity":
        bottomwear = Product.objects.filter(category="BW").filter(brand=data)
    elif data == "below":
        bottomwear = Product.objects.filter(
            category="BW").filter(discounted_price__lt=1000)
    elif data == "above":
        bottomwear = Product.objects.filter(
            category="BW").filter(discounted_price__gt=900)
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        return render(request, 'app/bottomwear.html', {'bottomwear': bottomwear, 'tcart': cart})
    return render(request, 'app/bottomwear.html', {'bottomwear': bottomwear})


def login(request):

    return render(request, 'app/login.html')


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()

        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Congratulations!! Registered Successfully')

        return render(request, 'app/customerregistration.html', {'form': form})


@login_required
def checkout(request):
    user = request.user
    add = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shiping_amount = 70.0
    total_amount = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user ==
                    request.user]

    if cart_product:
        for p in cart_product:
            tempamount = (p.quantity * p.product.discounted_price)
            amount += tempamount
        total_amount += amount + shiping_amount

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        return render(request, 'app/checkout.html', {'add': add, 'total_amount': total_amount, 'cart_items': cart_items, 'tcart': cart})

    return render(request, 'app/checkout.html', {'add': add, 'total_amount': total_amount, 'cart_items': cart_items})


@login_required
def payment_done(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user=user)
    for c in cart:
        OrderPlaced(user=user, customer=customer,
                    product=c.product, quantity=c.quantity).save()
        c.delete()

    return redirect('orders')


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user)
            return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary', 'tcart': cart})
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            reg = Customer(user=usr, name=name, locality=locality,
                           city=city, state=state, zipcode=zipcode)
            reg.save()
            messages.success(
                request, 'Congratulations Profile Updated Successfully')
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user)
            return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary', 'tcart': cart})
        return render(request, 'app/profile.html', {'form': form, 'active': 'btn-primary'})


class PasswordChangeView(View):
    def get(self, request):
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user)
            return render(request, 'app/passwordchange.html', {'tcart': cart})
        return (request, 'app/passwordchange.html')


def searchhresult(request):
    search = request.GET.get('search')
    n = search.capitalize()
    allpro = Product.objects.filter(title=n)
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        return render(request, 'app/search.html', {'product': allpro, 'tcart': cart})
    return render(request, 'app/search.html', {'product': allpro})
