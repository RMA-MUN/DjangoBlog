// 头像上传预览功能
function setupAvatarPreview() {
    const avatarInput = document.getElementById('id_avatar');
    const avatarPreview = document.querySelector('.avatar-preview');

    if (avatarInput && avatarPreview) {
        avatarInput.addEventListener('change', function(e) {
            // 文件类型验证
            const file = e.target.files[0];
            if (!file) return;

            // 检查文件类型
            const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
            if (!allowedTypes.includes(file.type)) {
                alert('请上传 JPG、PNG、GIF 或 WebP 格式的图片');
                this.value = '';
                return;
            }

            // 检查文件大小（2MB）
            const maxSize = 2 * 1024 * 1024; // 2MB
            if (file.size > maxSize) {
                alert('图片大小不能超过 2MB');
                this.value = '';
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                avatarPreview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        });
    }
}

// 表单验证功能
function setupFormValidation() {
    const settingsForm = document.getElementById('settings-form');

    if (settingsForm) {
        settingsForm.addEventListener('submit', function(e) {
            const bioField = document.getElementById('id_bio');

            // 个人简介字符限制验证
            if (bioField && bioField.value.length > 500) {
                alert('个人简介不能超过500个字符');
                e.preventDefault();
                return false;
            }

            // 邮箱格式简单验证
            const emailField = document.getElementById('id_email');
            if (emailField && emailField.value) {
                const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
                if (!emailPattern.test(emailField.value)) {
                    alert('请输入有效的邮箱地址');
                    e.preventDefault();
                    return false;
                }
            }
        });
    }
}

// 选项卡切换动画效果
function setupTabAnimation() {
    const tabLinks = document.querySelectorAll('.nav-tabs .nav-link');

    tabLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // 添加简单的动画效果类
            const tabContent = document.querySelector(this.getAttribute('href'));
            if (tabContent) {
                tabContent.classList.add('fade');
                setTimeout(() => {
                    tabContent.classList.remove('fade');
                }, 300);
            }
        });
    });
}

// 头像放大查看功能
function initAvatarZoom() {
    const modal = document.getElementById("avatar-modal");
    const modalImg = document.getElementById("modal-img");
    const previewImg = document.getElementById("avatar-preview");
    const closeBtn = document.getElementsByClassName("close")[0];

    if (!modal || !modalImg || !previewImg || !closeBtn) return;

    // 点击头像或搜索图标时显示大图
    previewImg.onclick = function() {
        modal.style.display = "block";
        modalImg.src = this.src;
    }

    // 点击关闭按钮隐藏大图
    closeBtn.onclick = function() {
        modal.style.display = "none";
    }

    // 点击模态框背景也隐藏大图
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}

// 页面加载完成后初始化所有功能
document.addEventListener('DOMContentLoaded', function() {
    setupAvatarPreview();
    setupFormValidation();
    setupTabAnimation();
    initAvatarZoom();
});