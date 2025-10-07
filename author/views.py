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
            if user:
                if user.check_password(password):
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
                    # 密码错误，返回错误信息
                    form.add_error('password', '密码错误')
                    return render(request, 'login.html', {'form': form})
            else:
                # 邮箱不存在，返回错误信息
                form.add_error('email', '该邮箱未注册')
                return render(request, 'login.html', {'form': form})
        else:
            # 表单验证失败，返回错误信息
            return render(request, 'login.html', {'form': form})


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
    """用户资料设置页面，实现与数据库数据比对，仅更新发生变化的字段，同时支持密码修改"""
    # 获取或创建用户资料
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    password_error = {}
    
    if request.method == 'GET':
        form = UserProfileForm(instance=profile)
        return render(request, 'settings.html', {'form': form, 'profile': profile, 'password_error': password_error})
    
    elif request.method == 'POST':
        # 检查是否是密码修改请求
        if 'password_change' in request.POST:
            # 密码修改逻辑
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            # 验证当前密码
            if not current_password:
                password_error['current_password'] = '请输入当前密码'
            elif not request.user.check_password(current_password):
                password_error['current_password'] = '当前密码错误'
            
            # 验证新密码
            if not new_password:
                password_error['new_password'] = '请输入新密码'
            elif len(new_password) < 8:
                password_error['new_password'] = '密码长度至少8位'
            elif not any(char.isalpha() for char in new_password) or not any(char.isdigit() for char in new_password):
                password_error['new_password'] = '密码必须包含字母和数字'
            
            # 验证确认密码
            if not confirm_password:
                password_error['confirm_password'] = '请确认新密码'
            elif new_password != confirm_password:
                password_error['confirm_password'] = '两次输入的密码不一致'
            
            # 如果没有错误，更新密码
            if not password_error:
                request.user.set_password(new_password)
                request.user.save()
                # 重新登录用户
                from django.contrib.auth import login as auth_login
                auth_login(request, request.user)
                messages.success(request, '密码修改成功')
                return redirect(reverse('author:settings'))
            else:
                # 密码验证失败，返回错误信息
                form = UserProfileForm(instance=profile)
                return render(request, 'settings.html', {'form': form, 'profile': profile, 'password_error': password_error})
        else:
            # 个人信息修改逻辑
            # 创建表单实例
            form = UserProfileForm(request.POST, request.FILES, instance=profile)
            
            # 获取原始数据用于比对
            original_username = request.user.username
            original_email = request.user.email
            original_bio = profile.bio
            original_avatar = profile.avatar
            has_changes = False
            
            # 处理用户名更新（仅当发生变化时）
            if 'username' in request.POST and request.POST['username']:
                new_username = request.POST['username'].strip()
                # 只有当用户名发生变化时才进行更新
                if new_username != original_username:
                    # 检查用户名长度
                    if len(new_username) < 2 or len(new_username) > 20:
                        messages.error(request, '用户名长度应在2-20个字符之间')
                        return render(request, 'settings.html', {'form': form, 'profile': profile, 'password_error': password_error})
                    # 检查用户名是否已存在
                    if User.objects.filter(username=new_username).exclude(id=request.user.id).exists():
                        messages.error(request, '该用户名已被使用')
                        return render(request, 'settings.html', {'form': form, 'profile': profile, 'password_error': password_error})
                    # 更新用户名
                    request.user.username = new_username
                    has_changes = True
            
            # 检查电子邮箱是否有变更
            new_email = request.POST.get('email', '').strip()
            if new_email and new_email != original_email:
                # 简单的邮箱格式验证
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, new_email):
                    messages.error(request, '请输入有效的邮箱地址')
                    return render(request, 'settings.html', {'form': form, 'profile': profile, 'password_error': password_error})
                
                # 检查邮箱是否已被使用
                if User.objects.filter(email=new_email).exclude(id=request.user.id).exists():
                    messages.error(request, '该邮箱已被注册')
                    return render(request, 'settings.html', {'form': form, 'profile': profile, 'password_error': password_error})
                
                # 更新邮箱
                request.user.email = new_email
                has_changes = True
            
            # 处理个人简介更新（仅当发生变化时）
            new_bio = request.POST.get('bio', '').strip()
            if new_bio != original_bio:
                # 检查简介长度
                if len(new_bio) > 500:
                    messages.error(request, '个人简介不能超过500个字符')
                    return render(request, 'settings.html', {'form': form, 'profile': profile, 'password_error': password_error})
                # 更新个人简介
                profile.bio = new_bio
                has_changes = True
            
            # 处理头像更新（仅当有新文件上传时）
            if 'avatar' in request.FILES:
                # 验证文件类型和大小
                file = request.FILES['avatar']
                allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
                if file.content_type not in allowed_types:
                    messages.error(request, '只允许上传jpg、png、gif、webp格式的图片')
                    return render(request, 'settings.html', {'form': form, 'profile': profile, 'password_error': password_error})
                
                if file.size > 2 * 1024 * 1024:
                    messages.error(request, '头像大小不能超过2MB')
                    return render(request, 'settings.html', {'form': form, 'profile': profile, 'password_error': password_error})
                
                # 如果用户已经有头像了，先删除旧头像
                if original_avatar and original_avatar != 'avatars/default.png':
                    old_avatar_path = os.path.join(settings.MEDIA_ROOT, str(original_avatar))
                    if os.path.exists(old_avatar_path):
                        try:
                            os.remove(old_avatar_path)
                        except Exception as e:
                            print(f"删除旧头像失败: {str(e)}")
                
                # 保存新头像
                profile.avatar = file
                has_changes = True
            
            # 只有当有变化时才保存数据
            if has_changes:
                # 保存用户信息和资料
                request.user.save()
                profile.save()
                messages.success(request, '资料更新成功')
            else:
                messages.info(request, '没有检测到数据变化')
            
            return redirect(reverse('author:settings'))


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
    if request.method == 'POST':
        # 先检查是否已经有了bio简介了，如果有，则删除并替换
        UserProfile.objects.filter(user=request.user).update(bio='')

        # 获取简介内容
        bio = request.POST['bio'].strip()

        # 检查简介长度（限制为500个字符）
        if len(bio) > 500:
            return JsonResponse({'code': 400, 'msg': '个人简介不能超过500个字符'})

        # 更新用户简介
        profile, created = UserProfile.objects.get_or_create(user=request.user)
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


