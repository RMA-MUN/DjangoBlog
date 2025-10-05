from django.contrib import admin
from .models import BlogCategory, Blog, BlogComment

# Register your models here.

class BlogCategoryAdmin(admin.ModelAdmin):
    """博客分类模型的Admin类"""
    list_display = ('name',)


class BlogAdmin(admin.ModelAdmin):
    """博客模型的Admin类"""
    list_display = ('title', 'content', 'create_time', 'update_time', 'category', 'author')


class BlogCommentAdmin(admin.ModelAdmin):
    """博客评论模型的Admin类"""
    list_display = ('content', 'create_time', 'update_time', 'blog', 'author')

admin.site.register(BlogCategory, BlogCategoryAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(BlogComment, BlogCommentAdmin)
