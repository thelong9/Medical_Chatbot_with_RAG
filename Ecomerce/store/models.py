from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save


# Create Customer Profile
class Profile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	date_modified = models.DateTimeField(User, auto_now=True)
	phone = models.CharField(max_length=20, blank=True)
	address1 = models.CharField(max_length=200, blank=True)
	address2 = models.CharField(max_length=200, blank=True)
	city = models.CharField(max_length=200, blank=True)	
	old_cart = models.CharField(max_length=200, blank=True, null=True)

	def __str__(self):
		return self.user.username

# Create a user Profile by default when user signs up
def create_profile(sender, instance, created, **kwargs):
	if created:
		user_profile = Profile(user=instance)
		user_profile.save()

# Automate the profile thing
post_save.connect(create_profile, sender=User)







# Categories of Products
class Category(models.Model):
	name = models.CharField(max_length=50)

	def __str__(self):
		return self.name

	#@daverobb2011
	class Meta:
		verbose_name_plural = 'categories'


# Customers
class Customer(models.Model):
	first_name = models.CharField(max_length=50)
	last_name = models.CharField(max_length=50)
	phone = models.CharField(max_length=10)
	email = models.EmailField(max_length=100)
	password = models.CharField(max_length=100)


	def __str__(self):
		return f'{self.first_name} {self.last_name}'



# All of our Products
class Product(models.Model):
	tiki_product_id = models.IntegerField(unique=True, default=0)
	name = models.CharField(max_length=100)
	price = models.IntegerField(default=0)
	category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
	description = models.CharField(max_length=250, default='', blank=True, null=True)
	image = models.CharField(max_length=100)
	brand_id = models.IntegerField(default=0)
	brand_name = models.CharField(max_length=100, default='')
	# Add Sale Stuff
	

	def __str__(self):
		# return self.name + ' - \n' + str(self.price) + ' - \n' + self.category.name+ ' - \n' + self.description + ' - \n' + self.image + ' - \n' + str(self.tiki_product_id)
		return self.name

# Customer Orders
class Order(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
	quantity = models.IntegerField(default=1)
	address = models.CharField(max_length=100, default='', blank=True)
	phone = models.CharField(max_length=20, default='', blank=True)
	date = models.DateField(default=datetime.datetime.today)
	status = models.BooleanField(default=False)

	def __str__(self):
		return self.product
	
class Rating(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE, to_field='tiki_product_id', related_name='ratings')
	title = models.CharField(max_length=100, default='')
	customer_id = models.IntegerField(default=0)
	rating = models.IntegerField(default=0)
	customer_name = models.CharField(max_length=100, default='')

	def __str__(self):
		return str(self.rating)
	
#Thêm rating và nối lại cho id sản phẩm match với id sp trong rating