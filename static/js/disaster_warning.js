// 灾害预警页面专用JavaScript代码

// 获取当前用户信息（从全局变量或页面中解析）
function getCurrentUser() {
    if (window.currentUser) {
        return window.currentUser;
    }
    const userDataElement = document.getElementById('user-data');
    if (userDataElement) {
        const userId = userDataElement.dataset.userId;
        const role = userDataElement.dataset.role;
        if (userId) {
            return {
                UserID: userId,
                Role: role
            };
        }
    }
    // 尝试从用户信息文本中解析
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

// 保存预警数据，用于处理和查看详情时快速获取
let warningsData = [];

// 加载区域列表
function loadRegions() {
    // 获取当前用户信息
    const currentUser = getCurrentUser();
    
    // 区域护林员不需要区域选择（用于查看预警记录），隐藏选择器
    const warningRegionSelect = document.getElementById('warning-region-select');
    if (warningRegionSelect) {
        warningRegionSelect.style.display = 'none';
        const label = warningRegionSelect.previousElementSibling;
        if (label && label.textContent.includes('预警区域')) {
            label.style.display = 'none';
        }
    }
    
    // 填充影响区域选择器
    const affectedAreaSelect = document.getElementById('affected_area');
    if (affectedAreaSelect) {
        // 清空选择器
        affectedAreaSelect.innerHTML = '<option value="">请选择区域</option>';
        
        // 检查当前用户是否是区域护林员
        if (currentUser.Role === '区域护林员' && currentUser.ManagedRegions) {
            // 区域护林员只能看到自己管理的区域
            currentUser.ManagedRegions.forEach(region => {
                const option = document.createElement('option');
                option.value = region.RegionID;
                option.textContent = region.RegionName;
                affectedAreaSelect.appendChild(option);
            });
        } else {
            // 非区域护林员可以看到所有区域，需要从API加载
            fetch('/api/resource_management/get_regions')
                .then(response => response.json())
                .then(data => {
                    console.log('获取到的区域列表:', data);
                    
                    // 填充区域选项
                    if (Array.isArray(data) && data.length > 0) {
                        data.forEach(region => {
                            const option = document.createElement('option');
                            option.value = region.RegionID || region.region_id;
                            option.textContent = region.RegionName || region.region_name;
                            affectedAreaSelect.appendChild(option);
                        });
                    }
                })
                .catch(error => {
                    console.error('加载区域列表失败:', error);
                });
        }
    }
}



// 加载预警记录
function loadWarningRecords() {
    const tableBody = document.getElementById('warning-records-table');
    tableBody.innerHTML = '<tr><td colspan="12" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    // 获取当前用户
    const currentUser = getCurrentUser();
    
    // 构造API请求URL，区域护林员不需要region_id参数（后端会自动处理）
    let url = '/api/disaster_warning/get_warnings';
    
    // 如果不是区域护林员，则从选择器获取region_id
    if (currentUser.Role !== '区域护林员') {
        const regionId = document.getElementById('warning-region-select').value;
        url += `?region_id=${regionId}`;
    }
    
    fetch(url, {
        credentials: 'include' // 发送cookie，保持登录状态
    })
        .then(response => response.json())
        .then(data => {
            console.log('获取到的预警记录:', data);
            
            // 保存预警数据，用于处理和查看详情时快速获取
            warningsData = data;
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="12" style="text-align: center; color: #999;">未找到匹配的预警记录</td></tr>';
                return;
            }
            
            let tableHtml = '';
            data.forEach(warning => {
                // 计算处理时效
                const publishTime = new Date(warning.TriggerTime || warning.trigger_time || '');
                const handleTime = new Date(warning.HandleTime || warning.handle_time || '');
                let handleDuration = '--';
                let durationClass = '';
                
                if (!isNaN(publishTime.getTime()) && !isNaN(handleTime.getTime())) {
                    const durationMs = handleTime - publishTime;
                    const durationMinutes = Math.round(durationMs / (1000 * 60));
                    
                    if (durationMinutes < 60) {
                        handleDuration = `${durationMinutes}分钟`;
                    } else {
                        const hours = Math.floor(durationMinutes / 60);
                        const minutes = durationMinutes % 60;
                        handleDuration = `${hours}小时${minutes}分钟`;
                    }
                    
                    // 根据处理时效添加样式（严重级别预警需要在1小时内处理，其他级别需要在2小时内处理）
                    const isSevere = (warning.WarningLevel || warning.warning_level) === '严重' || (warning.WarningLevel || warning.warning_level) === '特别严重';
                    if ((isSevere && durationMinutes > 60) || (!isSevere && durationMinutes > 120)) {
                        durationClass = 'style="color: #e74c3c; font-weight: bold;"';
                    } else {
                        durationClass = 'style="color: #27ae60;"';
                    }
                } else if ((warning.Status || warning.status) === '已处理') {
                    handleDuration = '未知';
                    durationClass = 'style="color: #f39c12;"';
                }
                
                // 监督按钮（只有监管人员可以看到）
                const supervisionButton = currentUser.Role === '监管人员' ? 
                    `<button class="btn btn-warning" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" onclick="superviseWarning('${warning.WarningID || warning.warning_id}')">监督</button>` : '';
                
                tableHtml += `
                    <tr>
                        <td>${warning.WarningID || warning.warning_id || '--'}</td>
                        <td>${warning.WarningType || warning.warning_type || '--'}</td>
                        <td>${warning.WarningLevel || warning.warning_level || '--'}</td>
                        <td>${warning.WarningContent || warning.warning_content || '--'}</td>
                        <td>${warning.RegionName || warning.region_name || warning.RegionID || warning.region_id || '--'}</td>
                        <td>${warning.TriggerTime || warning.trigger_time || '--'}</td>
                        <td>${warning.Status || warning.status || '--'}</td>
                        <td>${warning.HandlerID || warning.handler_id || '--'}</td>
                        <td>${warning.HandleTime || warning.handle_time || '--'}</td>
                        <td ${durationClass}>${handleDuration}</td>
                        <td>
                            <button class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" onclick="handleWarning('${warning.WarningID || warning.warning_id}')">处理</button>
                            <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-left: 0.5rem;" onclick="viewWarningDetail('${warning.WarningID || warning.warning_id}')">详情</button>
                        </td>
                        <td>
                            ${supervisionButton}
                        </td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHtml;
            
            // 数据加载完成后检查并隐藏空列
            hideEmptyColumns(tableBody.closest('.table'));
        })
        .catch(error => {
            console.error('加载预警记录失败:', error);
            tableBody.innerHTML = '<tr><td colspan="12" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
}

// 提交预警表单
function submitWarningForm() {
    document.getElementById('warning-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const warningData = Object.fromEntries(formData);
        
        console.log('提交的预警数据:', warningData);
        
        // 发送请求到服务器
        fetch('/api/disaster_warning/publish_warning', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(warningData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('服务器返回:', data);
            
            if (data.success) {
                alert('预警信息发布成功！');
                this.reset();
                // 刷新预警记录列表
                loadWarningRecords();
            } else {
                alert('预警信息发布失败！' + (data.error || ''));
            }
        })
        .catch(error => {
            console.error('发布预警失败:', error);
            alert('预警信息发布失败，请稍后重试！');
        });
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
    // 获取当前登录用户的ID，设置为处理人ID
    const currentUser = getCurrentUser();
    document.getElementById('handle-handler_id').value = currentUser.UserID || warning.HandlerID || warning.handler_id || '';
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
            <span>${warning.RegionName || warning.region_name || warning.RegionID || warning.region_id || '--'}</span>
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

// 打开预警规则模态框
function openRuleModal() {
    const modal = document.getElementById('warning-rule-modal');
    modal.style.display = 'block';
    // 重置模态框中的选择器和表格
    document.getElementById('modal-rule-type-select').value = '';
    const tableBody = document.getElementById('modal-warning-rules-table');
    tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #999;">选择规则类型，点击查询按钮加载数据</td></tr>';
}

// 关闭预警规则模态框
function closeRuleModal() {
    const modal = document.getElementById('warning-rule-modal');
    modal.style.display = 'none';
}

// 加载预警规则到模态框
function loadRuleModalData() {
    const warningType = document.getElementById('modal-rule-type-select').value;
    const tableBody = document.getElementById('modal-warning-rules-table');
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
                        <td>${rule.IsActive ? '生效' : '失效'}</td>
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

// 点击模态框外部关闭模态框
window.onclick = function(event) {
    const handleModal = document.getElementById('warning-handle-modal');
    const detailModal = document.getElementById('warning-detail-modal');
    const ruleModal = document.getElementById('warning-rule-modal');
    
    if (event.target === handleModal) {
        handleModal.style.display = 'none';
    }
    
    if (event.target === detailModal) {
        detailModal.style.display = 'none';
    }
    
    if (event.target === ruleModal) {
        ruleModal.style.display = 'none';
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

// 根据用户角色显示不同内容
function setupRoleBasedContent() {
    const currentUser = getCurrentUser();
    console.log('当前用户角色:', currentUser.Role);
    
    // 检查是否是管理员角色
    if (currentUser.Role === '管理员' || currentUser.Role === '系统管理员') {
        // 管理员只显示预警规则管理
        document.getElementById('admin-content').style.display = 'block';
        document.getElementById('non-admin-content').style.display = 'none';
        
        // 初始化管理员内容
        loadAdminRuleData();
    } else {
        // 非管理员显示完整内容
        document.getElementById('admin-content').style.display = 'none';
        document.getElementById('non-admin-content').style.display = 'block';
        
        // 监管人员不能发布预警，隐藏发布功能
        if (currentUser.Role === '监管人员') {
            const warningForm = document.getElementById('warning-form');
            if (warningForm) {
                // 隐藏预警发布表单
                const card = warningForm.closest('.card');
                if (card) {
                    card.style.display = 'none';
                }
            }
        }
    }
}

// 保存预警规则数据，用于编辑时快速获取
let warningRulesData = [];

// 加载管理员预警规则数据
function loadAdminRuleData() {
    const warningType = document.getElementById('admin-rule-type-select').value;
    const tableBody = document.getElementById('admin-warning-rules-table');
    tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    let url = '/api/disaster_warning/get_warning_rules';
    if (warningType) {
        url += `?warning_type=${warningType}`;
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log('获取到的预警规则:', data);
            
            // 保存规则数据，用于编辑时快速获取
            warningRulesData = data;
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">未找到匹配的预警规则</td></tr>';
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
                        <td>${rule.IsActive ? '生效' : '失效'}</td>
                        <td>
                            <button class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" onclick="editWarningRule('${rule.RuleID || rule.rule_id}')">编辑</button>
                        </td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHtml;
        })
        .catch(error => {
            console.error('加载预警规则失败:', error);
            tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
}

// 编辑预警规则
function editWarningRule(ruleId) {
    // 根据规则ID查找规则数据
    const rule = warningRulesData.find(r => (r.RuleID || r.rule_id) === ruleId);
    if (!rule) {
        console.error('未找到预警规则数据:', ruleId);
        alert('未找到预警规则数据！');
        return;
    }
    
    console.log('编辑预警规则:', ruleId, rule);
    
    // 填充编辑模态框表单
    document.getElementById('edit-rule_id').value = rule.RuleID || rule.rule_id;
    document.getElementById('edit-warning_type').value = rule.WarningType || rule.warning_type;
    document.getElementById('edit-warning_level').value = rule.WarningLevel || rule.warning_level;
    document.getElementById('edit-trigger_condition').value = rule.TriggerCondition || rule.trigger_condition;
    document.getElementById('edit-is_active').value = rule.IsActive ? '1' : '0';
    
    // 显示编辑模态框
    const modal = document.getElementById('warning-rule-edit-modal');
    modal.style.display = 'block';
}

// 关闭规则编辑模态框
function closeRuleEditModal() {
    const modal = document.getElementById('warning-rule-edit-modal');
    modal.style.display = 'none';
}

// 打开预警监督模态框
function superviseWarning(warningId) {
    // 根据预警ID查找预警数据
    const warning = warningsData.find(w => (w.WarningID || w.warning_id) === warningId);
    if (!warning) {
        console.error('未找到预警数据:', warningId);
        alert('未找到预警数据！');
        return;
    }
    
    // 填充预警信息
    const warningInfoDiv = document.getElementById('supervision-warning-info');
    warningInfoDiv.innerHTML = `
        <strong>预警ID:</strong> ${warning.WarningID || warning.warning_id || '--'}<br>
        <strong>预警类型:</strong> ${warning.WarningType || warning.warning_type || '--'}<br>
        <strong>预警级别:</strong> ${warning.WarningLevel || warning.warning_level || '--'}<br>
        <strong>发布时间:</strong> ${warning.TriggerTime || warning.trigger_time || '--'}<br>
        <strong>状态:</strong> ${warning.Status || warning.status || '--'}<br>
        <strong>处理人:</strong> ${warning.HandlerID || warning.handler_id || '--'}<br>
        <strong>处理时间:</strong> ${warning.HandleTime || warning.handle_time || '--'}<br>
        <strong>处理内容:</strong> ${warning.HandleResult || warning.handle_result || '--'}
    `;
    
    // 设置预警ID
    document.getElementById('supervision-warning-id').value = warningId;
    
    // 显示监督模态框
    const modal = document.getElementById('warning-supervision-modal');
    modal.style.display = 'block';
}

// 关闭预警监督模态框
function closeSupervisionModal() {
    const modal = document.getElementById('warning-supervision-modal');
    modal.style.display = 'none';
    document.getElementById('supervision-form').reset();
}

// 处理预警监督表单提交
function submitSupervisionForm() {
    document.getElementById('supervision-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const supervisionData = Object.fromEntries(formData);
        
        console.log('提交的监督数据:', supervisionData);
        
        // 提交到服务器
        fetch('/api/disaster_warning/supervise_warning', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include', // 发送cookie，保持登录状态
            body: JSON.stringify(supervisionData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('服务器返回:', data);
            
            if (data.success) {
                alert('监督意见提交成功！');
                // 关闭模态框
                closeSupervisionModal();
                // 刷新预警记录
                loadWarningRecords();
            } else {
                alert('监督意见提交失败！');
            }
        })
        .catch(error => {
            console.error('提交监督数据失败:', error);
            alert('提交监督数据失败！');
        });
    });
}

// 提交编辑预警规则表单
function setupEditRuleForm() {
    const editForm = document.getElementById('edit-warning-rule-form');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const ruleData = Object.fromEntries(formData);
            
            // 确保is_active是布尔值或数字
            ruleData.is_active = parseInt(ruleData.is_active);
            
            console.log('提交的编辑预警规则数据:', ruleData);
            console.log('warning_level类型:', typeof ruleData.warning_level);
            console.log('warning_level值:', ruleData.warning_level);
            
            // 发送请求到服务器
            fetch('/api/disaster_warning/update_warning_rule', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(ruleData)
            })
            .then(response => {
                console.log('响应状态:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('服务器返回:', data);
                
                if (data.success) {
                    alert('预警规则更新成功！');
                    // 关闭模态框
                    closeRuleEditModal();
                    // 刷新预警规则列表
                    loadAdminRuleData();
                } else {
                    alert('预警规则更新失败！' + (data.error || ''));
                }
            })
            .catch(error => {
                console.error('更新预警规则失败:', error);
                alert('更新预警规则失败，请稍后重试！');
            });
        });
    }
}


// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    // 根据用户角色显示不同内容
    setupRoleBasedContent();
    
    // 初始加载区域列表
    loadRegions();
    
    // 初始加载预警记录
    loadWarningRecords();
    
    // 初始化表单提交处理
    submitWarningForm();
    
    // 初始化处理预警表单提交处理
    submitHandleWarningForm();
    
    // 初始化预警规则编辑表单处理
    setupEditRuleForm();
    
    // 初始化预警监督表单处理
    submitSupervisionForm();
    
    // 添加预警区域选择器变化事件监听器，自动加载预警记录
    const warningRegionSelect = document.getElementById('warning-region-select');
    if (warningRegionSelect) {
        warningRegionSelect.addEventListener('change', function() {
            console.log('预警区域选择变化，自动加载预警记录...');
            loadWarningRecords();
        });
    }
    
    // 添加管理员规则类型选择器变化事件监听器
    const adminRuleTypeSelect = document.getElementById('admin-rule-type-select');
    if (adminRuleTypeSelect) {
        adminRuleTypeSelect.addEventListener('change', function() {
            console.log('管理员规则类型选择变化，自动加载规则数据...');
            loadAdminRuleData();
        });
    }
    
    // 添加模态框外部点击关闭事件
    window.onclick = function(event) {
        // 关闭预警规则编辑模态框
        const ruleEditModal = document.getElementById('warning-rule-edit-modal');
        if (event.target === ruleEditModal) {
            ruleEditModal.style.display = 'none';
        }
    };
});
