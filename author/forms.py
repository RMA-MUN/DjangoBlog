from django import forms
from django.contrib.auth import get_user_model

from .models import Captcha, UserProfile

User = get_user_model()

class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=20, min_length=2, label="用户名",
        error_messages={
            "required": "请输入用户名",
            "min_length": "用户名长度不能小于2个字符",
            "max_length": "用户名长度不能大于20个字符"
        })
    password = forms.CharField(
        max_length=20, min_length=2, label="密码",
        error_messages={
            "required": "请输入密码",
            "min_length": "密码长度不能小于6个字符",
            "max_length": "密码长度不能大于30个字符"
        })

    email = forms.EmailField(error_messages={
        "required": "请输入邮箱",
        "invalid": "请输入正确的邮箱格式"
    })

    captcha = forms.CharField(
        max_length=6, min_length=6, label="验证码",
        error_messages={
            "required": "请输入验证码",
            "invalid": "验证码格式错误"
        })


class UserProfileForm(forms.ModelForm):
    """用户资料表单，用于处理头像上传等操作"""
    # 添加邮箱字段
    email = forms.EmailField(
        required=False,
        label="电子邮箱",
        error_messages={
            "invalid": "请输入正确的邮箱格式"
        }
    )
    
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio']
        labels = {
            'avatar': '用户头像',
            'bio': '个人简介'
        }
        error_messages = {
            'avatar': {
                'invalid_image': '请上传有效的图片文件',
            },
        }
    
    def __init__(self, *args, **kwargs):
        # 获取用户对象以填充邮箱字段
        self.user = kwargs.get('instance') and kwargs['instance'].user
        super().__init__(*args, **kwargs)
        # 如果有用户对象，设置初始邮箱值
        if self.user:
            self.fields['email'].initial = self.user.email

    def clean_bio(self):
        """验证个人简介"""
        bio = self.cleaned_data['bio'].strip()
        if len(bio) > 500:
            raise forms.ValidationError('个人简介不能超过500个字符')
        return bio

    def clean_avatar(self):
        """验证头像文件"""
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # 检查文件大小（限制为2MB）
            if avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError('头像大小不能超过2MB')
            # 检查文件类型
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if avatar.content_type not in allowed_types:
                raise forms.ValidationError('只允许上传jpg、png、gif、webp格式的图片')
        return avatar

    def clean_email(self):
        """验证注册邮箱是否已注册"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("该邮箱已被注册，请前往登录")
        return email

    def clean_captcha(self):
        """验证验证码是否正确"""
        captcha = self.cleaned_data.get('captcha')
        email = self.cleaned_data.get('email')

        # 添加更健壮的错误处理
        if not email:
            raise forms.ValidationError("请先填写邮箱")
            
        try:
            captcha_obj = Captcha.objects.filter(email=email, captcha__iexact=captcha).first()
            if not captcha_obj:
                raise forms.ValidationError("验证码错误，请重新输入")
            # 验证完成后删除验证码记录
            captcha_obj.delete()
        except Exception as e:
            print(f"验证码验证异常: {str(e)}")
            raise forms.ValidationError("验证码验证出错，请重试")
        
        return captcha

class LoginForm(forms.Form):
    password = forms.CharField(
        max_length=20, min_length=2, label="密码",
        error_messages={
            "required": "请输入密码",
            "min_length": "密码长度不能小于6个字符",
            "max_length": "密码长度不能大于30个字符"
        })

    email = forms.EmailField(error_messages={
        "required": "请输入邮箱",
        "invalid": "请输入正确的邮箱格式"
    })

    remember = forms.IntegerField(required=False)