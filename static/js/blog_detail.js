// 代码高亮
function highlightCode() {
    // 使用highlight.js库进行代码高亮
    if (typeof hljs !== 'undefined') {
        hljs.highlightAll();
    } else {
        // 如果highlight.js不可用，至少添加基本样式
        const codeBlocks = document.querySelectorAll('pre code');
        codeBlocks.forEach(block => {
            if (block.classList.contains('language-python')) {
                block.style.backgroundColor = '#f8f9fa';
                block.style.borderRadius = '4px';
                block.style.padding = '1rem';
                block.style.display = 'block';
            }
        });
    }
}

// 阅读进度条
function updateReadingProgress() {
    const progressBar = document.getElementById('reading-progress');
    if (!progressBar) return;

    const totalHeight = document.body.scrollHeight - window.innerHeight;
    const progress = (window.pageYOffset / totalHeight) * 100;
    progressBar.style.width = progress + '%';
}

// 回复功能
function initReplyFunctionality() {
    // 显示回复表单
    document.querySelectorAll('.reply-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            if (replyForm) {
                replyForm.classList.toggle('hidden');
            }
        });
    });

    // 取消回复
    document.querySelectorAll('.cancel-reply').forEach(btn => {
        btn.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            if (replyForm) {
                replyForm.classList.add('hidden');
            }
        });
    });
}

// 保存滚动位置到localStorage
function saveScrollPosition() {
    localStorage.setItem('scrollPosition', window.scrollY.toString());
    console.log('保存滚动位置:', window.scrollY);
}

// 恢复滚动位置
function restoreScrollPosition() {
    const savedPosition = localStorage.getItem('scrollPosition');
    if (savedPosition) {
        // 延迟恢复以确保页面内容已加载
        setTimeout(() => {
            window.scrollTo(0, parseInt(savedPosition));
            console.log('恢复滚动位置:', savedPosition);
            // 恢复后清除保存的位置
            localStorage.removeItem('scrollPosition');
        }, 100);
    }
}

// 增强的CSRF Token获取函数
function getCSRFToken() {
    try {
        // 1. 从cookie中获取CSRF Token
        const cookieValue = document.cookie
            .split('; ')  // 分割cookie字符串
            .find(row => row.startsWith('csrftoken='))  // 查找以csrftoken开头的行
            ?.split('=')[1];  // 分割键值对并获取值
        
        if (cookieValue) {
            return cookieValue;
        }
        
        // 2. 如果cookie中没有，尝试从meta标签中获取
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken && metaToken.content) {
            return metaToken.content;
        }
        
        // 3. 如果meta标签中也没有，尝试从表单中的隐藏字段获取
        const formToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (formToken && formToken.value) {
            return formToken.value;
        }
        
        // 所有方法都失败
        console.error('无法通过任何方式获取CSRF Token');
        return null;
    } catch (error) {
        console.error('获取CSRF Token时发生错误:', error);
        return null;
    }
}


