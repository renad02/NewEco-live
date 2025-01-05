from django.db import models
from django.contrib.auth.models import User 

# Create your models here.

class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)   #OneToOne relationship, it means , one user only have one customer and one customer only have one user 
	name = models.CharField(max_length=200, null=True)
	email = models.CharField(max_length=200)

	def __str__(self):
		return self.name
	

class Product(models.Model):
	name = models.CharField(max_length=200)
	price = models.DecimalField(max_digits=7, decimal_places=2)
	digital = models.BooleanField(default=False,null=True, blank=True)   # digital is BooleanField because if iteam is digital so it is  true and we don't need to shipped it and if not so it is false so we don't need to shipped it 
	image = models.ImageField(null=True, blank=True)

	def __str__(self):
		return self.name
	
	@property
	def imageURL(self):                  #this for if image dose not found it will be error , so this prevent the error and it show empty image
		try:
			url = self.image.url 
		except:
			url = ''
		return url 


class Detials(models.Model):
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	description=models.CharField(max_length=5000)
	color=models.CharField(max_length=50)
	availability=models.BooleanField() 

	def __str__(self):
		return str(self.product)


class Order(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)  # ForeignKey for Customer table , if customer deleted we don't need to delete the order so we set the customer null -->> on_delete=models.SET_NULL
	date_ordered = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)                 # A Boolean field indicating whether the order is complete.
	transaction_id = models.CharField(max_length=100, null=True)   # it is look like order id 

	def __str__(self):
		return str(self.id)  # str -->> string 
	
	@property
	def shipping(self):       # make the shipping false because the product is digital then check if the order contain object product then make the shipping True
		shipping = False
		orderitems = self.orderitem_set.all()
		for i in orderitems:
			if i.product.digital == False:
				shipping = True
		return shipping
	
	@property
	def get_cart_total(self):    # return the number of order total 
		orderitems = self.orderitem_set.all()
		total = sum([item.get_total for item in orderitems])
		return total
	
	@property
	def get_cart_items(self):    # return the number of order items 
		orderitems = self.orderitem_set.all()
		total = sum([item.quantity for item in orderitems])
		return total

	

class OrderItem(models.Model):
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)

	@property
	def get_total(self):       # return the number of item total 
		total = self.product.price * self.quantity
		return total



class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address