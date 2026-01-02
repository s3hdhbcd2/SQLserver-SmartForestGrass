// 设备管理页面专用JavaScript代码

// 保存设备数据，用于编辑时快速获取
let devicesData = [];

// 加载区域列表
function loadRegions() {
    fetch('/api/resource_management/get_regions')
        .then(response => response.json())
        .then(data => {
            console.log('获取到的区域列表:', data);
            
            // 填充所有区域选择器
            const regionSelects = [
                {
                    id: 'device-region-select',
                    hasAllOption: true
                },
                {
                    id: 'installation_location',
                    hasAllOption: false
                },
                {
                    id: 'edit-installation_location',
                    hasAllOption: false
                }
            ];
            
            regionSelects.forEach(selectConfig => {
                const select = document.getElementById(selectConfig.id);
                if (select) {
                    // 保存当前选中的值
                    const currentValue = select.value;
                    
                    // 清空选择器
                    if (selectConfig.hasAllOption) {
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

// 加载设备档案列表
function loadDevices() {
    const regionId = document.getElementById('device-region-select').value;
    const deviceType = document.getElementById('device-type-select').value;
    const tableBody = document.getElementById('devices-table');
    tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    let url = '/api/equipment_management/get_devices';
    const params = [];
    
    if (regionId) {
        params.push(`region_id=${regionId}`);
    }
    if (deviceType) {
        params.push(`device_type=${deviceType}`);
    }
    
    if (params.length > 0) {
        url += `?${params.join('&')}`;
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log('获取到的设备档案:', data);
            
            // 保存设备数据，用于编辑时快速获取
            devicesData = data;
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #999;">未找到匹配的设备档案</td></tr>';
                return;
            }
            
            let tableHtml = '';
            let deviceSelectHtml = '<option value="">请选择设备</option>';
            
            data.forEach(device => {
                const deviceId = device.DeviceID || device.device_id;
                const deviceName = device.DeviceName || device.device_name || '未知设备';
                
                // 填充设备档案表格
                tableHtml += `
                    <tr>
                        <td>${deviceId || '--'}</td>
                        <td>${deviceName}</td>
                        <td>${device.DeviceType || device.device_type || '--'}</td>
                        <td>${device.ModelSpecification || device.model_specification || '--'}</td>
                        <td>${device.PurchaseTime || device.purchase_time || '--'}</td>
                        <td>${device.RegionID || device.region_id || '--'}</td>
                        <td>
                            <button class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" onclick="editEquipment('${deviceId}')">编辑</button>
                            <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-left: 0.5rem;" onclick="viewEquipmentDetail('${deviceId}')">详情</button>
                        </td>
                    </tr>
                `;
                
                // 填充设备状态查询的设备选择器
                deviceSelectHtml += `<option value="${deviceId}">${deviceName} (${deviceId})</option>`;
            });
            
            tableBody.innerHTML = tableHtml;
            // 更新设备选择器
            const deviceSelect = document.getElementById('device-id-select');
            if (deviceSelect) {
                deviceSelect.innerHTML = deviceSelectHtml;
            }
        })
        .catch(error => {
            console.error('加载设备档案失败:', error);
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
}

// 加载设备状态
function loadDeviceStatus() {
    const deviceId = document.getElementById('device-id-select').value;
    const startTime = document.getElementById('status-start-time').value;
    const endTime = document.getElementById('status-end-time').value;
    const tableBody = document.getElementById('device-status-table');
    tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    if (!deviceId) {
        tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">请选择设备ID</td></tr>';
        return;
    }
    
    // 转换时间格式为YYYY-MM-DD HH:MM:SS
    const formattedStartTime = startTime.replace('T', ' ');
    const formattedEndTime = endTime.replace('T', ' ');
    
    const url = `/api/equipment_management/get_device_status?device_id=${deviceId}&start_time=${formattedStartTime}&end_time=${formattedEndTime}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log('获取到的设备状态:', data);
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">未找到匹配的设备状态数据</td></tr>';
                return;
            }
            
            let tableHtml = '';
            data.forEach(status => {
                tableHtml += `
                    <tr>
                        <td>${status.StatusID || status.status_id || '--'}</td>
                        <td>${status.DeviceID || status.device_id || '--'}</td>
                        <td>${status.CollectionTime || status.collection_time || '--'}</td>
                        <td>${status.RunningStatus || status.running_status || '--'}</td>
                        <td>${status.BatteryLevel || status.battery_level || '--'}</td>
                        <td>${status.SignalStrength || status.signal_strength || '--'}</td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHtml;
        })
        .catch(error => {
            console.error('加载设备状态失败:', error);
            tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
}

// 编辑设备
function editEquipment(deviceId) {
    // 根据设备ID查找设备数据
    const device = devicesData.find(d => (d.DeviceID || d.device_id) === deviceId);
    if (!device) {
        console.error('未找到设备数据:', deviceId);
        alert('未找到设备数据！');
        return;
    }
    
    console.log('编辑设备:', deviceId, device);
    
    // 填充编辑模态框表单
    document.getElementById('edit-equipment_id').value = device.DeviceID || device.device_id;
    document.getElementById('edit-equipment_name').value = device.DeviceName || device.device_name || '';
    document.getElementById('edit-equipment_type').value = device.DeviceType || device.device_type || '温度传感器';
    document.getElementById('edit-installation_location').value = device.RegionID || device.region_id || 'R001';
    document.getElementById('edit-equipment_status').value = device.Status || device.status || '正常';
    // 格式化日期，去掉时间部分
    const purchaseTime = device.PurchaseTime || device.purchase_time;
    const formattedDate = purchaseTime ? purchaseTime.split(' ')[0] : '';
    document.getElementById('edit-last_maintenance_date').value = formattedDate;
    
    // 显示编辑模态框
    const modal = document.getElementById('equipment-edit-modal');
    modal.style.display = 'block';
}

// 查看设备详情
function viewEquipmentDetail(deviceId) {
    // 根据设备ID查找设备数据
    const device = devicesData.find(d => (d.DeviceID || d.device_id) === deviceId);
    if (!device) {
        console.error('未找到设备数据:', deviceId);
        alert('未找到设备数据！');
        return;
    }
    
    console.log('查看设备详情:', deviceId, device);
    
    // 填充详情内容
    const detailContent = document.getElementById('equipment-detail-content');
    detailContent.innerHTML = `
        <div class="detail-item">
            <label>设备ID</label>
            <span>${device.DeviceID || device.device_id || '--'}</span>
        </div>
        <div class="detail-item">
            <label>设备名称</label>
            <span>${device.DeviceName || device.device_name || '--'}</span>
        </div>
        <div class="detail-item">
            <label>设备类型</label>
            <span>${device.DeviceType || device.device_type || '--'}</span>
        </div>
        <div class="detail-item">
            <label>型号规格</label>
            <span>${device.ModelSpecification || device.model_specification || '--'}</span>
        </div>
        <div class="detail-item">
            <label>购买时间</label>
            <span>${device.PurchaseTime || device.purchase_time || '--'}</span>
        </div>
        <div class="detail-item">
            <label>安装位置</label>
            <span>${device.RegionID || device.region_id || '--'}</span>
        </div>
        <div class="detail-item">
            <label>安装人员ID</label>
            <span>${device.InstallerID || device.installer_id || '--'}</span>
        </div>
        <div class="detail-item">
            <label>保修期</label>
            <span>${device.WarrantyPeriod || device.warranty_period || '--'} 年</span>
        </div>
    `;
    
    // 显示详情模态框
    const modal = document.getElementById('equipment-detail-modal');
    modal.style.display = 'block';
}

// 关闭编辑模态框
function closeEditModal() {
    const modal = document.getElementById('equipment-edit-modal');
    modal.style.display = 'none';
}

// 关闭详情模态框
function closeDetailModal() {
    const modal = document.getElementById('equipment-detail-modal');
    modal.style.display = 'none';
}

// 点击模态框外部关闭模态框
window.onclick = function(event) {
    const editModal = document.getElementById('equipment-edit-modal');
    const detailModal = document.getElementById('equipment-detail-modal');
    
    if (event.target === editModal) {
        editModal.style.display = 'none';
    }
    
    if (event.target === detailModal) {
        detailModal.style.display = 'none';
    }
}

// 提交设备表单
function submitDeviceForm() {
    const equipmentForm = document.getElementById('equipment-form');
    if (equipmentForm) {
        equipmentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const deviceData = Object.fromEntries(formData);
            
            // 这里可以添加提交到服务器的逻辑
            console.log('提交的设备数据:', deviceData);
            
            // 模拟提交成功
            alert('设备信息保存成功！');
            this.reset();
            // 刷新设备列表
            loadDevices();
        });
    }
}

// 提交编辑设备表单
function submitEditDeviceForm() {
    const editForm = document.getElementById('edit-equipment-form');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const deviceData = Object.fromEntries(formData);
            
            // 这里可以添加提交到服务器的逻辑
            console.log('提交的编辑设备数据:', deviceData);
            
            // 模拟提交成功
            alert('设备信息更新成功！');
            // 关闭模态框
            closeEditModal();
            // 刷新设备列表
            loadDevices();
        });
    }
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    // 初始加载区域列表
    loadRegions();
    
    // 初始加载设备档案列表
    loadDevices();
    
    // 设置默认时间范围为最近24小时
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - 24 * 60 * 60 * 1000);
    
    // 格式化为YYYY-MM-DDTHH:MM格式
    const formattedStartDate = startDate.toISOString().slice(0, 16);
    const formattedEndDate = endDate.toISOString().slice(0, 16);
    
    document.getElementById('status-start-time').value = formattedStartDate;
    document.getElementById('status-end-time').value = formattedEndDate;
    
    // 初始化表单提交处理
    submitDeviceForm();
    
    // 初始化编辑表单提交处理
    submitEditDeviceForm();
    
    // 添加区域选择器和设备类型选择器的变化事件监听器，自动加载设备列表
    const deviceRegionSelect = document.getElementById('device-region-select');
    const deviceTypeSelect = document.getElementById('device-type-select');
    
    if (deviceRegionSelect) {
        deviceRegionSelect.addEventListener('change', function() {
            console.log('区域选择器变化，自动加载设备列表...');
            loadDevices();
        });
    }
    
    if (deviceTypeSelect) {
        deviceTypeSelect.addEventListener('change', function() {
            console.log('设备类型选择器变化，自动加载设备列表...');
            loadDevices();
        });
    }
});
