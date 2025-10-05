import os
import random
import string
import traceback
import uuid  # 添加uuid模块用于生成唯一ID
from datetime import datetime  # 添加datetime模块

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import BadHeaderError, HttpResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .forms import RegisterForm, LoginForm, UserProfileForm
from .models import Captcha, UserProfile

# Create your views here.

User = get_user_model()

@require_http_methods(["GET", "POST"])
def blog_login(request) -> HttpResponse|JsonResponse|None:
    """登录视图函数"""
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            remember = form.cleaned_data.get('remember')
            user = User.objects.filter(email=email).first()
            if user and user.check_password(password):
                login(request, user)
                # 是否使用记住我
                if not remember:
                    # 设置过期时间为0， 退出浏览器就过期
                    request.session.set_expiry(0)
                else:
                    # 设置过期时间为7天
                    request.session.set_expiry(60 * 60 * 24 * 7)
                # 登录成功后提示用户，跳转到首页
                messages.success(request, '登录成功')
                return redirect(reverse('blog:index'))
            else:
                # 邮箱或密码错误，返回错误信息
                messages.error(request, '邮箱或密码错误')
                return render(request, 'login.html', {'form': form})
        else:
            # 表单验证失败，返回错误信息
            messages.error(request, '表单验证失败')
            errors = form.errors.get_json_data()
            if errors:
                first_error = list(errors.values())[0][0]['message']
            else:
                first_error = "表单验证失败"
            return render(request, 'login.html', {'form': form, 'error': first_error})


def blog_logout(request) -> HttpResponse:
    """后续会增加一些逻辑，在点击退出登录后，弹出确认框，确认后才会执行退出登录操作"""
    logout(request)
    messages.success(request, '退出登录成功')
    return redirect(reverse('blog:index'))


