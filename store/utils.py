import json
from .models import *

#The purpose of this function is to handle all the logic we created for our guest users order.
def cookieCart(request):

	#Create empty cart for now for non-logged in user
	# Cart does not exist error. We can fix this by using a try/except statement
	try:
		cart = json.loads(request.COOKIES['cart'])     #retrieve what's in our browsers cookies by using request.COOKIES['cart'] and json.loads() to parse the data because currently it is a string value.
	except:
		cart = {}        #create an empty cart to work with if one does not exist.
		print('CART:', cart)

    #Create empty cart for now for non-logged in user
	items = []
	order = {'get_cart_total':0, 'get_cart_items':0, 'shipping':False}     # to handel the error of unlogged user
	cartItems = order['get_cart_items']

	for i in cart:   # This loop will query the quantity of each item in our cart and add to the value of "cartItems" therefore giving us the total of all items + quantity in the entire cart.
		#We use try block to prevent items in cart that may have been removed from causing error
		try:
			cartItems += cart[i]['quantity']

            #Order Totals
			product = Product.objects.get(id=i)    #get product that its id equal to i
			total = (product.price * cart[i]['quantity'])   #the value of total by multiplying the product price by the quantity.

			order['get_cart_total'] += total      # add the total (+=) to order['get_cart_total']
			order['get_cart_items'] += cart[i]['quantity']    #Do the same for order['get_cart_items'] with the quantity

			item = {       #In each iteration of the loop for items in our cart, we will create an item object and append to our items list.
				'id':product.id,
				'product':{'id':product.id,'name':product.name, 'price':product.price, 
				'imageURL':product.imageURL}, 'quantity':cart[i]['quantity'],
				'digital':product.digital,'get_total':total,
				}
			items.append(item)

            #Shipping Information
			if product.digital == False:
				order['shipping'] = True
		except:
			pass
			
	return {'cartItems':cartItems ,'order':order, 'items':items}  # return to views function when we call 


def cartData(request):
	if request.user.is_authenticated:        #check if user authenticated 
		customer = request.user.customer      # user authenticated
		order, created = Order.objects.get_or_create(customer=customer, complete=False)      #Checks if there’s an incomplete order for this customer in the database. If it exists, order is assigned to it; if not, it creates a new Order. 
		items = order.orderitem_set.all()                #Fetches all items (related OrderItem objects) associated with the order.
		cartItems = order.get_cart_items
	else:
		cookieData = cookieCart(request)    # call cookieCart function that in utils.py 
		cartItems = cookieData['cartItems']   # get cartItems
		order = cookieData['order']          # get order
		items = cookieData['items']          # get items

	return {'cartItems':cartItems ,'order':order, 'items':items}


def guestOrder(request, data):
	#Get cookie cart
	print('COOKIES:', request.COOKIES)
	name = data['form']['name']
	email = data['form']['email']

	cookieData = cookieCart(request)  # cookieCart is a function from utils.py
	items = cookieData['items']

    #Create customer & Order
	customer, created = Customer.objects.get_or_create(
			email=email,
			)
	customer.name = name
	customer.save()

	order = Order.objects.create(
		customer=customer,
		complete=False,
		)

    #Create Items
	for item in items:
		product = Product.objects.get(id=item['id'])
		orderItem = OrderItem.objects.create(
			product=product,
			order=order,
			quantity=item['quantity'],
		)
	return customer, order


def Orders(request):
	if request.user.is_authenticated:         
		customer = request.user.customer 
		orders = Order.objects.filter(customer=customer, complete=True)
	return orders