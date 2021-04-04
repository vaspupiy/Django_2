from django.urls import path

from authapp import views as authapp

app_name = 'authapp'

urlpatterns = [
    path('login/', authapp.login, name='login'),
    path('logout/', authapp.logout, name='logout'),
    path('register/', authapp.register, name='register'),
    path('edit/', authapp.edit, name='edit'),
    path('verify/<email>/<activation_key>/', authapp.verify, name='verify'),
    path('success/', authapp.success, name='success'),
    path('not_success/', authapp.not_success, name='not_success'),
]
