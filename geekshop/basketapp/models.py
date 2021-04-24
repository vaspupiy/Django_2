from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

from mainapp.models import Product


# class BasketQuerySet(models.QuerySet):
#     def delete(self):
#         for item in self:
#             item.product.quantity += item.quantity
#             item.product.save()
#         super().delete()


class Basket(models.Model):
    # objects = BasketQuerySet.as_manager()

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='basket')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(verbose_name='количество', default=0)
    add_datetime = models.DateTimeField(verbose_name='время', auto_now_add=True)

    # class Meta:
    #     unique_together = ('user', 'product',)

    # Добавлено после просмотра вебинара №6

    @cached_property
    def get_items_cached(self):
        return self.user.basket.select_related()

    @property
    def product_cost(self):
        return self.quantity * self.product.price

    @property
    def total_quantity(self):
        # _item = Basket.objects.filter(user=self.user)
        _item = self.get_items_cached
        return sum(list(map(lambda x: x.quantity, _item)))

    @property
    def total_cost(self):
        # _item = Basket.objects.filter(user=self.user)
        _item = self.get_items_cached
        return sum(list(map(lambda x: x.product_cost, _item)))

    @staticmethod
    def get_items(user):
        return Basket.objects.filter(user=user).order_by('product__category')

    @classmethod
    def get_products_quantity(cls, user):
        basket_items = cls.get_items(user)
        basket_items_dic = {}
        [basket_items_dic.update({item.product: item.quantity}) for item in basket_items]
        return basket_items_dic

    @staticmethod
    def get_item(pk):
        return Basket.objects.get(pk=pk)


    # def delete(self):
    #     self.product.quantity += self.quantity
    #     self.product.save()
    #     super().delete()