@login_required(login_url='author:login')
@require_POST
def update_password(request):
    """处理密码更新的API"""
    # 根据当前登录的用户获取到用户实例
    user = request.user

    # 获取表单数据，如果字段不存在不会抛出异常
    current_password = request.POST.get('current-password')
    new_password = request.POST.get('new_password')
    confirm_password = request.POST.get('confirm_password')

    # 检查必要字段是否存在
    if not current_password:
        return JsonResponse({'code': 400, 'msg': '请输入当前密码'})
    if not new_password:
        return JsonResponse({'code': 400, 'msg': '请输入新密码'})

    # 检查两次输入的新密码是否一致
    if new_password != confirm_password:
        return JsonResponse({'code': 400, 'msg': '两次输入的新密码不一致'})

    # 检查旧密码是否正确
    if not user.check_password(current_password):
        return JsonResponse({'code': 400, 'msg': '旧密码错误'})

    # 检查新密码是否与旧密码相同
    # 注意：不能直接比较明文密码，因为数据库中存储的是加密后的密码
    if user.check_password(new_password):
        return JsonResponse({'code': 400, 'msg': '新密码不能与旧密码相同'})

    # 更新密码
    user.set_password(new_password)
    user.save()

    # 返回成功响应
    return render(request, 'settings.html', {'user': user, 'msg': '密码更新成功'})