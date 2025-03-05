from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Product
from store.models import Category

# Create your tests here.
TEST_USERNAME = "test_user"
FIRST_NAME = "John"
LAST_NAME = "Doe"
TEST_PASSWORD =  'secret_password'
TEST_EMAIL = 'email@gmail.com'
class LoginTestCase(TestCase):
    """Tests customer login functionality"""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        User.objects.create_user(TEST_USERNAME, "", TEST_PASSWORD)

    def test_user_login(self):
        response = self.client.post(self.login_url, {"username": TEST_USERNAME, "password": TEST_PASSWORD})
        self.assertRedirects(response, reverse('home'))
        
class RegisterTestCase(TestCase):
    """Tests customer registration functionality
    fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    """
    
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
    
    def test_user_registration(self):
        form_data = {
            'username': TEST_USERNAME,
            'first_name': FIRST_NAME,
            'last_name': LAST_NAME,
            'email': TEST_EMAIL,
            'password1': TEST_PASSWORD,
            'password2': TEST_PASSWORD
        }
        response = self.client.post(self.register_url, form_data)
        self.assertRedirects(response, reverse('update_info'))
        
class LogoutTestCase(TestCase):
    """Tests customer logout functionality"""
    def setUp(self):
        self.client = Client()
        User.objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        self.logout_url = reverse('logout')
    
    def test_user_logout(self):
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, reverse('home'))

class UpdatePasswordTestCase(TestCase):
    """Tests customer update password functionality"""
    def setUp(self):
        self.client = Client()
        self.update_password_url = reverse('update_password')
        User.objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        
    def test_user_update_password(self):
        form_data = {
            'old_password': TEST_PASSWORD,
            'new_password1': 'new_password',
            'new_password2': 'new_password'
        }
        response = self.client.post(self.update_password_url, form_data)
        self.assertRedirects(response, reverse('update_user'))
    
class UpdateUserTestCase(TestCase):
    """Tests customer update user functionality"""
    def setUp(self):
        self.client = Client()
        self.update_user_url = reverse('update_user')
        User.objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        
    def test_user_update_user(self):
        form_data = {
            'username': TEST_USERNAME,
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'new_email@gmail.com'}
        response = self.client.post(self.update_user_url, form_data)
        self.assertRedirects(response, reverse('home'))
        
class UpdateInfoTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.update_info_url = reverse('update_info')
        User.objects.create_user(TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD)
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        
    def test_user_update_info(self):
        ''' 
        user info form: 
            fields = ('phone', 'address1', 'address2', 'city', 'state', 'zipcode', 'country', )
        shippingform:
            fields = ['shipping_full_name', 'shipping_email', 'shipping_address1', 'shipping_address2', 'shipping_city', 'shipping_state', 'shipping_zipcode', 'shipping_country']

        '''
        
        user_info_data = {
            'phone': '1234567890',
            'address1': '123 Main St',
            'address2': 'Apt 1',
            'city': 'Anytown',
            'state': 'CA',
            'zipcode': '12345',
            'country': 'USA'
        }
        shipping_data = {
            'shipping_full_name': 'John Doe',
            'shipping_email': 'new_email@gmail.com',
            'shipping_address1': '123 Main St',
            'shipping_address2': 'Apt 1',
            'shipping_city': 'Anytown',
            'shipping_state': 'CA',
            'shipping_zipcode': '12345',
            'shipping_country': 'USA'}
        response = self.client.post(self.update_info_url, { **user_info_data, **shipping_data})
        self.assertRedirects(response, reverse('home'))
    
class ProductTestCase(TestCase):
    ''' 
    def product(request,pk):
    	product = Product.objects.get(id=pk)
	return render(request, 'product.html', {'product':product})'''
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Books')
        self.product= Product.objects.create(name='Test Product', category= self.category, price=10.00, description='Test Description', image= 'uploads/product/1.png')
        self.product_url = reverse('product', args=[self.product.id])
        
    def test_product(self):
        response = self.client.get(self.product_url)
        self.assertEqual(response.status_code, 200)
    
class CategoryTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category_url = reverse('category', args=['Programming Books'])
        
    def test_category(self):
        response = self.client.get(self.category_url)
        self.assertEqual(response.status_code, 302)
    
class CategorySummaryTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category_summary_url = reverse('category_summary')
        
    def test_category_summary(self):
        response = self.client.get(self.category_summary_url)
        self.assertEqual(response.status_code, 200)

class SearchTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.search_url = reverse('search')
        
    def test_search(self):
        response = self.client.get(self.search_url)
        self.assertEqual(response.status_code, 200)
        
        
    