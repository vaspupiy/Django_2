import json
import os

from django.core.management import BaseCommand
from django.conf import settings

from mainapp.models import ProductCategory, Product
from authapp.models import ShopUser


def load_from_json(file_name):
    with open(os.path.join(settings.BASE_DIR, f'mainapp/json/{file_name}.json'), 'r', encoding='utf-8') as file:
        return json.load(file)


class Command(BaseCommand):

    def handle(self, *args, **options):
        categories = load_from_json('categories')

        ProductCategory.objects.all().delete()

        for cat in categories:
            ProductCategory.objects.create(**cat)

        products = load_from_json('products')

        Product.objects.all().delete()

        for prod in products:
            _cat = ProductCategory.objects.get(name=prod['category'])
            prod['category'] = _cat
            Product.objects.create(**prod)

        ShopUser.objects.create_superuser('django', 'django@local.db', 'geekbrains', age=30)
