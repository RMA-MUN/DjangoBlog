// 发布博客页面主脚本
window.onload = function () {
    const { createEditor, createToolbar } = window.wangEditor;
    let editor = null;
    
    // 初始化富文本编辑器
    function initEditor() {
        const editorConfig = {
            placeholder: '点击输入博客内容...',
            onChange() {
                // 自动保存到隐藏字段
                const html = editor.getHtml();
                document.getElementById('content').value = html;
            },
            // 配置上传图片的功能
            MENU_CONF: {
                uploadImage: {
                    server: '/api/upload-image/', // 图片上传接口
                    timeout: 5000, // 5秒超时
                    fieldName: 'image',
                    metaWithUrl: true,
                    // 自定义上传参数
                    meta: {
                        csrfmiddlewaretoken: document.querySelector('input[name="csrfmiddlewaretoken"]').value
                    },
                    // 上传成功回调
                    onSuccess(file, res) {
                        editor.insertText(' '); // 在图片前插入一个空格
                        editor.insertImage(res.data.url); // 插入图片
                        editor.insertText(' '); // 在图片后插入一个空格
                        return false; // 阻止默认行为
                    },
                    // 上传失败回调
                    onFailed(file, res) {
                        alert('上传图片失败: ' + (res.msg || '未知错误'));
                        return false;
                    }
                }
            }
        };

        editor = createEditor({
            selector: '#editor-container',
            html: '<p><br></p>',
            config: editorConfig,
            mode: 'default' // 或 'simple'
        });

        const toolbarConfig = {
            // 自定义工具栏配置
            excludeKeys: [] // 不排除任何按钮
        };

        const toolbar = createToolbar({
            editor,
            selector: '#toolbar-container',
            config: toolbarConfig,
            mode: 'default'
        });
    }
    
    // 创建隐藏的content字段
    function createHiddenContentField() {
        const form = document.getElementById('blog-form');
        // 先检查是否已存在content字段，如果存在则移除
        const existingContentField = document.getElementById('content');
        if (existingContentField) {
            existingContentField.remove();
        }
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = 'content';
        hiddenInput.id = 'content';
        form.appendChild(hiddenInput);
    }
    
    // 表单提交处理
    function handleFormSubmit() {
        const form = document.getElementById('blog-form');
        const submitBtn = document.getElementById('submit-btn');
        
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 验证标题
            const titleInput = document.querySelector('input[name="title"]');
            if (!titleInput.value.trim()) {
                alert('请输入博客标题');
                titleInput.focus();
                return;
            }
            
            // 验证内容
            const content = editor.getHtml();
            if (!content.trim() || content === '<p><br></p>') {
                alert('请输入博客内容');
                return;
            }
            
            // 验证分类
            const categorySelect = document.getElementById('category');
            if (!categorySelect.value) {
                alert('请选择博客分类');
                categorySelect.focus();
                return;
            }
            
            // 更新隐藏字段的值
            const contentField = document.getElementById('content');
            contentField.value = content;
            
            // 调试输出，确保隐藏字段被正确设置
            console.log('Content field value set:', contentField.value.length > 0 ? 'Yes' : 'No');
            console.log('Content preview:', content.substring(0, 100) + '...');
            
            // 显示加载状态
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 发布中...';
            
            // 准备表单数据
            const formData = new FormData(form);
            
            // 调试表单数据
            console.log('Form data being submitted:');
            formData.forEach((value, key) => {
                if (key !== 'csrfmiddlewaretoken' && key !== 'content') {
                    console.log(`${key}: ${value}`);
                }
            });
            console.log('Content field present in formData:', formData.has('content') ? 'Yes' : 'No');
            if (formData.has('content')) {
                console.log('Content length:', formData.get('content').length);
            }
            
            // 发送AJAX请求
            fetch('/public/', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                console.log('Response status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                submitBtn.disabled = false;
                submitBtn.innerHTML = '发布';
                
                if (data.code === 200) {
                    alert('发布成功！');
                    // 跳转到博客详情页
                    if (data.data && data.data.blog_id) {
                        // 使用正确的路径，移除多余的'blog/'前缀
                        window.location.href = `/detail/${data.data.blog_id}/`;
                    }
                } else {
                    alert('发布失败: ' + data.msg);
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                submitBtn.disabled = false;
                submitBtn.innerHTML = '发布';
                alert('请求错误: ' + error.message);
            });
        });
    }
    
    // 页面滚动时调整编辑器高度
    function adjustEditorHeight() {
        function updateHeight() {
            const windowHeight = window.innerHeight;
            const editorWrapper = document.querySelector('.editor-wrapper');
            const wrapperTop = editorWrapper.getBoundingClientRect().top;
            
            // 设置编辑器高度，留出适当的底部边距
            const newHeight = Math.max(300, windowHeight - wrapperTop - 150);
            document.getElementById('editor-container').style.height = newHeight + 'px';
        }
        
        // 初始化时设置一次
        updateHeight();
        
        // 监听窗口大小变化
        window.addEventListener('resize', updateHeight);
    }
    
    // 初始化
    createHiddenContentField();
    initEditor();
    handleFormSubmit();
    adjustEditorHeight();
    
    // 添加快捷键支持
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + S 保存草稿（预留功能）
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            alert('草稿保存功能暂未实现');
        }
    });
};

// 发布博客页面额外脚本
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('blog-form');
    const submitBtn = document.getElementById('submit-btn');

    if (form && submitBtn) {
        form.addEventListener('submit', function(e) {
            // 禁用提交按钮并显示加载状态
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="loader"></span> 发布中...';

            // 隐藏所有旧的错误消息
            const oldErrors = document.querySelectorAll('.error-message');
            oldErrors.forEach(el => el.remove());
        });
    }

    // 表单验证增强
    const titleInput = document.getElementById('title');
    const categorySelect = document.getElementById('category');

    if (titleInput) {
        titleInput.addEventListener('input', function() {
            this.classList.remove('is-invalid');
            const errorEl = this.nextElementSibling;
            if (errorEl && errorEl.classList.contains('error-message')) {
                errorEl.remove();
            }
        });
    }

    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            this.classList.remove('is-invalid');
            const errorEl = this.nextElementSibling;
            if (errorEl && errorEl.classList.contains('error-message')) {
                errorEl.remove();
            }
        });
    }
});