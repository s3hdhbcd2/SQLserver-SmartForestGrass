// 资源管理页面专用JavaScript代码

// 获取当前用户信息（从页面中解析）
function getCurrentUser() {
    const userInfoSpan = document.querySelector('.user-info span');
    if (userInfoSpan) {
        const text = userInfoSpan.textContent;
        // 更准确地提取角色，忽略后续括号中的负责区域信息
        const roleMatch = text.match(/\(([^)]+)\)(?=\(|$)/);
        if (roleMatch) {
            const role = roleMatch[1].trim();
            console.log('提取到的用户角色:', role);
            return {
                Role: role
            };
        }
    }
    console.log('未提取到用户角色');
    return { Role: '' };
}

// 保存资源数据，用于编辑时快速获取
let resourcesData = [];

// 加载资源信息列表
function loadResources() {
    // 简化逻辑，直接调用API获取资源列表，不依赖角色判断
    // 后端会根据用户角色自动过滤资源
    const tableBody = document.getElementById('resources-table');
    tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    // 获取区域选择器的值
    let regionId = '';
    const resourceRegionSelect = document.getElementById('resource-region-select');
    if (resourceRegionSelect && resourceRegionSelect.style.display !== 'none') {
        regionId = resourceRegionSelect.value;
    }
    
    let url = '/api/resource_management/get_resources';
    if (regionId) {
        url += `?region_id=${regionId}`;
        console.log('调用资源API，指定区域ID:', regionId, 'URL:', url);
    } else {
        console.log('调用资源API，获取所有负责区域的资源，URL:', url);
    }
    
    fetch(url, {
            credentials: 'include' // 发送cookie，保持登录状态
        })
        .then(response => response.json())
        .then(data => {
            console.log('获取到的资源信息:', data);
            
            // 保存资源数据，用于编辑时快速获取
            resourcesData = data;
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #999;">未找到匹配的资源信息</td></tr>';
                return;
            }
            
            let tableHtml = '';
            data.forEach(resource => {
                // 生成资源名称
                const resourceName = resource.ResourceName || resource.resource_name || `${resource.ResourceType || resource.resource_type || '资源'}-${resource.ResourceID || resource.resource_id || '000'}`;
                // 生成地理位置
                const geoLocation = resource.GeographicalLocation || resource.geographical_location || `${resource.RegionID || resource.region_id || '未知区域'}`;
                
                tableHtml += `
                    <tr>
                        <td>${resource.ResourceID || resource.resource_id || '--'}</td>
                        <td>${resource.ResourceType || resource.resource_type || '--'}</td>
                        <td>${resourceName}</td>
                        <td>${geoLocation}</td>
                        <td>${resource.CoverageArea || resource.coverage_area || '--'}</td>
                        <td>${resource.EntryTime || resource.entry_time || '--'}</td>
                        <td>
                            <button class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" onclick="editResource('${resource.ResourceID || resource.resource_id}')">编辑</button>
                            <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-left: 0.5rem;" onclick="viewResourceDetail('${resource.ResourceID || resource.resource_id}')">详情</button>
                        </td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHtml;
        })
        .catch(error => {
            console.error('加载资源信息失败:', error);
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
}

// 编辑资源
function editResource(resourceId) {
    // 根据资源ID查找资源数据
    const resource = resourcesData.find(r => (r.ResourceID || r.resource_id) === resourceId);
    if (!resource) {
        console.error('未找到资源数据:', resourceId);
        alert('未找到资源数据！');
        return;
    }
    
    console.log('编辑资源:', resourceId, resource);
    
    // 填充编辑模态框表单
    document.getElementById('edit-resource_id').value = resource.ResourceID || resource.resource_id;
    document.getElementById('edit-region_id').value = resource.RegionID || resource.region_id || '';
    document.getElementById('edit-resource_type').value = resource.ResourceType || resource.resource_type || '森林';
    document.getElementById('edit-tree_species').value = resource.TreeSpecies || resource.tree_species || '';
    document.getElementById('edit-coverage_area').value = resource.CoverageArea || resource.coverage_area || '';
    document.getElementById('edit-growth_status').value = resource.GrowthStatus || resource.growth_status || '良好';
    document.getElementById('edit-updated_by').value = resource.UpdatedBy || resource.updated_by || 'U001';
    
    // 显示编辑模态框
    const modal = document.getElementById('resource-edit-modal');
    modal.style.display = 'block';
}

// 查看资源详情
function viewResourceDetail(resourceId) {
    // 根据资源ID查找资源数据
    const resource = resourcesData.find(r => (r.ResourceID || r.resource_id) === resourceId);
    if (!resource) {
        console.error('未找到资源数据:', resourceId);
        alert('未找到资源数据！');
        return;
    }
    
    console.log('查看资源详情:', resourceId, resource);
    
    // 填充详情内容
    const detailContent = document.getElementById('resource-detail-content');
    detailContent.innerHTML = `
        <div class="detail-item">
            <label>资源ID</label>
            <span>${resource.ResourceID || resource.resource_id || '--'}</span>
        </div>
        <div class="detail-item">
            <label>区域ID</label>
            <span>${resource.RegionID || resource.region_id || '--'}</span>
        </div>
        <div class="detail-item">
            <label>资源类型</label>
            <span>${resource.ResourceType || resource.resource_type || '--'}</span>
        </div>
        <div class="detail-item">
            <label>树种</label>
            <span>${resource.TreeSpecies || resource.tree_species || '--'}</span>
        </div>
        <div class="detail-item">
            <label>数量</label>
            <span>${resource.Quantity || resource.quantity || '--'}</span>
        </div>
        <div class="detail-item">
            <label>覆盖面积 (公顷)</label>
            <span>${resource.CoverageArea || resource.coverage_area || '--'}</span>
        </div>
        <div class="detail-item">
            <label>生长状态</label>
            <span>${resource.GrowthStatus || resource.growth_status || '--'}</span>
        </div>
        <div class="detail-item">
            <label>种植时间</label>
            <span>${resource.PlantingTime || resource.planting_time || '--'}</span>
        </div>
        <div class="detail-item">
            <label>更新时间</label>
            <span>${resource.UpdateTime || resource.update_time || '--'}</span>
        </div>
        <div class="detail-item">
            <label>更新人ID</label>
            <span>${resource.UpdatedBy || resource.updated_by || '--'}</span>
        </div>
        <div class="detail-item">
            <label>资源名称</label>
            <span>${resource.ResourceName || resource.resource_name || '--'}</span>
        </div>
        <div class="detail-item">
            <label>地理位置</label>
            <span>${resource.GeographicalLocation || resource.geographical_location || '--'}</span>
        </div>
    `;
    
    // 显示模态框
    const modal = document.getElementById('resource-detail-modal');
    modal.style.display = 'block';
}

// 关闭详情模态框
function closeDetailModal() {
    const modal = document.getElementById('resource-detail-modal');
    modal.style.display = 'none';
}

// 关闭编辑模态框
function closeEditModal() {
    const modal = document.getElementById('resource-edit-modal');
    modal.style.display = 'none';
}

// 点击模态框外部关闭模态框
window.onclick = function(event) {
    const detailModal = document.getElementById('resource-detail-modal');
    const editModal = document.getElementById('resource-edit-modal');
    
    if (event.target === detailModal) {
        detailModal.style.display = 'none';
    }
    
    if (event.target === editModal) {
        editModal.style.display = 'none';
    }
}

// 处理编辑资源表单提交
function submitEditResourceForm() {
    document.getElementById('edit-resource-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const resourceData = Object.fromEntries(formData);
        
        console.log('提交的编辑资源数据:', resourceData);
        
        // 提交到服务器
        fetch('/api/resource_management/update_resource', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include', // 发送cookie，保持登录状态
            body: JSON.stringify(resourceData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('服务器返回:', data);
            
            if (data.success) {
                alert('资源信息更新成功！');
                // 关闭模态框
                closeEditModal();
                // 刷新资源列表
                loadResources();
            } else {
                alert('资源信息更新失败！');
            }
        })
        .catch(error => {
            console.error('提交资源数据失败:', error);
            alert('提交资源数据失败！');
        });
    });
}

// 加载资源变动记录
function loadResourceChanges() {
    const resourceId = document.getElementById('resource-id-input').value;
    const tableBody = document.getElementById('resource-changes-table');
    tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    let url = '/api/resource_management/get_resource_changes';
    if (resourceId) {
        url += `?resource_id=${resourceId}`;
    }
    
    fetch(url, {
            credentials: 'include' // 发送cookie，保持登录状态
        })
        .then(response => response.json())
        .then(data => {
            console.log('获取到的资源变动记录:', data);
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">未找到匹配的资源变动记录</td></tr>';
                return;
            }
            
            let tableHtml = '';
            data.forEach(change => {
                tableHtml += `
                    <tr>
                        <td>${change.ChangeID || change.change_id || '--'}</td>
                        <td>${change.ResourceID || change.resource_id || '--'}</td>
                        <td>${change.ChangeType || change.change_type || '--'}</td>
                        <td>${change.ChangeReason || change.change_reason || '--'}</td>
                        <td>${change.ChangeTime || change.change_time || '--'}</td>
                        <td>${change.OperatorID || change.operator_id || '--'}</td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHtml;
        })
        .catch(error => {
            console.error('加载资源变动记录失败:', error);
            tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
}

// 提交资源表单
function submitResourceForm() {
    document.getElementById('resource-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const resourceData = Object.fromEntries(formData);
        
        // 检查是添加还是编辑
        const isEdit = resourceData.resource_id && resourceData.resource_id !== '';
        let url = '/api/resource_management/add_resource';
        let method = 'POST';
        
        if (isEdit) {
            url = '/api/resource_management/update_resource';
            method = 'PUT';
        }
        
        // 提交到服务器
        fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include', // 发送cookie，保持登录状态
            body: JSON.stringify(resourceData)
        })
        .then(response => response.json())
        .then(data => {
            console.log('服务器返回:', data);
            
            if (data.success) {
                alert(isEdit ? '资源信息更新成功！' : '资源信息保存成功！');
                this.reset();
                // 刷新资源列表
                loadResources();
            } else {
                alert(isEdit ? '资源信息更新失败！' : '资源信息保存失败！');
            }
        })
        .catch(error => {
            console.error('提交资源数据失败:', error);
            alert('提交资源数据失败！');
        });
    });
}

