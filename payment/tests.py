from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Category, Product
from django.test import Client

class PaymentTestCase(TestCase):
    def setUp(self):
        TEST_USERNAME = "test_user"
        FIRST_NAME = "John"
        LAST_NAME = "Doe"
        TEST_PASSWORD =  'secret_password'
        TEST_EMAIL = 'email@gmail.com'

        self.user_info_data = {
                    'phone': '1234567890',
                    'address1': '123 Main St',
                    'address2': 'Apt 1',
                    'city': 'Anytown',
                    'state': 'CA',
                    'zipcode': '12345',
                    'country': 'USA'
                }
        self.shipping_data = {
            'shipping_full_name': 'John Doe',
            'shipping_email': 'new_email@gmail.com',
            'shipping_address1': '123 Main St',
            'shipping_address2': 'Apt 1',
            'shipping_city': 'Anytown',
            'shipping_state': 'CA',
            'shipping_zipcode': '12345',
            'shipping_country': 'USA'}
        
        self.payment_form = {'card_name': 'John Doe', 
                        'card_number': '1234567890123456', 
                        'card_exp_date': '12/25', 
                        'card_cvv_number': '123',
                        'card_address1': '123 Main St',
                        'card_address2': 'Apt 1',
                        'card_city': 'Anytown',
                        'card_state': 'CA',
                        'card_zipcode': '12345',
                        'card_country': 'USA'}
        ### create user and login

        self.user = User.objects.create_user(username=TEST_USERNAME, email=TEST_EMAIL, password=TEST_PASSWORD)
        self.client = Client()
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)

        ## update info for user
        update_info_url = reverse('update_info')
        self.client.post(update_info_url, { **self.user_info_data, **self.shipping_data})

        ## add products and category
        self.category = Category.objects.create(name='Books')
        self.product1= Product.objects.create(name='Test Product 1', category= self.category, price=10.00, description='Test Description', image= 'uploads/product/1.png')
        self.product2= Product.objects.create(name='Test Product 2', category= self.category, price=15.00, description='Test Description', image= 'uploads/product/2.png')
        
       ## add product to cart
        add_to_cart_url = reverse('cart_add')
        # print(add_to_cart_url)
        self.client.post(add_to_cart_url, {'action': 'post', 'product_id': self.product1.id, 'product_qty': 1})
        self.client.post(add_to_cart_url, {'action': 'post', 'product_id': self.product2.id, 'product_qty': 1})
    def test_checkout_authenticated(self):
        
        # Simulate a session or request object containing cart data (optional)
        request = self.client.get(reverse('checkout'))

        response = self.client.get(reverse('checkout'), follow=True)

        # Assert successful rendering of the template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payment/checkout.html")

    def test_billing_info_authenticated(self):
        """Tests successful rendering of billing info for authenticated user
        PaymentForm:
        card_name, card_number, card_exp_date, card_cvv_number ,card_address1 card_address2, card_city, card_state, card_zipcode, card_country 
        """

        # Simulate POST request with shipping information and cart data (optional)
        
        response = self.client.post(reverse('billing_info'), self.payment_form, follow=True)

        # Assert successful rendering of the template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payment/billing_info.html")

        # Assert context data contains cart information, shipping info, and empty payment form (optional)
        self.assertEqual(len(response.context['quantities']), 2)
        
    def test_process_order(self):
        """Tests successful order processing for authenticated user
        Order:
        user, full_name, email, shipping_address, amount_paid
        """

        # Simulate POST request with payment information and cart data (optional)
        response = self.client.post(reverse('process_order'), follow=True)

        # Assert successful rendering of the template
        self.assertEqual(response.status_code, 200)

        # Assert context data contains order information (optional)
        self.assertRedirects(response, reverse('home'))
        
    def test_payment_success(self):
        """Tests successful rendering of payment success page
        """

        # Simulate a session or request object containing order data (optional)
        response = self.client.get(reverse('payment_success'))

        # Assert successful rendering of the template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payment/payment_success.html")


        