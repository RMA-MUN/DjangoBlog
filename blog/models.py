from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class BlogCategory(models.Model):
    """博客分类模型"""
    name = models.CharField(max_length=120, verbose_name='分类名称')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '博客分类'
        verbose_name_plural = verbose_name

class Blog(models.Model):
    """博客模型"""
    title = models.CharField(max_length=120, verbose_name='博客标题')
    content = models.TextField(verbose_name='博客内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, verbose_name='博客分类')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = '博客'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

class BlogComment(models.Model):
    """博客的评论模型"""
    content = models.TextField(verbose_name='评论内容')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments', verbose_name='博客')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')

    def __str__(self):
        return self.content[:20] + '...'

    class Meta:
        verbose_name = '博客评论'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']
