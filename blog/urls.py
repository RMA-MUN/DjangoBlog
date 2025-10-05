from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('public/', views.pub_blog, name='pub_blog'),
    # 添加图片上传API路由
    path('api/upload-image/', views.upload_image, name='upload_image'),
    path('blog/comment/', views.pub_comment, name='comment_blog'),
    path('search/', views.search_blog, name='search_blog'),
]