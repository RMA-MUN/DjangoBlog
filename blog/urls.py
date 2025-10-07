from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('blog/pub-blog/', views.pub_blog, name='pub_blog'),
    path('blog/upload-image/', views.upload_image, name='upload_image'),
    path('blog/comment/', views.pub_comment, name='comment_blog'),
    path('blog/like-comment/', views.like_comment, name='like_comment'),
    path('blog/like-blog/', views.like_blog, name='like_blog'),
    path('search/', views.search_blog, name='search_blog'),
]