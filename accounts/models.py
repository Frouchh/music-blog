from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    BUYER = 'buyer'
    AUTHOR = 'author'
    ADMIN = 'admin'

    name = models.CharField('Код роли', max_length=20, unique=True)
    title = models.CharField('Название', max_length=50)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

    def __str__(self):
        return self.title


class User(AbstractUser):
    email = models.EmailField('E-mail', unique=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, null=True,
                             related_name='users', verbose_name='Роль')
    is_blocked = models.BooleanField('Заблокирован', default=False)

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def has_role(self, *names):
        if self.is_superuser and Role.ADMIN in names:
            return True
        return self.role is not None and self.role.name in names

    @property
    def is_author(self):
        return self.has_role(Role.AUTHOR)

    @property
    def is_shop_admin(self):
        return self.has_role(Role.ADMIN)


class AuthorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='author_profile')
    stage_name = models.CharField('Псевдоним', max_length=100)
    payout_details = models.CharField('Реквизиты для выплат', max_length=255, blank=True)
    balance = models.DecimalField('Баланс, руб.', max_digits=12, decimal_places=2,
                                  default=Decimal('0.00'))

    class Meta:
        db_table = 'author_profiles'
        verbose_name = 'Профиль автора'
        verbose_name_plural = 'Профили авторов'

    def __str__(self):
        return self.stage_name
