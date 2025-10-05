from django import forms
from .models import BlogCategory, Blog

class BlogForm(forms.ModelForm):
    title = forms.CharField(
        max_length=100,
        label='博客标题',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入博客标题'
        })
    )
    
    content = forms.CharField(
        label='博客内容',
        widget=forms.HiddenInput()  # 使用隐藏字段存储富文本内容
    )
    
    # 使用ModelChoiceField来处理分类，确保数据有效性
    category = forms.ModelChoiceField(
        queryset=BlogCategory.objects.all(),
        label='博客分类',
        to_field_name='id',
        empty_label='请选择分类',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def clean_category(self):
        # 验证分类是否存在
        category_id = self.cleaned_data.get('category')
        if not category_id:
            raise forms.ValidationError('请选择博客分类')
        return category_id

    class Meta:
        model = Blog
        fields = ['title', 'content', 'category']