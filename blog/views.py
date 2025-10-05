import uuid
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.db.models import Q
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect, reverse
from django.views.decorators.http import require_http_methods, require_POST, require_GET

from .forms import BlogForm
from .models import BlogCategory, Blog, BlogComment


# Create your views here.

def index(request) -> HttpResponse:
    # 获取所有博客并按创建时间倒序排序
    blogs = Blog.objects.all().order_by('-create_time')
    return render(request, 'index.html', {'blogs': blogs})

def blog_detail(request, blog_id) -> HttpResponse:
    """
    获取博客详情
    :param request: 请求对象
    :param blog_id: 博客ID
    :return: 渲染博客详情页面
    """
    try:
        # 修正查询方式，并使用正确的变量名
        blog = Blog.objects.get(pk=blog_id)
    except Blog.DoesNotExist:
        return HttpResponseBadRequest("博客不存在")

    # 传递正确的变量名到模板
    return render(request, 'blog_detail.html', {'blog': blog})

@login_required(login_url='author:login')
@require_http_methods(['GET', 'POST'])
def pub_blog(request) -> HttpResponse|None|JsonResponse:
    """
    发布博客
    :param request: 请求对象
    :return: 渲染发布博客页面
    """
    # 获取所有分类，用于模板中的下拉选择
    categories = BlogCategory.objects.all()
    
    if request.method == 'GET':
        form = BlogForm()  # 创建一个空的表单实例
        return render(request, 'pub_blog.html', {'form': form, 'categories': categories})
    elif request.method == 'POST':
        form = BlogForm(request.POST)
        if form.is_valid():
            blog = form.save(commit=False)  # 创建对象但不保存到数据库
            blog.author = request.user       # 添加作者信息
            blog.save()                      # 保存完整对象到数据库
            return JsonResponse({'code': 200, 'msg': '发布成功', 'data': {'blog_id': blog.id}})
        else:
                # 返回更详细的错误信息，指明具体字段
                detailed_errors = []
                for field, field_errors in form.errors.items():
                    field_name = field
                    # 映射字段名到更友好的中文名称
                    if field == 'title':
                        field_name = '博客标题'
                    elif field == 'content':
                        field_name = '博客内容'
                    elif field == 'category':
                        field_name = '博客分类'
                    
                    for error in field_errors:
                        detailed_errors.append(f'{field_name}：{error}')
                
                return JsonResponse({'code': 400, 'msg': '; '.join(detailed_errors), 'errors': form.errors})


@login_required(login_url='author:login')
@require_http_methods(['POST'])
def upload_image(request) -> JsonResponse:
    """
    处理富文本编辑器中的图片上传
    :param request: 请求对象
    :return: 图片上传结果
    """
    try:
        # 检查是否有文件
        if 'image' not in request.FILES:
            return JsonResponse({'code': 400, 'msg': '请选择要上传的图片'})
        
        # 获取上传的文件
        file = request.FILES['image']
        
        # 检查文件类型
        allowed_extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        file_extension = file.name.split('.')[-1].lower()
        if file_extension not in allowed_extensions:
            return JsonResponse({'code': 400, 'msg': '只允许上传jpg、jpeg、png、gif、webp格式的图片'})
        
        # 检查文件大小（限制为5MB）
        if file.size > 5 * 1024 * 1024:
            return JsonResponse({'code': 400, 'msg': '图片大小不能超过5MB'})
        
        # 创建上传目录结构（按年月日）
        today = datetime.now()
        upload_dir = f'uploads/images/{today.year}/{today.month}/{today.day}'
        
        # 生成唯一的文件名
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = f"{upload_dir}/{unique_filename}"
        
        # 保存文件
        with default_storage.open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # 构建返回的URL
        image_url = f"/{file_path}"
        
        # 返回成功响应
        return JsonResponse({
            'errno': 0,  # 0表示成功，非0表示失败
            'data': {
                'url': image_url,
                'alt': file.name,
                'href': image_url
            }
        })
    
    except Exception as e:
        # 捕获所有异常并返回错误信息
        return JsonResponse({'code': 500, 'msg': f'上传失败: {str(e)}'})


@require_POST
@login_required(login_url='author:login')
def pub_comment(request) -> HttpResponse:
    """
    评论博客
    :param request: 请求对象
    :return: 评论结果
    """
    blog_id = request.POST.get('blog_id')
    content = request.POST.get('content')
    
    # 添加输入验证
    if not blog_id or not content:
        return HttpResponseBadRequest("博客ID和评论内容不能为空")
        
    try:
        BlogComment.objects.create(blog_id=blog_id, content=content, author=request.user)
        # 重新加载博客详情页
        return redirect(reverse('blog:blog_detail', kwargs={'blog_id': blog_id}))
    except Exception as e:
        return HttpResponseBadRequest(f"评论失败: {str(e)}")


@require_GET
def search_blog(request) -> HttpResponse:
    """
    搜索博客
    :param request: 请求对象
    :return: 搜索结果页面
    """
    # 获取搜索关键词
    keyword = request.GET.get('Q', '').strip()
    
    if keyword:
        # 使用Q对象进行多字段搜索
        blogs = Blog.objects.filter(
            Q(title__icontains=keyword) | Q(content__icontains=keyword)
        ).order_by('-create_time')
    else:
        # 如果没有关键词，显示所有博客
        blogs = Blog.objects.all().order_by('-create_time')
    
    return render(request, 'index.html', {'blogs': blogs, 'keyword': keyword})