def send_email_captcha(request) -> HttpResponse:
    email = request.POST.get('email')
    if not email:
        return JsonResponse({'code': 400, 'msg': '邮箱不能为空'})

    try:
        # 生成验证码
        captcha = ''.join(random.sample(string.ascii_uppercase + string.digits, 6))
        # 保存验证码到数据库
        Captcha.objects.update_or_create(email=email, defaults={'captcha': captcha})
        # 更新验证码发送时间
        Captcha.objects.filter(email=email).update(created_time=timezone.now())
        # 发送邮件
        send_mail(
            "DjangoBlog验证码", # 邮件标题
            f"您的验证码是：{captcha}", # 邮件内容
            settings.DEFAULT_FROM_EMAIL, # 使用settings中配置的发送方邮箱
            [email], # 接收方邮箱
            fail_silently=False, # 是否静默失败
        )
        return JsonResponse({'code': 200, 'msg': '验证码发送成功'})
    except BadHeaderError:
        return JsonResponse({'code': 400, 'msg': '邮件标题或内容格式错误'})
    except Exception as e:
        print(f"邮件发送失败: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'code': 500, 'msg': f'发送失败: {str(e)}'})


@login_required(login_url='author:login')
def settings_view(request) -> HttpResponse:
    return render(request, 'settings.html')


@require_http_methods(["GET", "POST"])
def register(request) -> HttpResponse|JsonResponse|None:
    """注册视图函数"""
    if request.method == "GET":
        return render(request, 'register.html')
    elif request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 获取表单数据
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # 创建用户
            User.objects.create_user(username=username, email=email, password=password)
            # 注册成功后提示用户登录，跳转到登录页面
            messages.success(request, '注册成功，请登录')
            return redirect(reverse('author:login'))
        else:
            # 表单验证失败，返回错误信息
            print(f"表单验证失败: {form.errors}")
            errors = form.errors.get_json_data()
            if errors:
                first_error = list(errors.values())[0][0]['message']
            else:
                first_error = "表单验证失败"
            return render(request, 'register.html', {'form': form, 'error': first_error})


@login_required(login_url='author:login')
@require_http_methods(['GET', 'POST'])
def settings_view(request) -> HttpResponse|JsonResponse|None:
    """用户资料设置页面"""
    # 获取或创建用户资料
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
        form = UserProfileForm(instance=profile)
        return render(request, 'settings.html', {'form': form, 'profile': profile})
    
    elif request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # 保存用户资料
            profile = form.save(commit=False)
            
            # 处理邮箱更新
            if 'email' in form.cleaned_data and form.cleaned_data['email']:
                request.user.email = form.cleaned_data['email']
                request.user.save()
            
            profile.save()
            messages.success(request, '资料更新成功')
            return redirect(reverse('author:settings'))
        else:
            messages.error(request, '资料更新失败，请检查输入')
            return render(request, 'settings.html', {'form': form, 'profile': profile})


@login_required(login_url='author:login')
@require_POST
def upload_avatar(request) -> HttpResponse|JsonResponse|None:
    """处理头像上传的API"""
    try:
        # 检查是否有文件
        if 'avatar' not in request.FILES:
            return JsonResponse({'code': 400, 'msg': '请选择要上传的头像'})
        
        # 获取上传的文件
        file = request.FILES['avatar']
        
        # 检查文件类型
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if file.content_type not in allowed_types:
            return JsonResponse({'code': 400, 'msg': '只允许上传jpg、png、gif、webp格式的图片'})
        
        # 检查文件大小（限制为2MB）
        if file.size > 2 * 1024 * 1024:
            return JsonResponse({'code': 400, 'msg': '头像大小不能超过2MB'})
        
        # 获取或创建用户资料
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # 如果用户已经有头像了，先删除旧头像
        if profile.avatar and profile.avatar != 'avatars/default.png':
            # 构建旧头像的完整文件路径
            old_avatar_path = os.path.join(settings.MEDIA_ROOT, str(profile.avatar))
            # 检查旧头像文件是否存在，如果存在则删除
            if os.path.exists(old_avatar_path):
                try:
                    os.remove(old_avatar_path)
                except Exception as e:
                    print(f"删除旧头像失败: {str(e)}")
        
        # 生成唯一的文件名
        file_extension = file.name.split('.')[-1].lower()  # 获取文件扩展名
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"  # 生成唯一文件名
        
        # 创建上传目录（按年月日）
        today = datetime.now()
        upload_dir = f"avatars/{today.year}/{today.month}/{today.day}"
        
        # 构建完整的文件路径
        file_path = os.path.join(upload_dir, unique_filename)
        
        # 确保上传目录存在
        os.makedirs(os.path.join(settings.MEDIA_ROOT, upload_dir), exist_ok=True)
        
        # 保存文件到指定路径
        with open(os.path.join(settings.MEDIA_ROOT, file_path), 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # 设置头像路径
        profile.avatar = file_path
        profile.save()
        
        # 返回成功响应
        return JsonResponse({
            'code': 200,
            'msg': '头像上传成功',
            'data': {
                'avatar_url': profile.avatar.url
            }
        })
    
    except Exception as e:
        # 捕获所有异常并返回错误信息
        return JsonResponse({'code': 500, 'msg': f'上传失败: {str(e)}'})

@login_required(login_url='author:login')
@require_POST
def upload_bio(request) -> HttpResponse|JsonResponse|None:
    """处理个人简介上传的API"""
    try:
        # 检查是否有简介
        if 'bio' not in request.POST:
            return JsonResponse({'code': 400, 'msg': '请输入个人简介'})

        # 获取简介内容
        bio = request.POST['bio'].strip()

        # 检查简介长度（限制为500个字符）
        if len(bio) > 500:
            return JsonResponse({'code': 400, 'msg': '个人简介不能超过500个字符'})

        # 获取或创建用户资料
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        # 更新简介
        profile.bio = bio
        profile.save()

        # 返回成功响应
        return JsonResponse({
            'code': 200,
            'msg': '个人简介上传成功',
            'data': {
                'bio': profile.bio
            }
        })

    except Exception as e:
        # 捕获所有异常并返回错误信息
        return JsonResponse({'code': 500, 'msg': f'上传失败: {str(e)}'})