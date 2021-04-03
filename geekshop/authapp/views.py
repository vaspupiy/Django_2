from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render

from authapp.forms import ShopUserLoginForm, ShopUserRegisterForm, ShopUserEditForm
from django.urls import reverse


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
            register_form.save()
            return HttpResponseRedirect(reverse('auth:login'))
    else:
        register_form = ShopUserRegisterForm

    content = {
        'title': 'регистрация',
        'form': register_form
    }

    return render(request, 'authapp/register.html', content)


def edit(request):
    title = 'редактирование'

    if request.method == 'POST':
        print('1')
        edit_form = ShopUserEditForm(request.POST, request.FILES, instance=request.user)
        if edit_form.is_valid():
            print('2')
            edit_form.save()
            return HttpResponseRedirect(reverse('auth:edit'))
        print('5')
    else:
        print('3')
        edit_form = ShopUserEditForm(instance=request.user)

    content = {
        'title': title,
        'edit_form': edit_form
    }

    return render(request, 'authapp/edit.html', content)

