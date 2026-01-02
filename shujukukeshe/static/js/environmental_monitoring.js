// 环境监测页面专用JavaScript代码

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
        const envRegionSelect = document.getElementById('env-region-select');
        if (envRegionSelect) {
            envRegionSelect.style.display = 'none';
            const label = envRegionSelect.previousElementSibling;
            if (label && label.textContent.includes('选择区域')) {
                label.style.display = 'none';
            }
        }
        return; // 区域护林员不需要加载区域列表
    }
    
    fetch('/api/resource_management/get_regions')
        .then(response => response.json())
        .then(data => {
            console.log('获取到的区域列表:', data);
            
            // 填充环境数据列表的区域选择器
            const envRegionSelect = document.getElementById('env-region-select');
            if (envRegionSelect) {
                // 保存当前选中的值
                const currentValue = envRegionSelect.value;
                
                // 清空选择器，保留"全部区域"选项
                envRegionSelect.innerHTML = '<option value="">全部区域</option>';
                
                // 填充区域选项
                if (Array.isArray(data) && data.length > 0) {
                    data.forEach(region => {
                        const option = document.createElement('option');
                        option.value = region.RegionID || region.region_id;
                        option.textContent = region.RegionName || region.region_name;
                        envRegionSelect.appendChild(option);
                    });
                }
                
                // 恢复之前的选中值
                if (currentValue) {
                    envRegionSelect.value = currentValue;
                }
            }
        })
        .catch(error => {
            console.error('加载区域列表失败:', error);
        });
}

// 刷新环境数据
function refreshEnvironmentData() {
    // 模拟刷新数据，实际应该调用API获取最新数据
    document.getElementById('realtime-temperature').textContent = (Math.random() * 20 + 10).toFixed(1);
    document.getElementById('realtime-humidity').textContent = (Math.random() * 30 + 40).toFixed(1);
    document.getElementById('realtime-windspeed').textContent = (Math.random() * 10).toFixed(1);
    document.getElementById('realtime-rainfall').textContent = (Math.random() * 5).toFixed(1);
}

// 加载环境数据列表
function loadEnvironmentData() {
    // 检查当前用户是否是区域护林员
    const currentUser = getCurrentUser();
    let regionId = '';
    
    if (currentUser.Role === '区域护林员') {
        // 区域护林员不需要选择区域，直接调用API（后端会自动根据用户ID过滤）
        regionId = '';
    } else {
        // 非区域护林员，使用选择器的值
        regionId = document.getElementById('env-region-select').value;
    }
    
    const startTime = document.getElementById('start-time').value;
    const endTime = document.getElementById('end-time').value;
    
    // 转换时间格式为YYYY-MM-DD HH:MM:SS
    const formattedStartTime = startTime.replace('T', ' ');
    const formattedEndTime = endTime.replace('T', ' ');
    
    const tableBody = document.getElementById('environment-data-table');
    tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    let url = `/api/environmental_monitoring/get_monitoring_data?region_id=${regionId}&start_time=${formattedStartTime}&end_time=${formattedEndTime}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log('获取到的环境监测数据:', data);
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">未找到匹配的监测数据</td></tr>';
                return;
            }
            
            let tableHtml = '';
            data.forEach(item => {
                tableHtml += `
                    <tr>
                        <td>${item.DataID || item.data_id || '--'}</td>
                        <td>${item.Temperature || '--'}</td>
                        <td>${item.Humidity || '--'}</td>
                        <td>${item.WindSpeed || '--'}</td>
                        <td>${item.Rainfall || '--'}</td>
                        <td>${item.DataTime || item.data_time || '--'}</td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHtml;
        })
        .catch(error => {
            console.error('加载环境监测数据失败:', error);
            tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
}

// 加载反馈表单的区域列表
function loadFeedbackRegions() {
    console.log('开始加载反馈表单区域列表...');
    
    fetch('/api/resource_management/get_regions')
        .then(response => {
            console.log('反馈表单区域列表API响应状态:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('获取到的反馈表单区域列表:', data);
            
            // 填充反馈表单的区域选择器
            const feedbackRegionSelect = document.getElementById('feedback-region');
            if (feedbackRegionSelect) {
                console.log('找到反馈表单区域选择器，开始填充选项...');
                
                // 清空选择器，保留默认选项
                feedbackRegionSelect.innerHTML = '<option value="">请选择区域</option>';
                
                // 填充区域选项
                if (Array.isArray(data) && data.length > 0) {
                    console.log(`开始填充 ${data.length} 个区域选项...`);
                    data.forEach(region => {
                        const option = document.createElement('option');
                        option.value = region.RegionID || region.region_id;
                        option.textContent = region.RegionName || region.region_name;
                        feedbackRegionSelect.appendChild(option);
                    });
                    console.log('反馈表单区域选项填充完成！');
                } else {
                    console.warn('反馈表单区域列表为空！');
                }
            } else {
                console.error('未找到反馈表单区域选择器！');
            }
        })
        .catch(error => {
            console.error('加载反馈表单区域列表失败:', error);
            alert('反馈表单区域列表加载失败，请刷新页面重试！');
        });
}

// 提交反馈表单
function submitFeedbackForm() {
    const feedbackForm = document.getElementById('feedback-form');
    if (feedbackForm) {
        feedbackForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 获取表单数据
            const formData = new FormData(this);
            const feedbackData = Object.fromEntries(formData);
            
            console.log('提交的反馈数据:', feedbackData);
            
            // 显示加载状态
            const submitButton = this.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.textContent = '提交中...';
            submitButton.disabled = true;
            
            // 发送POST请求到后端API
            fetch('/api/feedback/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(feedbackData)
            })
            .then(response => response.json())
            .then(data => {
                console.log('反馈提交结果:', data);
                
                if (data.success) {
                    // 显示成功提示
                    alert('感谢您的反馈！我们已经收到您的信息，将尽快处理。');
                    // 重置表单
                    this.reset();
                } else {
                    // 显示错误提示
                    alert('反馈提交失败: ' + (data.error || '未知错误'));
                }
            })
            .catch(error => {
                console.error('反馈提交失败:', error);
                alert('反馈提交失败: 网络错误，请稍后重试');
            })
            .finally(() => {
                // 恢复按钮状态
                submitButton.textContent = originalText;
                submitButton.disabled = false;
            });
        });
    }
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    // 初始加载环境数据区域列表
    loadRegions();
    
    // 初始加载反馈表单区域列表
    loadFeedbackRegions();
    
    // 初始化反馈表单提交处理
    submitFeedbackForm();
    
    // 设置默认时间范围为最近7天
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    // 格式化为YYYY-MM-DDTHH:MM格式
    const formattedStartDate = startDate.toISOString().slice(0, 16);
    const formattedEndDate = endDate.toISOString().slice(0, 16);
    
    document.getElementById('start-time').value = formattedStartDate;
    document.getElementById('end-time').value = formattedEndDate;
});
