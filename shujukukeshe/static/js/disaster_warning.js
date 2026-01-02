// 灾害预警页面专用JavaScript代码

// 保存预警数据，用于处理和查看详情时快速获取
let warningsData = [];

// 加载区域列表
function loadRegions() {
    fetch('/api/resource_management/get_regions')
        .then(response => response.json())
        .then(data => {
            console.log('获取到的区域列表:', data);
            
            // 填充所有区域选择器
            const regionSelects = [
                'affected_area',
                'warning-region-select'
            ];
            
            regionSelects.forEach(selectId => {
                const select = document.getElementById(selectId);
                if (select) {
                    // 保存当前选中的值
                    const currentValue = select.value;
                    
                    // 清空选择器（除了第一个选项，如果是"全部区域"的话）
                    if (selectId === 'warning-region-select') {
                        // 保留"全部区域"选项
                        select.innerHTML = '<option value="">全部区域</option>';
                    } else {
                        select.innerHTML = '<option value="">请选择区域</option>';
                    }
                    
                    // 填充区域选项
                    if (Array.isArray(data) && data.length > 0) {
                        data.forEach(region => {
                            const option = document.createElement('option');
                            option.value = region.RegionID || region.region_id;
                            option.textContent = region.RegionName || region.region_name;
                            select.appendChild(option);
                        });
                    }
                    
                    // 恢复之前的选中值
                    if (currentValue) {
                        select.value = currentValue;
                    }
                }
            });
        })
        .catch(error => {
            console.error('加载区域列表失败:', error);
        });
}

