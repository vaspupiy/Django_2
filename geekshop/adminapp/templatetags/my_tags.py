from django import template
from django.conf import settings

register = template.Library()


@register.filter(name='media_for_users')
def media_for_users(path_to_avatar):
    if not path_to_avatar:
        path_to_avatar = '/users_avatars/default_avatar.png'

    return f'{settings.MEDIA_URL}{path_to_avatar}'


def media_for_products(path_to_image):
    if not path_to_image:
        path_to_image = 'products_images/default.png'

    return f'{settings.MEDIA_URL}{path_to_image}'


@register.filter(name='only_active')
def only_active(items_list):
    """ Наверное лучше прям в контроллере фильтровать, но мало-ли..."""
    return [item for item in items_list if item.is_active]


register.filter('media_for_products', media_for_products)
