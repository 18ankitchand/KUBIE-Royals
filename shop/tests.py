from django.test import TestCase,override_settings
from django.contrib.auth import get_user_model
from .models import Product
class APIContractTests(TestCase):
 def setUp(self):
  self.user=get_user_model().objects.create_user(username='shopadmin',password='a-long-test-password',is_staff=True)
  self.data={'name':'Test Saree','category':'Sarees','originalPrice':1200,'discountPercent':20}
 def test_public_contract(self):
  response=self.client.get('/api/products');self.assertEqual(response.status_code,200)
  self.assertEqual(set(['products','categories','counts','total'])-set(response.json()),set())
  self.assertEqual(self.client.get('/api/session').json()['authenticated'],False)
 def test_requires_admin(self):self.assertEqual(self.client.post('/api/products',self.data,content_type='application/json').status_code,401)
 def test_login_crud_and_price(self):
  self.client.get('/api/session')
  self.assertEqual(self.client.post('/api/login',{'password':'a-long-test-password'},content_type='application/json').status_code,200)
  r=self.client.post('/api/products',self.data,content_type='application/json');self.assertEqual(r.status_code,201,r.content)
  obj=r.json()['product'];self.assertEqual(obj['finalPrice'],960.0)
  self.assertEqual(self.client.get('/api/products/'+str(obj['id'])).status_code,200)
  self.assertEqual(self.client.put('/api/products/'+str(obj['id']),{'featured':True},content_type='application/json').status_code,200)
  self.assertEqual(self.client.delete('/api/products/'+str(obj['id'])).status_code,200)
 def test_invalid_discount(self):
  self.client.force_login(self.user)
  self.assertEqual(self.client.post('/api/products',{**self.data,'discountPercent':100},content_type='application/json').status_code,422)
 def test_settings_requires_admin(self):self.assertEqual(self.client.put('/api/settings',{'brandName':'New'},content_type='application/json').status_code,401)