// 加载预警规则
function loadWarningRules() {
    const warningType = document.getElementById('rule-type-select').value;
    const tableBody = document.getElementById('warning-rules-table');
    tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    let url = '/api/disaster_warning/get_warning_rules';
    if (warningType) {
        url += `?warning_type=${warningType}`;
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log('获取到的预警规则:', data);
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #999;">未找到匹配的预警规则</td></tr>';
                return;
            }
            
            let tableHtml = '';
            data.forEach(rule => {
                tableHtml += `
                    <tr>
                        <td>${rule.RuleID || rule.rule_id || '--'}</td>
                        <td>${rule.WarningType || rule.warning_type || '--'}</td>
                        <td>${rule.WarningLevel || rule.warning_level || '--'}</td>
                        <td>${rule.TriggerCondition || rule.trigger_condition || '--'}</td>
                        <td>${rule.IsActive === 1 ? '生效' : '失效'}</td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHtml;
        })
        .catch(error => {
            console.error('加载预警规则失败:', error);
            tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
}

// 加载预警记录
function loadWarningRecords() {
    const regionId = document.getElementById('warning-region-select').value;
    const tableBody = document.getElementById('warning-records-table');
    tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    fetch(`/api/disaster_warning/get_warnings?region_id=${regionId}`)
        .then(response => response.json())
        .then(data => {
            console.log('获取到的预警记录:', data);
            
            // 保存预警数据，用于处理和查看详情时快速获取
            warningsData = data;
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #999;">未找到匹配的预警记录</td></tr>';
                return;
            }
            
            let tableHtml = '';
            data.forEach(warning => {
                tableHtml += `
                    <tr>
                        <td>${warning.WarningID || warning.warning_id || '--'}</td>
                        <td>${warning.WarningType || warning.warning_type || '--'}</td>
                        <td>${warning.WarningLevel || warning.warning_level || '--'}</td>
                        <td>${warning.WarningContent || warning.warning_content || '--'}</td>
                        <td>${warning.RegionID || warning.region_id || '--'}</td>
                        <td>${warning.TriggerTime || warning.trigger_time || '--'}</td>
                        <td>${warning.Status || warning.status || '--'}</td>
                        <td>
                            <button class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" onclick="handleWarning('${warning.WarningID || warning.warning_id}')">处理</button>
                            <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-left: 0.5rem;" onclick="viewWarningDetail('${warning.WarningID || warning.warning_id}')">详情</button>
                        </td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHtml;
        })
        .catch(error => {
            console.error('加载预警记录失败:', error);
            tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
}

// 提交预警表单
function submitWarningForm() {
    document.getElementById('warning-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const warningData = Object.fromEntries(formData);
        
        // 这里可以添加提交到服务器的逻辑
        console.log('提交的预警数据:', warningData);
        
        // 模拟提交成功
        alert('预警信息发布成功！');
        this.reset();
    });
}

// 处理预警
function handleWarning(warningId) {
    // 根据预警ID查找预警数据
    const warning = warningsData.find(w => (w.WarningID || w.warning_id) === warningId);
    if (!warning) {
        console.error('未找到预警数据:', warningId);
        alert('未找到预警数据！');
        return;
    }
    
    console.log('处理预警:', warningId, warning);
    
    // 填充处理模态框表单
    document.getElementById('handle-warning_id').value = warning.WarningID || warning.warning_id;
    document.getElementById('handle-warning_status').value = warning.Status || warning.status || '未处理';
    document.getElementById('handle-handler_id').value = warning.HandlerID || warning.handler_id || 'U001';
    document.getElementById('handle-handle_result').value = warning.HandleResult || warning.handle_result || '';
    
    // 显示处理模态框
    const modal = document.getElementById('warning-handle-modal');
    modal.style.display = 'block';
}

// 查看预警详情
function viewWarningDetail(warningId) {
    // 根据预警ID查找预警数据
    const warning = warningsData.find(w => (w.WarningID || w.warning_id) === warningId);
    if (!warning) {
        console.error('未找到预警数据:', warningId);
        alert('未找到预警数据！');
        return;
    }
    
    console.log('查看预警详情:', warningId, warning);
    
    // 填充详情内容
    const detailContent = document.getElementById('warning-detail-content');
    detailContent.innerHTML = `
        <div class="detail-item">
            <label>预警ID</label>
            <span>${warning.WarningID || warning.warning_id || '--'}</span>
        </div>
        <div class="detail-item">
            <label>预警类型</label>
            <span>${warning.WarningType || warning.warning_type || '--'}</span>
        </div>
        <div class="detail-item">
            <label>预警级别</label>
            <span>${warning.WarningLevel || warning.warning_level || '--'}</span>
        </div>
        <div class="detail-item">
            <label>预警内容</label>
            <span>${warning.WarningContent || warning.warning_content || '--'}</span>
        </div>
        <div class="detail-item">
            <label>影响区域</label>
            <span>${warning.RegionID || warning.region_id || '--'}</span>
        </div>
        <div class="detail-item">
            <label>发布时间</label>
            <span>${warning.TriggerTime || warning.trigger_time || '--'}</span>
        </div>
        <div class="detail-item">
            <label>处理状态</label>
            <span>${warning.Status || warning.status || '--'}</span>
        </div>
        <div class="detail-item">
            <label>处理人ID</label>
            <span>${warning.HandlerID || warning.handler_id || '--'}</span>
        </div>
        <div class="detail-item">
            <label>处理结果</label>
            <span>${warning.HandleResult || warning.handle_result || '--'}</span>
        </div>
    `;
    
    // 显示详情模态框
    const modal = document.getElementById('warning-detail-modal');
    modal.style.display = 'block';
}

// 关闭处理模态框
function closeHandleModal() {
    const modal = document.getElementById('warning-handle-modal');
    modal.style.display = 'none';
}

// 关闭详情模态框
function closeDetailModal() {
    const modal = document.getElementById('warning-detail-modal');
    modal.style.display = 'none';
}

// 点击模态框外部关闭模态框
window.onclick = function(event) {
    const handleModal = document.getElementById('warning-handle-modal');
    const detailModal = document.getElementById('warning-detail-modal');
    
    if (event.target === handleModal) {
        handleModal.style.display = 'none';
    }
    
    if (event.target === detailModal) {
        detailModal.style.display = 'none';
    }
}

// 处理预警表单提交
function submitHandleWarningForm() {
    document.getElementById('handle-warning-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const handleData = Object.fromEntries(formData);
        
        console.log('提交的预警处理数据:', handleData);
        
        // 提交到服务器
        fetch('/api/disaster_warning/update_warning_status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(handleData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('服务器返回:', data);
            
            if (data.success) {
                alert('预警处理结果保存成功！');
                // 关闭模态框
                closeHandleModal();
                // 刷新预警记录列表
                loadWarningRecords();
            } else {
                alert('预警处理结果保存失败！');
            }
        })
        .catch(error => {
            console.error('提交预警处理数据失败:', error);
            alert('提交预警处理数据失败！');
        });
    });
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    // 初始加载区域列表
    loadRegions();
    
    // 初始加载预警记录
    loadWarningRecords();
    
    // 初始化表单提交处理
    submitWarningForm();
    
    // 初始化处理预警表单提交处理
    submitHandleWarningForm();
    
    // 添加预警区域选择器变化事件监听器，自动加载预警记录
    const warningRegionSelect = document.getElementById('warning-region-select');
    if (warningRegionSelect) {
        warningRegionSelect.addEventListener('change', function() {
            console.log('预警区域选择变化，自动加载预警记录...');
            loadWarningRecords();
        });
    }
    
    // 添加预警规则类型选择器变化事件监听器，自动加载预警规则
    const ruleTypeSelect = document.getElementById('rule-type-select');
    if (ruleTypeSelect) {
        ruleTypeSelect.addEventListener('change', function() {
            console.log('预警规则类型选择变化，自动加载预警规则...');
            loadWarningRules();
        });
    }
});
