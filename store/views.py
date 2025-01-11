from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout   
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import RegisterUserForm
import json                             # it is defrent from JsonResponse
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder, Orders, authenticate

def store(request):

	data = cartData(request)    # call cartData function and set the variable to "data", now we can just call "data" and get all the values we need.

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()    # the model Product
	context = {'products':products, 'cartItems':cartItems}    # this is ('cartItems':cartItems) to sent main.html to correct the number of basket
	return render(request, 'store/store.html', context)


def cart(request):

	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)



def checkout(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)



def updateItem(request):
	data = json.loads(request.body)        # to get or load data that sented   
	productId = data['productId']          # get productId
	action = data['action']                # get action
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer       # get customer from database
	product = Product.objects.get(id=productId)    # get product id from database that equal to productId that user sented
	order, created = Order.objects.get_or_create(customer=customer, complete=False)    #get order or created

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)   #get order item or created

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)


from django.views.decorators.csrf import csrf_exempt


def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()     #transaction ID
	data = json.loads(request.body) # get data

	#Set Data
	if request.user.is_authenticated:   # if user authenticated 
		customer = request.user.customer   # get customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)   # get or create order

    #Guest Checkout Logic
	else:
		customer, order = guestOrder(request, data) # we sent data as parameter because we use it to get name and email
		
	total = float(data['form']['total'])     # get total by using (data), get form and then get total.
	order.transaction_id = transaction_id    # set transaction_id that in order table in models to be equal to (transaction_id datetime). it all about send transaction_id to backend

    #Confirm Total
	if total == order.get_cart_total:
		order.complete = True
	order.save()

	#Shipping Logic. Send shipping address data to backend
	if order.shipping == True:
		ShippingAddress.objects.create(
	        customer=customer,
	        order=order,
	        address=data['shipping']['address'],  # we do like this because address is in javascript form 
	        city=data['shipping']['city'],
	        state=data['shipping']['state'],
	        zipcode=data['shipping']['zipcode'],
	    )

	return JsonResponse('Payment submitted..', safe=False)


def login_user(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}

	if request.method =="POST":
		email = request.POST["email"]
		password = request.POST["password"]
		user = authenticate(email=email, password=password)
		if user is not None:
			login(request, user)
			return redirect('store')
		else:
			messages.success(request, ("There Was An Error Logging In, Try Again..."))
			return redirect('login')
	else:
		return render(request, 'store/login.html', context)

def logout_user(request):
	logout(request)
	messages.success(request, ("You Were Logged out!"))
	return redirect('store')

def register_user(request):

	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
	
	if request.method =="POST":
		form = RegisterUserForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			email = form.cleaned_data['email']
			first_name = form.cleaned_data['first_name']
			last_name = form.cleaned_data['last_name']
			user = authenticate(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
			user_info = Customer(user = user, name = first_name, email = email)
			user_info.save()
			login(request, user)
			messages.success(request, ("Registration Successful! "))
			return redirect('store')
	else:	
		form = RegisterUserForm()
		
	context = {'items':items, 'order':order, 'cartItems':cartItems, 'form':form}
	return render(request, 'store/register.html', context)


def user_account(request):
	try:
		data = cartData(request)
		cartItems = data['cartItems']
		order = data['order']
		items = data['items']

		orders = Orders(request)

		context = {'items':items, 'order':order, 'cartItems':cartItems, 'orders':orders}

	except:
		context = {'items':items, 'order':order, 'cartItems':cartItems}

	return render(request, 'store/useraccount.html', context)


def detials(request,id):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	item = Detials.objects.select_related('product').filter(id=id).first()

	context = {'items':items, 'order':order, 'cartItems':cartItems, 'item':item}
	return render(request, 'store/detials.html', context)

def preorder(request,tranid):

	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	orderid = Order.objects.get(transaction_id=tranid)

	preord = orderid.orderitem_set.all()                
	
	#preord = OrderItem.objects.select_related('order').filter(order_id=orderid).first()

	context = {'items':items, 'order':order, 'cartItems':cartItems, 'preord':preord, 'orderid':orderid}
	return render(request, 'store/preorder.html', context)
