from django.urls import path
from django.views.decorators.cache import cache_page

import mainapp.views as mainapp

app_name = 'mainapp'

urlpatterns = [
    path('', mainapp.products, name='index'),
    path('<int:pk>/', cache_page(360)(mainapp.products), name='category'),
    # path('<int:pk>/<int:page>', mainapp.products, name='page'),
    path('product/<int:pk>/', mainapp.product, name='product')
]
