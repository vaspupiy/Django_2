from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import connection
from django.db.models import F
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, UpdateView, DeleteView, CreateView

from django.dispatch import receiver
from django.db.models.signals import pre_save

from mainapp.models import Product, ProductCategory

from basketapp.models import Basket


# @login_required
# def basket(request):
#     basket_item = Basket.objects.filter(user=request.user).order_by('product__category')
#     content = {
#         'title': 'корзина',
#         'basket_items': basket_item,
#     }
#     return render(request, 'basketapp/basket.html', content)

class BasketListView(ListView):
    model = Basket
    template_name = 'basketapp/basket.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = 'корзина'
        context['title'] = title
        return context

    @method_decorator(user_passes_test(lambda u: u.is_active))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


def db_profile_by_type(prefix, type, queries):
    update_queries = list(filter(lambda x: type in x['sql'], queries))
    print(f'db_profile {type} for {prefix}:')
    [print(query['sql']) for query in update_queries]


@receiver(pre_save, sender=ProductCategory)
def product_is_active_update_productcategory_save(sender, instance, **kwargs):
    if instance.pk:
        if instance.is_active:
            instance.product_set.update(is_active=True)
        else:
            instance.product_set.update(is_active=False)

        db_profile_by_type(sender, 'UPDATE', connection.queries)


@login_required()
def basket_add(request, pk):
    if 'login' in request.META.get('HTTP_REFERER'):
        return HttpResponseRedirect(reverse('products:product', args=[pk]))
    product_item = get_object_or_404(Product, pk=pk)

    basket_item = Basket.objects.filter(product=product_item, user=request.user).first()

    if not basket_item:
        basket_item = Basket(user=request.user, product=product_item)

    # basket_item.quantity += 1
    basket_item.quantity = F('quantity') + 1
    basket_item.save()

    update_queries = list(filter(lambda x: 'UPDATE' in x['sql'], connection.queries))
    print(f'f query basket_add: {update_queries}')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


# class BasketAddView(CreateView):
#     model = Basket
#
#     def get(self, request, *args, **kwargs):
#         if 'login' in request.META.get('HTTP_REFERER'):
#             return HttpResponseRedirect(reverse('products:product', args=(kwargs['pk'],)))
#         product_item = get_object_or_404(Product, pk=kwargs['pk'])
#
#         self.object = Basket.objects.filter(product=product_item, user=request.user).first()
#
#         if not self.object:
#             self.object = Basket(user=request.user, product=product_item)
#
#         self.object.quantity += 1
#         self.object.save()
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#
#     @method_decorator(user_passes_test(lambda u: u.is_active))
#     def dispatch(self, request, *args, **kwargs):
#         return super().dispatch(request, *args, **kwargs)


# @login_required
# def basket_remove(request, pk):
#     basket_item = get_object_or_404(Basket, pk=pk)
#     basket_item.delete()
#     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
#

class BasketDeleteView(DeleteView):
    model = Basket
    template_name = 'basketapp/basket.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    @method_decorator(user_passes_test(lambda u: u.is_active))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


# @login_required
# def basket_edit(request, pk, quantity):
#     if request.is_ajax():
#         quantity = int(quantity)
#         new_basket_item = Basket.objects.get(pk=int(pk))
#
#         if quantity > 0:
#             new_basket_item.quantity = quantity
#             new_basket_item.save()
#         else:
#             new_basket_item.delete()
#
#         basket_items = Basket.objects.filter(user=request.user). \
#             order_by('product__category')
#
#         content = {
#             'basket_items': basket_items,
#         }
#
#         result = render_to_string('basketapp/includes/inc_basket_list.html', content)
#
#         return JsonResponse({'result': result})

class BasketUpdateView(UpdateView):
    model = Basket
    template_name = 'basketapp/basket.html'

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            quantity = int(kwargs['quantity'])
            new_basket_item = Basket.objects.get(pk=int(kwargs['pk']))

            if quantity > 0:
                new_basket_item.quantity = quantity
                new_basket_item.save()
            else:
                new_basket_item.delete()

            object_list = Basket.objects.filter(user=request.user). \
                order_by('product__category')

            content = {
                'object_list': object_list,
            }

            result = render_to_string('basketapp/includes/inc_basket_list.html', content)
            return JsonResponse({'result': result})
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    @method_decorator(user_passes_test(lambda u: u.is_active))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
