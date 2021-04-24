from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now


class ShopUser(AbstractUser):
    avatar = models.ImageField(upload_to='users_avatars', blank=True)
    age = models.PositiveSmallIntegerField(verbose_name='возраст', default=18)
    activation_key = models.CharField(verbose_name='ключ подтверждения', max_length=128, blank=True)
    activation_key_expires = models.DateTimeField(
        verbose_name='актуальность ключа',
        auto_now_add=True,
        blank=True,
        null=True
    )

    def id_activation_key_expired(self):
        now_date = now() - timedelta(hours=48)
        if now_date <= self.activation_key_expires:
            return False
        return True


class ShopUserProfile(models.Model):
    MALE = 'M'
    FEMALE = 'W'

    GENDER_CHOICES = (
        (MALE, 'М'),
        (FEMALE, 'Ж'),
    )

    user = models.OneToOneField(ShopUser, unique=True, null=False, db_index=True, on_delete=models.CASCADE)
    tag_line = models.CharField(max_length=128, verbose_name='Теги', blank=True)
    about_me = models.TextField(verbose_name='о себе', blank=True, max_length=512)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name='пол', db_index=True)

    # Мы используем декоратор @receiver, который при получении определенных сигналов вызывает задекорированный метод.
    # В нашем случае сигналом является сохранение (post_save) объекта модели ShopUser (sender=ShopUser).
    @receiver(post_save, sender=ShopUser)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            ShopUserProfile.objects.create(user=instance)

    @receiver(post_save, sender=ShopUser)
    def save_user_profile(sender, instance, **kwargs):
        instance.shopuserprofile.save()
