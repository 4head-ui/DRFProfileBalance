from django.db import models
from django.contrib.auth.models import AbstractUser


class FinUser(AbstractUser):
    account_balance = models.FloatField(verbose_name='Баланс пользователя',
                                        null=True,blank=True,default=0)

    class Meta(AbstractUser.Meta):
        pass


class Amounttake(models.Model):
    amount = models.FloatField(verbose_name='Сумма поступления',default=0)
    amount_date = models.DateTimeField(auto_now_add=True,db_index=True,
                                       verbose_name='Время начисления')
    company = models.CharField(max_length=20,verbose_name='Отправитель')
    description = models.TextField(verbose_name='Описание')
    name_of_category = models.CharField(max_length=30,verbose_name='Имя категории',
                                         blank=True,null=True)
    user = models.ForeignKey(FinUser,on_delete=models.PROTECT,to_field='username',
                             blank=True,null=True,verbose_name='Пользователь')

    class Meta:
        verbose_name_plural = 'Поступления'
        verbose_name = 'Поступление'


class Category(models.Model):
    user = models.ForeignKey(FinUser,on_delete=models.CASCADE,blank=True,to_field='username',
                             null=True,verbose_name='Пользователь')
    category_name = models.CharField(max_length=20,verbose_name='Категория')
    category_amount = models.FloatField(verbose_name='Баланс категории',default=0)

    class Meta:
        verbose_name_plural = 'Категории'
        verbose_name = 'Категория'
        ordering = ['category_name']

    def __str__(self):
        return f'{self.category_name}'