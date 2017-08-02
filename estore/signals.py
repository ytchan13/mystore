from django.contrib import messages
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver


@receiver(user_logged_in)
def user_logged_in(sender, request, user, *args, **kwargs):
    messages.success(request, '登入成功')


@receiver(user_logged_out)
def user_logged_out(sender, request, user, signal, *args, **kwargs):
    messages.success(request, '已登出!')


@receiver(user_login_failed)
def user_login_failed(sender, credentials, request, *args, **kwargs):
    messages.error(request, '帳號密碼驗證失敗，請重試')