import json
import os
import random

from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404

from django.core.cache import cache
from basketapp.models import Basket
from mainapp.models import Product, ProductCategory
from geekshop.settings import BASE_DIR


def get_hot_product():
    products_list = Product.objects.filter(is_active=True)
    return random.choice(list(products_list))


def get_same_products(hot_product):
    same_products = Product.objects.filter(category=hot_product.category).exclude(pk=hot_product.pk)[:3]
    return same_products


def main(request):
    links_menu = [
        {'href': 'main_new', 'name': 'новинки'},
        {'href': 'main_popular', 'name': 'популярное'},
    ]
    products = Product.objects.filter(is_active=True, category__is_active=True).select_related()[:4]
    content = {
        'title': 'Главная',
        'links_menu': links_menu,
        'products': products,
    }
    return render(request, 'mainapp/index.html', content)


def get_links_menu():
    if settings.LOW_CACHE:
        key = "links_menu"
        links_menu = cache.get(key)
        if links_menu is None:
            links_menu = ProductCategory.objects.filter(is_active=True)
            cache.set(key, links_menu)
        return links_menu
    else:
        return ProductCategory.objects.filter(is_active=True)


def products(request, pk=None):
    title = 'продукты'
    # links_menu = ProductCategory.objects.all()
    links_menu = get_links_menu()
    page = request.GET.get('p', 1)

    if pk is not None:
        if pk == 0:
            products_list = Product.objects.all().order_by('-is_active', 'price')
            category_item = {'name': 'все', 'pk': 0}
        else:
            category_item = get_object_or_404(ProductCategory, pk=pk)
            products_list = Product.objects.filter(category=category_item, is_active=True)

        paginator = Paginator(products_list, 2)

        try:
            products_paginator = paginator.page(page)
        except PageNotAnInteger:
            products_paginator = paginator.page(1)
        except EmptyPage:
            products_paginator = paginator.page(paginator.num_pages)

        content = {
            'title': title,
            'links_menu': links_menu,
            'category': category_item,
            'products': products_paginator,
        }

        return render(request, 'mainapp/products_list.html', content)

    hot_product = get_hot_product()
    same_products = get_same_products(hot_product)

    content = {
        'title': title,
        'links_menu': links_menu,
        'same_products': same_products,
        'hot_product': hot_product,
    }

    return render(request, 'mainapp/products.html', content)


def product(request, pk):
    links_menu = ProductCategory.objects.all()
    content = {
        'title': 'продукт',
        'product': get_object_or_404(Product, pk=pk),
        'links_menu': links_menu,

    }
    return render(request, 'mainapp/product.html', content)


def contact(request):
    with open(os.path.join(BASE_DIR, 'mainapp/json/contact__locations.json'), 'r', encoding='utf-8') as f:
        locations = json.load(f)
    content = {
        'title': 'Контакты',
        'locations': locations,
    }
    return render(request, 'mainapp/contact.html', content)

def get_category(pk):
    if settings.LOW_CACHE:
        key = f'category_{pk}'
        category = cache.get(key)
        if category is None:
            category = ProductCategory.objects.get(pk=pk)
            cache.set(key, category)
        return category
    else:
        return ProductCategory.objects.get(pk=pk)
