from django.conf import settings
from django.contrib import auth
from django.core.mail import send_mail
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render

from authapp.forms import ShopUserLoginForm, ShopUserRegisterForm, ShopUserEditForm, ShopUserProfilesEditForm
from django.urls import reverse

from authapp.models import ShopUser

from django.db import transaction


def login(request):
    title = 'вход',

    login_form = ShopUserLoginForm(data=request.POST or None)

    # next = request.GET.get('next', '')
    next = request.GET['next'] if 'next' in request.GET else ''

    if request.method == 'POST' and login_form.is_valid():
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            # print('request.POST', request.POST)
            # if request.POST['next']:
            if 'next' in request.POST.keys():
                return HttpResponseRedirect(request.POST['next'])
            return HttpResponseRedirect(reverse('main'))

    content = {
        'title': title,
        'login_form': login_form,
        'next': next,
    }
    return render(request, 'authapp/login.html', content)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('main'))


def register(request):
    if request.method == 'POST':
        register_form = ShopUserRegisterForm(request.POST, request.FILES)
        if register_form.is_valid():
            user = register_form.save()
            # send_verify_email(user)
            if send_verify_email(user):
                print('success')
                return HttpResponseRedirect(reverse('authapp:success'))
            else:
                print('failed')
                return HttpResponseRedirect(reverse('authapp:not_success'))
    else:
        register_form = ShopUserRegisterForm

    content = {
        'title': 'регистрация',
        'form': register_form
    }

    return render(request, 'authapp/register.html', content)


def success(request):
    content = {
        'title': 'Результат отправки запроса на активацию',
    }
    return render(request, 'authapp/success.html', content)


def not_success(request):
    content = {
        'title': 'Результат отправки запроса на активацию',
    }
    return render(request, 'authapp/not_success.html', content)


@transaction.atomic
def edit(request):
    title = 'редактирование'

    if request.method == 'POST':
        edit_form = ShopUserEditForm(request.POST, request.FILES, instance=request.user)
        profile_form = ShopUserProfilesEditForm(request.POST, instance=request.user.shopuserprofile)
        print('profile_form', profile_form)
        if edit_form.is_valid() and profile_form.is_valid():
            # profile_form.save() не пишем, тюкю отработает save() сигналу
            edit_form.save()
            return HttpResponseRedirect(reverse('auth:edit'))
    else:
        edit_form = ShopUserEditForm(instance=request.user)
        profile_form = ShopUserProfilesEditForm(instance=request.user.shopuserprofile)

    content = {
        'title': title,
        'edit_form': edit_form,
        'profile_form': profile_form,
    }

    return render(request, 'authapp/edit.html', content)


def send_verify_email(user):
    verify_link = reverse('authapp:verify', args=[user.email, user.activation_key])

    subject = f'Подтверждение учетной записи {user.email}'

    message = f'Сылка для активации: {settings.BASE_URL}{verify_link}'

    return send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)


def verify(request, email, activation_key):
    user = ShopUser.objects.get(email=email)
    if user.activation_key == activation_key and not user.id_activation_key_expired():
        user.is_active = True
        user.activation_key = ''
        user.save()
        auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return render(request, 'authapp/veryfication.html')
