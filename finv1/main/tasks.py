from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail

from .models import FinUser,Category


def categories(user):
    cates = []
    for c in Category.objects.filter(user=user):
        cates.append(f'Имя категории: {c.category_name},Баланс категории: {c.category_amount}, ')
    return cates


@shared_task
def send():
    for user in FinUser.objects.all():
        send_mail(f'Привет {user.username}',f'Ваш баланс составляет: '
                                            f'{user.account_balance}Руб.\n'
                                            f'Баланс на ваших статьях затрат:'
                                            f'{categories(user.username)}',
                                            'westsouthnothern@gmail.com', (user.email,))




