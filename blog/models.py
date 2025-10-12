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
    views_count = models.IntegerField(default=0, verbose_name='浏览量')
    likes_count = models.IntegerField(default=0, verbose_name='点赞数')

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
    parent_comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies', verbose_name='父评论')
    likes_count = models.IntegerField(default=0, verbose_name='点赞数')
    # is_reply字段，设置默认值为False
    is_reply = models.BooleanField(default=False, verbose_name='是否回复评论')
    # 添加一个id字段来存储这个回复评论的id
    reply_id = models.IntegerField(null=True, blank=True, verbose_name='回复评论id')

    def __str__(self):
        return self.content[:20] + '...'
    
    def save(self, *args, **kwargs):
        # 当有parent_comment时，设置is_reply为True
        self.is_reply = self.parent_comment is not None
        # 如果有parent_comment，同时设置reply_id
        if self.parent_comment:
            self.reply_id = self.parent_comment.id
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '博客评论'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']

class CommentLike(models.Model):
    """评论点赞模型"""
    comment = models.ForeignKey(BlogComment, on_delete=models.CASCADE, related_name='likes', verbose_name='评论')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='点赞用户')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')
    
    class Meta:
        unique_together = ('comment', 'user')  # 确保一个用户对一条评论只能点赞一次
        verbose_name = '评论点赞'
        verbose_name_plural = verbose_name

class BlogLike(models.Model):
    """博客点赞模型"""
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='likes', verbose_name='博客')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='点赞用户')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='点赞时间')
    
    class Meta:
        unique_together = ('blog', 'user')  # 确保一个用户对一篇博客只能点赞一次
        verbose_name = '博客点赞'
        verbose_name_plural = verbose_name