// 反馈管理页面专用JavaScript代码

// 获取当前用户信息（从页面中解析）
function getCurrentUser() {
    const userInfoSpan = document.querySelector('.user-info span');
    if (userInfoSpan) {
        const text = userInfoSpan.textContent;
        const roleMatch = text.match(/\(([^)]+)\)/);
        if (roleMatch) {
            return {
                Role: roleMatch[1]
            };
        }
    }
    return { Role: '' };
}

// 加载区域列表
function loadRegions() {
    // 检查当前用户是否是区域护林员
    const currentUser = getCurrentUser();
    if (currentUser.Role === '区域护林员') {
        // 区域护林员不需要区域选择，隐藏选择器
        const feedbackRegionSelect = document.getElementById('feedback-region-select');
        if (feedbackRegionSelect) {
            feedbackRegionSelect.style.display = 'none';
            const label = feedbackRegionSelect.previousElementSibling;
            if (label && label.textContent.includes('选择区域')) {
                label.style.display = 'none';
            }
        }
        return; // 区域护林员不需要加载区域列表
    }
    
    console.log('开始加载区域列表...');
    
    fetch('/api/resource_management/get_regions')
        .then(response => response.json())
        .then(data => {
            console.log('获取到的区域列表:', data);
            
            // 填充反馈管理页面的区域选择器
            const feedbackRegionSelect = document.getElementById('feedback-region-select');
            if (feedbackRegionSelect) {
                console.log('找到反馈管理区域选择器，开始填充选项...');
                
                // 保存当前选中的值
                const currentValue = feedbackRegionSelect.value;
                
                // 清空选择器，保留默认选项
                feedbackRegionSelect.innerHTML = '<option value="">全部区域</option>';
                
                // 填充区域选项
                if (Array.isArray(data) && data.length > 0) {
                    console.log(`开始填充 ${data.length} 个区域选项...`);
                    data.forEach(region => {
                        const option = document.createElement('option');
                        option.value = region.RegionID || region.region_id;
                        option.textContent = region.RegionName || region.region_name;
                        feedbackRegionSelect.appendChild(option);
                    });
                    console.log('反馈管理区域选项填充完成！');
                } else {
                    console.warn('反馈管理区域列表为空！');
                }
                
                // 恢复之前的选中值
                if (currentValue) {
                    feedbackRegionSelect.value = currentValue;
                }
            } else {
                console.error('未找到反馈管理区域选择器！');
            }
        })
        .catch(error => {
            console.error('加载反馈管理区域列表失败:', error);
            alert('加载区域列表失败，请刷新页面重试！');
        });
}

