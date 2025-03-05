from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product, Category, Profile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
import random

from payment.forms import ShippingForm
from payment.models import ShippingAddress

from django import forms
from django.db.models import Q
import json
from cart.cart import Cart

from recommender.recommender import RecommendationSystem


def search(request):
	# Determine if they filled out the form
	if request.method == "POST":
		searched = request.POST['searched']
		# Query The Products DB Model
		searched = Product.objects.filter(Q(name__icontains=searched))
		# Test for null
		if not searched:
			messages.success(request, "That Product Does Not Exist...Please try Again.")
			return render(request, "search.html", {})
		else:
			return render(request, "search.html", {'searched':searched})
	else:
		return render(request, "search.html", {})	


def update_info(request):
	if request.user.is_authenticated:
		# Get Current User
		current_user = Profile.objects.get(user__id=request.user.id)
		# Get Current User's Shipping Info
		shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
		
		# Get original User Form
		form = UserInfoForm(request.POST or None, instance=current_user)
		# Get User's Shipping Form
		shipping_form = ShippingForm(request.POST or None, instance=shipping_user)		
		if form.is_valid() or shipping_form.is_valid():
			# Save original form
			form.save()
			# Save shipping form
			shipping_form.save()

			messages.success(request, "Your Info Has Been Updated!!")
			return redirect('home')
		return render(request, "update_info.html", {'form':form, 'shipping_form':shipping_form})
	else:
		messages.success(request, "You Must Be Logged In To Access That Page!!")
		return redirect('home')



def update_password(request):
	if request.user.is_authenticated:
		current_user = request.user
		# Did they fill out the form
		if request.method  == 'POST':
			form = ChangePasswordForm(current_user, request.POST)
			# Is the form valid
			if form.is_valid():
				form.save()
				messages.success(request, "Your Password Has Been Updated...")
				login(request, current_user)
				return redirect('update_user')
			else:
				for error in list(form.errors.values()):
					messages.error(request, error)
					return redirect('update_password')
		else:
			form = ChangePasswordForm(current_user)
			return render(request, "update_password.html", {'form':form})
	else:
		messages.success(request, "You Must Be Logged In To View That Page...")
		return redirect('home')

def update_user(request):
	if request.user.is_authenticated:
		current_user = User.objects.get(id=request.user.id)
		user_form = UpdateUserForm(request.POST or None, instance=current_user)

		if user_form.is_valid():
			user_form.save()

			login(request, current_user)
			messages.success(request, "User Has Been Updated!!")
			return redirect('home')
		return render(request, "update_user.html", {'user_form':user_form})
	else:
		messages.success(request, "You Must Be Logged In To Access That Page!!")
		return redirect('home')


def category_summary(request):
	categories = Category.objects.all()
	return render(request, 'category_summary.html', {"categories":categories})	

def category(request, foo):
	try:
		# Look Up The Category
		category = Category.objects.get(name=foo)
		product_list = Product.objects.filter(category=category)
		# Pagination
		paginator = Paginator(product_list, 52)  # Show 10 products per page
		page = request.GET.get('page')
		try:
			products = paginator.page(page)
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			products = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			products = paginator.page(paginator.num_pages)

		return render(request, 'category.html', {'products':products, 'category':category})
	except:
		messages.success(request, ("That Category Doesn't Exist..."))
		return redirect('home')


# def product(request,pk):
# 	product = Product.objects.get(id=pk)
# 	reccomend_products = Product.objects.filter(category=product.category)[:3]
# 	return render(request, 'product.html', {'product':product, 'reccomend_products':reccomend_products})

def category_map(natural_category):
	cat_map = {
	'Nhà Cửa - Đời Sống': 'nha_cua_doi_song',
	'Thời Trang Nữ': 'thoi_trang_nu',
	'Thiết Bị Kĩ Thuật Số - Phụ Kiện Số': 'thiet_bi_kts_phu_kien_so',
	'Ô Tô - Xe Máy - Xe Đạp': 'o_to_xe_may_xe_dap',
	'Làm Đẹp - Sức Khỏe': 'lam_dep_suc_khoe',
	'Đồ Chơi - Mẹ & Bé': 'do_choi_me_be',
	'Bách Hóa Online': 'bach_hoa_online',
	'Điện Gia Dụng': 'dien_gia_dung',
	'Điện Thoại - Máy Tính Bảng': 'dien_thoai_may_tinh_bang',
	'Thể Thao - Dã Ngoại': 'the_thao_da_ngoai'
	}
	return cat_map[str(natural_category)]

def product(request,pk):
	product = Product.objects.get(id=pk)
	iid = int(product.tiki_product_id)
	category = category_map(product.category)
	rcm = RecommendationSystem(category=category)
	rcm.initialize()
	most_similar = rcm.most_similar(iid)
	# Output: A list of Product objects
	recommend_products = []
	for i in most_similar:
		rec = Product.objects.filter(tiki_product_id=i).first()
		if rec:
			recommend_products.append(rec)
	recommend_products = recommend_products[:8]
	return render(request, 'product.html', {'product':product, 'recommend_products':recommend_products})

# def product(request,pk):
# 	product = Product.objects.get(id=pk)
# 	# print(product.id)
# 	# print(type(product.id))
# 	recommend_products = Product.objects.filter(category=product.category)[:3]
# 	for rec in recommend_products:
# 		print(rec.id)
# 	return render(request, 'product.html', {'product':product, 'recommend_products':recommend_products})

	


# def home(request):
# 	products = Product.objects.all()
# 	return render(request, 'home.html', {'products':products})


def about(request):
	return render(request, 'about.html', {})	

def login_user(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)

			# Do some shopping cart stuff
			current_user = Profile.objects.get(user__id=request.user.id)
			# Get their saved cart from database
			saved_cart = current_user.old_cart
			# Convert database string to python dictionary
			if saved_cart:
				# Convert to dictionary using JSON
				converted_cart = json.loads(saved_cart)
				# Add the loaded cart dictionary to our session
				# Get the cart
				cart = Cart(request)
				# Loop thru the cart and add the items from the database
				for key,value in converted_cart.items():
					cart.db_add(product=key, quantity=value)

			messages.success(request, ("You Have Been Logged In!"))
			return redirect('home')
		else:
			messages.success(request, ("There was an error, please try again..."))
			return redirect('login')

	else:
		return render(request, 'login.html', {})


def logout_user(request):
	logout(request)
	messages.success(request, ("You have been logged out...Thanks for stopping by..."))
	return redirect('home')



def register_user(request):
	form = SignUpForm()
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			# log in user
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, ("Username Created - Please Fill Out Your User Info Below..."))
			return redirect('update_info')
		else:
			messages.success(request, ("Whoops! There was a problem Registering, please try again..."))
			return redirect('register')
	else:
		return render(request, 'register.html', {'form':form})
	

def home(request):
    product_list = list(Product.objects.all())
    random.seed(27)
    random.shuffle(product_list)
    # Pagination
    paginator = Paginator(product_list, 40)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)

    return render(request, 'home.html', {'products': products})