// 加载区域列表
function loadRegions() {
    console.log('开始加载区域列表...');
    
    // 检查当前用户是否是区域护林员
    const currentUser = getCurrentUser();
    const isRanger = currentUser.Role === '区域护林员';
    
    if (isRanger) {
        // 区域护林员需要查询区域选择器，显示它
        const resourceRegionSelect = document.getElementById('resource-region-select');
        if (resourceRegionSelect) {
            resourceRegionSelect.style.display = 'inline-block';
            const label = resourceRegionSelect.previousElementSibling;
            if (label && label.textContent.includes('选择区域')) {
                label.style.display = 'inline-block';
            }
        }
    }
    
    fetch('/api/resource_management/get_regions', {
            credentials: 'include' // 发送cookie，保持登录状态
        })
        .then(response => {
            console.log('API响应状态:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('获取到的区域列表:', data);
            console.log('区域列表长度:', Array.isArray(data) ? data.length : 0);
            
            // 强制转换为数组，确保数据格式正确
            const regionsArray = Array.isArray(data) ? data : [];
            console.log('转换后的区域数组:', regionsArray);
            
            // 填充所有区域选择器
            const regionSelects = [
                {
                    id: 'resource-region-select',
                    hasAllOption: !isRanger
                },
                {
                    id: 'region_id',
                    hasAllOption: false
                },
                {
                    id: 'edit-region_id',
                    hasAllOption: false
                }
            ];
            
            regionSelects.forEach(selectConfig => {
                const select = document.getElementById(selectConfig.id);
                console.log(`处理区域选择器: ${selectConfig.id}`, select);
                
                if (select) {
                    // 保存当前选中的值
                    const currentValue = select.value;
                    console.log(`当前选中的值: ${currentValue}`);
                    
                    // 清空选择器
                    if (selectConfig.hasAllOption) {
                        // 保留"全部区域"选项
                        select.innerHTML = '<option value="">全部区域</option>';
                        console.log(`已重置${selectConfig.id}区域选择器，保留"全部区域"选项`);
                    } else {
                        select.innerHTML = '<option value="">请选择区域</option>';
                        console.log(`已重置${selectConfig.id}区域选择器`);
                    }
                    
                    // 填充区域选项
                    if (regionsArray.length > 0) {
                        console.log(`开始填充${selectConfig.id}区域选择器，共有${regionsArray.length}个区域`);
                        regionsArray.forEach((region, index) => {
                            const regionId = region.RegionID || region.region_id;
                            const regionName = region.RegionName || region.region_name || `未知区域${index}`;
                            console.log(`添加区域: ${regionId} - ${regionName}`);
                            
                            const option = document.createElement('option');
                            option.value = regionId;
                            option.textContent = regionName;
                            select.appendChild(option);
                        });
                        console.log(`${selectConfig.id}区域选择器填充完成`);
                    } else {
                        console.log(`没有区域数据可填充到${selectConfig.id}区域选择器`);
                    }
                    
                    // 恢复之前的选中值
                    if (currentValue) {
                        select.value = currentValue;
                        console.log(`已恢复${selectConfig.id}区域选择器的选中值: ${currentValue}`);
                    }
                } else {
                    console.error(`未找到区域选择器: ${selectConfig.id}`);
                }
            });
        })
        .catch(error => {
            console.error('加载区域列表失败:', error);
            console.error('错误详情:', error.stack);
        });
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    // 初始加载区域列表
    loadRegions();
    
    // 初始加载资源信息列表
    loadResources();
    
    // 初始加载资源变动记录
    loadResourceChanges();
    
    // 初始化表单提交处理
    submitResourceForm();
    
    // 初始化编辑表单提交处理
    submitEditResourceForm();
    
    // 添加区域选择器变化事件监听器，自动加载资源列表
    const resourceRegionSelect = document.getElementById('resource-region-select');
    if (resourceRegionSelect) {
        resourceRegionSelect.addEventListener('change', function() {
            console.log('资源列表查询区域变化，自动加载资源列表...');
            loadResources();
        });
    }
});
