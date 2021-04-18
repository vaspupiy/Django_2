import datetime

import requests
import os

from django.conf import settings
from django.utils import timezone
from social_core.exceptions import AuthForbidden

from authapp.models import ShopUserProfile, ShopUser


def save_user_profile(backend, user, response, *args, **kwargs):
    print(backend.name, response, user)
    if backend.name == 'google-oauth2':

        # ну, хоть что-то... распарсить api_url - ума не хватило, но может и нет возм., т.к. профиль закрыт с 19года...
        if response['picture'] and not user.avatar:
            url = response['picture']
            image_name = url.split("/")[-1] + '.jpg'
            pars = requests.get(url)
            with open(os.path.join(settings.BASE_DIR, f'media/users_avatars/{image_name}'), "wb") as f:
                f.write(pars.content)

            user.avatar = f'users_avatars/{image_name}'

        user.save()

    elif backend.name == 'vk-oauth2':

        api_url = f'https://api.vk.com/method/users.get?fields=bdate,sex,city,photo_max,about&access_token={response["access_token"]}&v=5.92'

        resp = requests.get(api_url)

        if resp.status_code != 200:
            return
        # print(resp.json())
        data = resp.json()['response'][0]

        if data['sex']:
            if data['sex'] == 1:
                user.shopuserprofile.gender = ShopUserProfile.FEMALE
            elif data['sex'] == 2:
                user.shopuserprofile.gender = ShopUserProfile.MALE

        if data['about']:
            data.shopuserprofile.about_me = data['about']

        if data['bdate']:
            bdate = datetime.datetime.strptime(data['bdate'], '%d.%m.%Y').date()
            age = timezone.now().date().year - bdate.year

            # if age < 180:
            if age < 18:
                user.delete()
                raise AuthForbidden('social_core.backends.vk.VKOAuth2')

            user.age = age

        if data['photo_max'] and not user.avatar:
            url = data['photo_max']
            pars = requests.get(url)
            if pars.status_code == 200:
                # image_name = url.split("/")[-1].split("?")[0]
                # image_name = user.pk
                photo_name = f'users_avatars/{user.pk}'
                with open(os.path.join(settings.BASE_DIR, f'media/{photo_name}'), "wb") as f:
                    f.write(pars.content)
                user.avatar = photo_name

        user.save()

        # if data['photo_max'] and not ShopUser.objects.get(pk=user.shopuserprofile.user_id).avatar:
        #     shop_user = ShopUser.objects.get(pk=user.shopuserprofile.user_id)
        #     url = data['photo_max']
        #     image_name = url.split("/")[-1].split("?")[0]
        #     pars = requests.get(url)
        #     with open(os.path.join(settings.BASE_DIR, f'media/users_avatars/{image_name}'), "wb") as f:
        #         f.write(pars.content)
        #     shop_user.avatar = f'users_avatars/{image_name}'
        #     shop_user.save()

        # if data['bdate']:
        #     bdate = datetime.datetime.strptime(data['bdate'], '%d.%m.%Y').date()
        #     age = timezone.now().date().year - bdate.year
        #
        #     if age < 18:
        #         user.delete()
        #         raise AuthForbidden('social_core.backends.vk.VKOAuth2')
        #     shop_user = ShopUser.objects.get(pk=user.shopuserprofile.user_id)
        #     shop_user.age = age
        #     shop_user.save()
