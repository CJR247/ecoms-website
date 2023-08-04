from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import *
import json
import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import SignUpForm
from store.models import Customer


def login_user(request):
    if request.method == 'POST':
        
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # customer = Customer.objects.get_or_create(user=user)[0]
            # customer.login_count += 1
            customer.save()
            messages.success(request, 'You are logged in')
            return redirect('store')
        else:
            messages.error(request, 'There was an error logging in')
            return redirect('login')

    else:
        
        cartItems =0
        return render(request, 'store/login.html',{'cartItems':cartItems})
    

# def get_login_count(user):
#     return LoginEvent.objects.filter(user=user).count()


def logout_user(request):
    logout(request)
    messages.success(request, 'you are logged out!')
    return redirect('store')


def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username,password=password)
            login(request,user)
            messages.success(request,'you have been logged in succesfully')
            return redirect('store')
        else:
            cartItems = 0  # You may want to update this value based on your actual cart logic
            return render(request, 'store/register.html', {'form': form, 'cartItems': cartItems})
    else:
        cartItems=0
        return render(request,'store/register.html',{'form':form,'cartItems':cartItems})


def store(request):
    cartItems = 0

    if request.user.is_authenticated:
        try:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(
                customer=customer, complete=False)
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items

        except Customer.DoesNotExist:
            customer = None

        
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)


def cart(request):
    cartItems = 0
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(
                customer=customer, complete=False)
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items

        except Customer.DoesNotExist:
            customer = None


        

    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)


def checkout(request):
    cartItems = 0
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(
                customer=customer, complete=False)
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items
            if cartItems == 0:
                messages.error(request,"please add items to the cart")
                return redirect('store')
            
        except Customer.DoesNotExist:
            customer = None

          # Redirect to the store if cart is empty

    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/checkout.html', context)


def main(request):
    context = {}
    return render(request, 'main/store.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(
        order=order, product=product)
    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)
    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)
        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if total == order.get_cart_total:
            order.complete = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )
    else:
        print('User is not logged in')

    return JsonResponse('Payment submitted..', safe=False)

def order_history(request):
    cartItems = 0
    user = request.user
    orders = Order.objects.filter(customer__user=user,complete=True).exclude(orderitem__isnull=True).order_by('-date_ordered')
    return render(request, 'store/history.html', {'orders': orders,'cartItems': cartItems})