// 博客点赞功能 - 刷新页面版本
function initBlogLikeFunctionality() {
    // 首先尝试直接从评论表单中获取博客ID作为备用
    let globalBlogId = null;
    const commentForm = document.querySelector('form[action="/blog/comment_blog/"]');
    if (commentForm) {
        const blogIdInput = commentForm.querySelector('input[name="blog_id"]');
        if (blogIdInput && blogIdInput.value) {
            globalBlogId = blogIdInput.value;
        }
    }

    // 使用更简单直接的选择器
    const likeButton = document.querySelector('.like-button[data-blog-id]');

    // 验证元素存在
    if (!likeButton) {
        console.error('未找到博客点赞按钮或按钮没有data-blog-id属性');
        return;
    }

    likeButton.addEventListener('click', function(e) {
        e.preventDefault(); // 防止意外的默认行为

        // 获取博客ID
        const blogId = this.dataset.blogId || this.getAttribute('data-blog-id') || globalBlogId;

        // 增强的ID验证
        if (!blogId || blogId.trim() === '' || isNaN(Number(blogId))) {
            console.error('无效的博客ID:', blogId);
            alert('无法获取博客信息，请刷新页面重试。');
            return;
        }

        // 将ID转换为数字
        const numericBlogId = Number(blogId);

        try {
            // 保存滚动位置
            saveScrollPosition();

            const xhr = new XMLHttpRequest();

            // 确保URL路径正确
            xhr.open('POST', '/blog/like-blog/', true);

            // 获取并设置CSRF Token
            const csrfToken = getCSRFToken();
            if (!csrfToken) {
                console.error('无法获取CSRF Token');
                alert('无法完成操作，请刷新页面重试');
                return;
            }
            xhr.setRequestHeader('X-CSRFToken', csrfToken);

            // 响应处理
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    try {
                        // 请求完成后刷新页面
                        window.location.reload();
                    } catch (error) {
                        console.error('处理博客点赞响应时发生异常:', error);
                        alert('操作处理失败');
                    }
                }
            };

            // 错误处理 - 仍然尝试刷新，因为点赞可能已成功
            xhr.onerror = function() {
                console.error('博客点赞网络请求错误');
                // 即使出错也尝试刷新页面
                window.location.reload();
            };

            // 超时处理 - 仍然尝试刷新
            xhr.ontimeout = function() {
                console.error('博客点赞请求超时');
                // 即使超时也尝试刷新页面
                window.location.reload();
            };

            xhr.timeout = 10000; // 10秒超时

            // 发送请求
            const formData = new FormData();
            formData.append('blog_id', numericBlogId);
            console.log('发送博客点赞请求数据:', { blog_id: numericBlogId });

            xhr.send(formData);

        } catch (error) {
            console.error('发送博客点赞请求时发生错误:', error);
            alert('请求处理失败');
        }
    });
}

// 评论点赞功能 - 刷新页面
function initCommentLikeFunctionality() {
    // 获取所有评论点赞按钮
    const likeButtons = document.querySelectorAll('.like-comment-btn');

    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault(); // 防止意外的默认行为

            // 获取评论ID
            const commentId = this.dataset.commentId || this.getAttribute('data-comment-id');

            // 增强的ID验证
            if (!commentId || commentId.trim() === '' || isNaN(Number(commentId))) {
                console.error('无效的评论ID:', commentId);
                alert('无法获取评论信息，请刷新页面重试');
                return;
            }

            // 将ID转换为数字
            const numericCommentId = Number(commentId);

            try {
                // 保存滚动位置
                saveScrollPosition();

                const xhr = new XMLHttpRequest();

                // 设置请求
                xhr.open('POST', '/blog/like-comment/', true);

                // 获取并设置CSRF Token
                const csrfToken = getCSRFToken();
                if (!csrfToken) {
                    console.error('无法获取CSRF Token');
                    alert('无法完成操作，请刷新页面重试');
                    return;
                }
                xhr.setRequestHeader('X-CSRFToken', csrfToken);

                // 响应处理
                xhr.onreadystatechange = function() {
                    if (xhr.readyState === XMLHttpRequest.DONE) {
                        try {
                            // 请求完成后刷新页面
                            window.location.reload();
                        } catch (error) {
                            console.error('处理评论点赞响应时发生异常:', error);
                            alert('操作处理失败');
                        }
                    }
                };

                // 错误处理 - 仍然尝试刷新，因为点赞可能已成功
                xhr.onerror = function() {
                    console.error('评论点赞网络请求错误');
                    // 即使出错也尝试刷新页面
                    window.location.reload();
                };

                // 超时处理 - 仍然尝试刷新
                xhr.ontimeout = function() {
                    console.error('评论点赞请求超时');
                    // 即使超时也尝试刷新页面
                    window.location.reload();
                };

                xhr.timeout = 10000; // 10秒超时

                // 发送请求
                const formData = new FormData();
                formData.append('comment_id', numericCommentId);
                console.log('发送评论点赞请求数据:', { comment_id: numericCommentId });

                xhr.send(formData);

            } catch (error) {
                console.error('发送评论点赞请求时发生错误:', error);
                alert('请求处理失败');
            }
        });
    });
}

// 页面加载完成后执行
window.addEventListener('DOMContentLoaded', function() {
    highlightCode();
    initReplyFunctionality();
    initBlogLikeFunctionality();
    initCommentLikeFunctionality();
    
    // 恢复滚动位置
    restoreScrollPosition();
});

// 监听滚动事件更新阅读进度
window.addEventListener('scroll', updateReadingProgress);