// 加载反馈列表
function loadFeedbacks() {
    console.log('开始加载反馈列表...');
    
    // 获取当前用户
    const currentUser = getCurrentUser();
    
    // 获取查询条件
    const status = document.getElementById('feedback-status-select').value;
    
    // 构建查询URL
    let url = '/api/feedback/get_feedbacks?';
    if (status) {
        url += `status=${status}&`;
    }
    
    // 对于非区域护林员，添加region_id参数
    if (currentUser.Role !== '区域护林员') {
        const regionId = document.getElementById('feedback-region-select').value;
        if (regionId) {
            url += `region_id=${regionId}&`;
        }
    }
    
    // 移除末尾的&符号
    url = url.replace(/&$/, '');
    
    // 显示加载状态
    const tableBody = document.getElementById('feedbacks-table');
    tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    // 发送请求获取反馈列表
    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log('获取到的反馈列表:', data);
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #999;">未找到反馈数据</td></tr>';
                return;
            }
            
            let tableHtml = '';
            data.forEach(feedback => {
                tableHtml += `
                    <tr>
                        <td>${feedback.FeedbackID || '--'}</td>
                        <td>${feedback.FeedbackType || '--'}</td>
                        <td>${feedback.RegionName || feedback.RegionID || '--'}</td>
                        <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; cursor: pointer;" title="${feedback.Description || ''}">${feedback.Description || '--'}</td>
                        <td>${feedback.Contact || '--'}</td>
                        <td>${feedback.SubmitTime ? new Date(feedback.SubmitTime).toLocaleString() : '--'}</td>
                        <td>
                            <span class="status-badge ${feedback.Status === '待处理' ? 'status-pending' : feedback.Status === '处理中' ? 'status-processing' : 'status-completed'}">
                                ${feedback.Status || '--'}
                            </span>
                        </td>
                        <td>
                            <button class="btn btn-sm btn-info" onclick="viewFeedbackDetail('${feedback.FeedbackID}')">查看详情</button>
                            ${feedback.Status === '待处理' || feedback.Status === '处理中' ? `<button class="btn btn-sm btn-primary" onclick="handleFeedback('${feedback.FeedbackID}')">处理</button>` : ''}
                        </td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHtml;
        })
        .catch(error => {
            console.error('加载反馈列表失败:', error);
            tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
}

// 查看反馈详情
function viewFeedbackDetail(feedbackId) {
    console.log(`查看反馈详情，ID: ${feedbackId}`);
    
    // 获取反馈详情
    fetch(`/api/feedback/get_feedbacks?feedback_id=${feedbackId}`)
        .then(response => response.json())
        .then(data => {
            console.log('获取到的反馈详情:', data);
            
            if (!Array.isArray(data) || data.length === 0) {
                alert('未找到反馈详情');
                return;
            }
            
            const feedback = data[0];
            
            // 填充反馈详情
            const detailContent = document.getElementById('feedback-detail-content');
            detailContent.innerHTML = `
                <div class="detail-item">
                    <label>反馈ID:</label>
                    <span>${feedback.FeedbackID || '--'}</span>
                </div>
                <div class="detail-item">
                    <label>反馈类型:</label>
                    <span>${feedback.FeedbackType || '--'}</span>
                </div>
                <div class="detail-item">
                    <label>区域名称:</label>
                    <span>${feedback.RegionName || feedback.RegionID || '--'}</span>
                </div>
                <div class="detail-item">
                    <label>详细描述:</label>
                    <span>${feedback.Description || '--'}</span>
                </div>
                <div class="detail-item">
                    <label>联系方式:</label>
                    <span>${feedback.Contact || '--'}</span>
                </div>
                <div class="detail-item">
                    <label>提交时间:</label>
                    <span>${feedback.SubmitTime ? new Date(feedback.SubmitTime).toLocaleString() : '--'}</span>
                </div>
                <div class="detail-item">
                    <label>状态:</label>
                    <span class="status-badge ${feedback.Status === '待处理' ? 'status-pending' : feedback.Status === '处理中' ? 'status-processing' : 'status-completed'}">
                        ${feedback.Status || '--'}
                    </span>
                </div>
                <div class="detail-item">
                    <label>处理人ID:</label>
                    <span>${feedback.HandlerID || '--'}</span>
                </div>
                <div class="detail-item">
                    <label>处理时间:</label>
                    <span>${feedback.HandleTime ? new Date(feedback.HandleTime).toLocaleString() : '--'}</span>
                </div>
                <div class="detail-item">
                    <label>处理结果:</label>
                    <span>${feedback.HandleResult || '--'}</span>
                </div>
            `;
            
            // 显示模态框
            const modal = document.getElementById('feedback-detail-modal');
            modal.style.display = 'block';
        })
        .catch(error => {
            console.error('获取反馈详情失败:', error);
            alert('获取反馈详情失败，请刷新页面重试');
        });
}

// 处理反馈
function handleFeedback(feedbackId) {
    console.log(`处理反馈，ID: ${feedbackId}`);
    
    // 设置反馈ID到表单中
    document.getElementById('handle-feedback-id').value = feedbackId;
    
    // 显示模态框
    const modal = document.getElementById('feedback-handle-modal');
    modal.style.display = 'block';
}

// 关闭详情模态框
function closeDetailModal() {
    const modal = document.getElementById('feedback-detail-modal');
    modal.style.display = 'none';
}

// 关闭处理模态框
function closeHandleModal() {
    const modal = document.getElementById('feedback-handle-modal');
    modal.style.display = 'none';
    // 重置表单
    document.getElementById('feedback-handle-form').reset();
}

// 提交反馈处理结果
function submitFeedbackHandleForm() {
    const handleForm = document.getElementById('feedback-handle-form');
    if (handleForm) {
        handleForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 获取表单数据
            const formData = new FormData(this);
            const handleData = Object.fromEntries(formData);
            
            console.log('提交的反馈处理数据:', handleData);
            
            // 显示加载状态
            const submitButton = this.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = '提交中...';
            submitButton.disabled = true;
            
            // 发送POST请求到后端API
            fetch('/api/feedback/update_status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(handleData)
            })
            .then(response => response.json())
            .then(data => {
                console.log('反馈处理结果:', data);
                
                if (data.success) {
                    // 显示成功提示
                    alert('反馈处理成功！');
                    // 关闭模态框
                    closeHandleModal();
                    // 重新加载反馈列表
                    loadFeedbacks();
                } else {
                    // 显示错误提示
                    alert('反馈处理失败: ' + (data.error || '未知错误'));
                }
            })
            .catch(error => {
                console.error('反馈处理失败:', error);
                alert('反馈处理失败: 网络错误，请稍后重试');
            })
            .finally(() => {
                // 恢复按钮状态
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            });
        });
    }
}

// 关闭模态框的事件监听
window.addEventListener('click', function(event) {
    // 关闭详情模态框
    const detailModal = document.getElementById('feedback-detail-modal');
    if (event.target == detailModal) {
        closeDetailModal();
    }
    
    // 关闭处理模态框
    const handleModal = document.getElementById('feedback-handle-modal');
    if (event.target == handleModal) {
        closeHandleModal();
    }
});

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    // 初始加载区域列表
    loadRegions();
    
    // 初始加载反馈列表
    loadFeedbacks();
    
    // 初始化反馈处理表单提交事件
    submitFeedbackHandleForm();
    
    // 为状态和区域选择器添加变化事件，自动重新加载数据
    const statusSelect = document.getElementById('feedback-status-select');
    if (statusSelect) {
        statusSelect.addEventListener('change', loadFeedbacks);
    }
    
    const regionSelect = document.getElementById('feedback-region-select');
    if (regionSelect) {
        regionSelect.addEventListener('change', loadFeedbacks);
    }
});
