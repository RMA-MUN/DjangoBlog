from django.urls import path
from . import views

app_name = 'author'

urlpatterns = [
    path('login/', views.blog_login, name='login'),
    path('register/', views.register, name='register'),
    path('email_captcha/', views.send_email_captcha, name='send_email_captcha'),  # 添加斜杠
    path('logout/', views.blog_logout, name='logout'),
    path('settings/', views.settings_view, name='settings'),
    path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('upload-bio/', views.upload_bio, name='upload_bio'),
]