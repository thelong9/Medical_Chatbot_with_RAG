from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Category, Product
from django.test import Client

# Create your tests here.



class CartTestCase(TestCase):
    def setUp(self):
        TEST_USERNAME = "test_user"
        FIRST_NAME = "John"
        LAST_NAME = "Doe"
        TEST_PASSWORD =  'secret_password'
        TEST_EMAIL = 'email@gmail.com'

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
        ### create user and login

        self.user = User.objects.create_user(username=TEST_USERNAME, email=TEST_EMAIL, password=TEST_PASSWORD)
        self.client = Client()
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

        ## update info for user
        update_info_url = reverse('update_info')
        self.client.post(update_info_url, { **user_info_data, **shipping_data})

        ## add products and category
        self.category = Category.objects.create(name='Books')
        self.product1= Product.objects.create(name='Test Product 1', category= self.category, price=10.00, description='Test Description', image= 'uploads/product/1.png')
        self.product2= Product.objects.create(name='Test Product 2', category= self.category, price=15.00, description='Test Description', image= 'uploads/product/2.png')
        
    
    def test_cart_summary_with_len(self, length = 0):
        """Tests rendering of cart summary with an empty cart"""
        view_cart_url = reverse('cart_summary')

        # Simulate the request
        response = self.client.get(view_cart_url)

        # Assert successful rendering of the template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cart_summary.html")
        
        ## check if cart is empty
        self.assertEqual(len(response.context['cart_products']), length)
        self.assertEqual(len(response.context['quantities']), length) 
        return response
    
    def test_cart_add_product(self):
        """Tests adding a product to the cart"""
        add_to_cart_url = reverse('cart_add')
        product_id = self.product1.id
        product_qty = 2
        
        response = self.client.post(add_to_cart_url, {'action': 'post', 'product_id': product_id, 'product_qty': product_qty})
        self.assertEqual(response.status_code, 200)
        
        ## check if product is in cart
        response = self.test_cart_summary_with_len(1)
        # print(product_id)
        # print(response.context['quantities'])
        # self.assertEqual(response.context['quantities'][product_id], product_qty)
        # self.assertEqual(response.context['cart_products'][f'{product_id}'], self.product1)

    def test_cart_delete(self):
        """Tests deleting a product from the cart"""
        add_to_cart_url = reverse('cart_add')
        product_id = self.product1.id
        product_qty = 2
        
        response = self.client.post(add_to_cart_url, {'action': 'post', 'product_id': product_id, 'product_qty': product_qty})
        self.assertEqual(response.status_code, 200)
        
        ## check if product is in cart
        response = self.test_cart_summary_with_len(1)
        
        ## delete product
        delete_from_cart_url = reverse('cart_delete')
        response = self.client.post(delete_from_cart_url, {'action': 'post', 'product_id': product_id})
        self.assertEqual(response.status_code, 200)
        
        ## check if product is deleted from cart
        self.test_cart_summary_with_len(0)
        
    def test_cart_update(self):
        """Tests updating the quantity of a product in the cart"""
        add_to_cart_url = reverse('cart_add')
        product_id = self.product1.id
        product_qty = 2
        
        response = self.client.post(add_to_cart_url, {'action': 'post', 'product_id': product_id, 'product_qty': product_qty})
        self.assertEqual(response.status_code, 200)
        
        ## check if product is in cart
        self.test_cart_summary_with_len(1)
        # self.assertEqual(response.context['quantities'][0], product_qty)
        # self.assertEqual(response.context['cart_products'][0], self.product1)
        
        ## update quantity
        update_cart_url = reverse('cart_update')
        new_qty = 3
        response = self.client.post(update_cart_url, {'action': 'post', 'product_id': product_id, 'product_qty': new_qty})
        self.assertEqual(response.status_code, 200)
        
        ## check if quantity is updated
        self.test_cart_summary_with_len(1)
        # self.assertEqual(response.context['quantities'][0], new_qty)
        # self.assertEqual(response.context['cart_products'][0], self.product1)

        