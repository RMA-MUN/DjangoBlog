/**
 * 注册页面验证码发送功能
 */
function setupCaptchaFunctionality() {
    const getCaptchaBtn = document.querySelector('button[type="button"]');
    if (!getCaptchaBtn) {
        console.error('未找到验证码按钮');
        return;
    }
    
    getCaptchaBtn.addEventListener('click', function() {
        const email = document.getElementById('email').value;
        if (!email) {
            alert('请先输入邮箱');
            return;
        }
        
        // 简单的邮箱格式验证
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('请输入有效的邮箱地址');
            return;
        }
        
        console.log('邮箱验证通过:', email);
        
        // 显示倒计时
        let countdown = 60;
        getCaptchaBtn.disabled = true;
        getCaptchaBtn.textContent = `重新获取(${countdown}s)`;
        
        const timer = setInterval(() => {
            countdown--;
            getCaptchaBtn.textContent = `重新获取(${countdown}s)`;
            if (countdown <= 0) {
                clearInterval(timer);
                getCaptchaBtn.disabled = false;
                getCaptchaBtn.textContent = '获取验证码';
            }
        }, 1000);
        
        // 从meta标签获取CSRF令牌
        const csrfMeta = document.querySelector('meta[name="csrf-token"]');
        if (!csrfMeta) {
            console.error('未找到CSRF令牌meta标签');
            alert('系统错误，请刷新页面重试');
            clearInterval(timer);
            getCaptchaBtn.disabled = false;
            getCaptchaBtn.textContent = '获取验证码';
            return;
        }
        const csrfToken = csrfMeta.getAttribute('content');
        console.log('CSRF令牌获取成功');
        
        // 从data属性获取URL
        const captchaUrl = getCaptchaBtn.getAttribute('data-captcha-url');
        if (!captchaUrl) {
            console.error('未找到验证码URL');
            alert('系统错误，请刷新页面重试');
            clearInterval(timer);
            getCaptchaBtn.disabled = false;
            getCaptchaBtn.textContent = '获取验证码';
            return;
        }
        console.log('验证码URL获取成功:', captchaUrl);
        
        // 发送请求
        console.log('准备发送验证码请求');
        fetch(captchaUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `email=${encodeURIComponent(email)}`
        })
        .then(response => {
            console.log('请求响应状态码:', response.status);
            console.log('响应头:', response.headers);
            if (!response.ok) {
                throw new Error(`HTTP错误! 状态码: ${response.status}`);
            }
            return response.json().catch(err => {
                console.error('JSON解析错误:', err);
                // 尝试获取原始响应文本
                return response.text().then(text => {
                    console.log('原始响应文本:', text);
                    throw new Error(`响应不是有效的JSON格式: ${text}`);
                });
            });
        })
        .then(data => {
            console.log('响应数据:', data);
            if (data.code === 200) {
                alert('验证码发送成功，请查收邮箱');
                console.log('验证码发送成功');
            } else {
                alert('发送失败: ' + data.msg);
                console.error('后端返回错误:', data.msg);
                // 重置按钮状态
                clearInterval(timer);
                getCaptchaBtn.disabled = false;
                getCaptchaBtn.textContent = '获取验证码';
            }
        })
        .catch(error => {
            console.error('请求失败:', error);
            alert('发送验证码失败，请检查网络连接或稍后重试');
            // 重置按钮状态
            clearInterval(timer);
            getCaptchaBtn.disabled = false;
            getCaptchaBtn.textContent = '获取验证码';
        });
    });
}

// 当DOM加载完成后执行
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupCaptchaFunctionality);
} else {
    setupCaptchaFunctionality();
}