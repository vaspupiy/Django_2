from django.conf import settings
from django.test import TestCase
from django.test.client import Client

from authapp.models import ShopUser


class UserAuthTestCase(TestCase):
    success_status_code = 200
    redirect_status_code = 302
    redirect_status_code_2 = 301
    forbidden_status_code = 403

    def setUp(self):
        self.client = Client()
        self.superuser = ShopUser.objects.create_superuser('django', 'django@db.local', 'geekbrains')
        self.user = ShopUser.objects.create_user('django2', 'django2@db.local', 'geekbrains2')

    def test_user_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, self.success_status_code)
        self.assertTrue(response.context['user'].is_anonymous)
        self.assertContains(response, 'вход')
        self.assertNotContains(response, 'Пользователь', status_code=self.success_status_code)

        self.client.login(username='django2', password='geekbrains2')

        response = self.client.get('/auth/login/')
        self.assertFalse(response.context['user'].is_anonymous)
        self.assertEqual(response.context['user'], self.user)

        response = self.client.get('/')
        self.assertEqual(response.status_code, self.success_status_code)
        self.assertNotContains(response, 'вход', status_code=self.success_status_code)
        self.assertContains(response, 'Пользователь')

        response = self.client.get('/basket/')
        self.assertEqual(response.status_code, self.success_status_code)

    def test_user_register(self):
        response = self.client.get('/auth/register/')
        self.assertEqual(response.status_code, self.success_status_code)

        new_user_data = {
            'username': 'django3',
            'first_name': 'django3',
            'last_name': 'django3',
            'password1': 'geekbrains',
            'password2': 'geekbrains',
            'email': 'django3@db.local',
            'age': 33,
        }

        response = self.client.post('/auth/register/', data=new_user_data)
        self.assertEqual(response.status_code, self.redirect_status_code)

        new_user = ShopUser.objects.get(username=new_user_data['username'])
        self.assertFalse(new_user.is_active)

        activation_url = f'{settings.BASE_URL}/auth/verify/{new_user_data["email"]}/{new_user.activation_key}/'

        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, self.success_status_code)

        new_user.refresh_from_db()

        self.assertTrue(new_user.is_active)

    def test_basketapp_login_redirect(self):
        response = self.client.get('/basket/')
        self.assertEqual(response.url, '/auth/login/?next=/basket/')
        self.assertEqual(response.status_code, self.redirect_status_code)

        self.client.login(username='django2', password='geekbrains2')

        response = self.client.get('/basket/')
        self.assertEqual(response.status_code, self.success_status_code)
        self.assertEqual(list(response.context['basket']), [])
        self.assertEqual(response.request['PATH_INFO'], '/basket/')
        self.assertIn('Пользователь', response.content.decode())

    def test_user_logout(self):
        #  данные юзвера
        self.client.login(username='django2', password='geekbrains2')

        #  логинемся
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, self.success_status_code)
        self.assertFalse(response.context['user'].is_anonymous)

        #  выходим
        response = self.client.get('/auth/logout/')
        self.assertEqual(response.status_code, self.redirect_status_code)

        response = self.client.get('/')
        self.assertEqual(response.status_code, self.success_status_code)
        self.assertTrue(response.context['user'].is_anonymous)

        response = self.client.get('/basket/')
        self.assertEqual(response.status_code, self.redirect_status_code)
