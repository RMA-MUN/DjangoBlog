from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class Captcha(models.Model):
    email = models.EmailField(unique=True)
    captcha = models.CharField(max_length=6)
    created_time = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    """用户资料扩展模型，用于存储头像等额外信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d/', 
        default='avatars/default.png',
        verbose_name='用户头像',
        blank=True
    )
    bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'