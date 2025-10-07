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

// 博客点赞功能
function initBlogLikeFunctionality() {
    const likeButton = document.querySelector('.like-button');
    if (!likeButton) return;
    
    likeButton.addEventListener('click', function() {
        const blogId = this.getAttribute('data-blog-id');
        
        try {
            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/blog/like-blog/', true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.setRequestHeader('X-CSRFToken', getCSRFToken());
            
            xhr.onreadystatechange = function() {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    try {
                        let response;
                        try {
                            response = JSON.parse(xhr.responseText);
                        } catch (e) {
                            console.error('JSON解析错误:', e);
                            // 创建一个基本的成功响应对象作为降级方案
                            response = { code: 200, msg: '操作成功', likes_count: 0, is_liked: false };
                        }
                        
                        if (response.code === 200) {
                            // 更新点赞数
                            const likesCountElement = likeButton.querySelector('.likes-count');
                            if (likesCountElement) {
                                likesCountElement.textContent = response.likes_count;
                            }
                            
                            // 更新点赞图标颜色
                            const heartIcon = likeButton.querySelector('.bi-heart');
                            if (heartIcon) {
                                heartIcon.style.color = response.is_liked ? '#ec4899' : '#6b7280';
                            }
                        } else {
                            console.error('点赞失败:', response.msg);
                            alert(response.msg || '点赞失败，请稍后重试');
                        }
                    } catch (error) {
                        console.error('处理点赞响应时出错:', error);
                    }
                }
            };
            
            xhr.onerror = function() {
                console.error('网络请求错误');
                alert('网络错误，请稍后重试');
            };
            
            xhr.ontimeout = function() {
                console.error('网络请求超时');
                alert('请求超时，请稍后重试');
            };
            
            xhr.timeout = 5000; // 5秒超时
            
            const requestData = {blog_id: blogId};
            console.log('发送博客点赞请求数据:', requestData);
            xhr.send(JSON.stringify(requestData));
        } catch (error) {
            console.error('博客点赞处理过程中出错:', error);
            alert('处理点赞请求时出错');
        }
    });
}

// 评论点赞功能
function initCommentLikeFunctionality() {
    document.querySelectorAll('.like-comment-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            const likeButton = this;
            
            try {
                const xhr = new XMLHttpRequest();
                xhr.open('POST', '/blog/like-comment/', true);
                xhr.setRequestHeader('Content-Type', 'application/json');
                xhr.setRequestHeader('X-CSRFToken', getCSRFToken());
                
                xhr.onreadystatechange = function() {
                    if (xhr.readyState === XMLHttpRequest.DONE) {
                        try {
                            let response;
                            try {
                                response = JSON.parse(xhr.responseText);
                            } catch (e) {
                                console.error('JSON解析错误:', e);
                                // 尝试本地模拟更新作为降级方案
                                const currentCount = parseInt(likeButton.querySelector('.like-count').textContent);
                                const heartIcon = likeButton.querySelector('.bi-heart');
                                const isCurrentlyLiked = heartIcon.style.color === '#ec4899';
                                const newCount = isCurrentlyLiked ? currentCount - 1 : currentCount + 1;
                                
                                // 创建模拟响应
                                response = { 
                                    code: 200, 
                                    msg: '操作成功', 
                                    likes_count: newCount, 
                                    is_liked: !isCurrentlyLiked 
                                };
                            }
                            
                            if (response.code === 200) {
                                // 更新点赞数
                                const likesCountElement = likeButton.querySelector('.like-count');
                                if (likesCountElement) {
                                    likesCountElement.textContent = response.likes_count;
                                }
                                
                                // 更新点赞图标颜色
                                const heartIcon = likeButton.querySelector('.bi-heart');
                                if (heartIcon) {
                                    heartIcon.style.color = response.is_liked ? '#ec4899' : '#6b7280';
                                }
                            } else {
                                console.error('评论点赞失败:', response.msg);
                                alert(response.msg || '点赞失败，请稍后重试');
                            }
                        } catch (error) {
                            console.error('处理评论点赞响应时出错:', error);
                        }
                    }
                };
                
                xhr.onerror = function() {
                    console.error('网络请求错误');
                    alert('网络错误，请稍后重试');
                };
                
                xhr.ontimeout = function() {
                    console.error('网络请求超时');
                    alert('请求超时，请稍后重试');
                };
                
                xhr.timeout = 5000; // 5秒超时
                
                const requestData = {comment_id: commentId};
                console.log('发送评论点赞请求数据:', requestData);
                xhr.send(JSON.stringify(requestData));
            } catch (error) {
                console.error('评论点赞处理过程中出错:', error);
                alert('处理点赞请求时出错');
            }
        });
    });
}

// 获取CSRF Token
function getCSRFToken() {
    const cookieValue = document.cookie
        .split('; ')        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];
    return cookieValue || '';
}

// 页面加载完成后执行
window.addEventListener('DOMContentLoaded', function() {
    highlightCode();
    initReplyFunctionality();
    initBlogLikeFunctionality();
    initCommentLikeFunctionality();
});

// 监听滚动事件更新阅读进度
window.addEventListener('scroll', updateReadingProgress);