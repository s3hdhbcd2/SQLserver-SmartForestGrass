// 设备管理页面专用JavaScript代码

// 获取当前用户信息（从全局变量或页面中解析）
function getCurrentUser() {
    if (window.currentUser) {
        return window.currentUser;
    }
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

// 保存设备数据，用于编辑时快速获取
let devicesData = [];

// 加载区域列表
function loadRegions() {
    // 获取当前用户信息
    const currentUser = getCurrentUser();
    
    // 监管人员不需要区域选择和设备列表，直接返回
    if (currentUser.Role === '监管人员') {
        return;
    }
    
    // 区域护林员不需要区域选择（用于查看设备列表），隐藏选择器
    const deviceRegionSelect = document.getElementById('device-region-select');
    if (deviceRegionSelect) {
        if (currentUser.Role === '区域护林员') {
            deviceRegionSelect.style.display = 'none';
            const label = deviceRegionSelect.previousElementSibling;
            if (label && label.textContent.includes('选择区域')) {
                label.style.display = 'none';
            }
        }
    }
    
    // 获取区域列表数据
    let regionsData = [];
    
    if (currentUser.Role === '区域护林员' && currentUser.ManagedRegions) {
        // 区域护林员只能看到自己管理的区域
        regionsData = currentUser.ManagedRegions;
        // 填充安装位置选择器
        fillRegionSelectors(regionsData, true);
    } else {
        // 非区域护林员从API获取所有区域
        fetch('/api/resource_management/get_regions')
            .then(response => response.json())
            .then(data => {
                console.log('获取到的区域列表:', data);
                fillRegionSelectors(data, false);
            })
            .catch(error => {
                console.error('加载区域列表失败:', error);
            });
    }
}

// 填充区域选择器
function fillRegionSelectors(data, isRegionalRanger) {
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
            // 对于区域护林员，只填充安装位置选择器，不填充设备区域选择器
            if (isRegionalRanger && selectConfig.id === 'device-region-select') {
                return;
            }
            
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
                    option.value = region.RegionID;
                    option.textContent = region.RegionName;
                    select.appendChild(option);
                });
            }
            
            // 恢复之前的选中值
            if (currentValue) {
                select.value = currentValue;
            }
        }
    });
}

// 加载设备档案列表
function loadDevices() {
    // 获取当前用户信息
    const currentUser = getCurrentUser();
    
    // 监管人员不需要设备列表，直接返回
    if (currentUser.Role === '监管人员') {
        return;
    }
    
    // 检查当前用户是否是区域护林员
    let regionId = '';
    
    // 区域选择器可能不存在，添加存在性检查
    const deviceRegionSelect = document.getElementById('device-region-select');
    if (currentUser.Role !== '区域护林员' && deviceRegionSelect) {
        // 非区域护林员，使用选择器的值
        regionId = deviceRegionSelect.value;
    }
    
    // 设备类型选择器可能不存在，添加存在性检查
    const deviceTypeSelect = document.getElementById('device-type-select');
    const deviceType = deviceTypeSelect ? deviceTypeSelect.value : '';
    
    let deviceStatus = '';
    // 只有非管理员和非系统管理员才获取设备状态选择器的值
    if (currentUser.Role !== '管理员' && currentUser.Role !== '系统管理员') {
        const deviceStatusSelect = document.getElementById('device-status-select');
        if (deviceStatusSelect) {
            deviceStatus = deviceStatusSelect.value;
        }
    }
    
    // 设备表格可能不存在，添加存在性检查
    const tableBody = document.getElementById('devices-table');
    if (!tableBody) {
        return;
    }
    
    tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    let url = '/api/equipment_management/get_devices';
    const params = [];
    
    if (regionId) {
        params.push(`region_id=${regionId}`);
    }
    if (deviceType) {
        params.push(`device_type=${deviceType}`);
    }
    if (deviceStatus) {
        params.push(`status=${deviceStatus}`);
    }
    
    if (params.length > 0) {
        url += `?${params.join('&')}`;
    }
    
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('获取到的设备档案:', data);
            
            // 保存设备数据，用于编辑时快速获取
            devicesData = data;
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #999;">未找到匹配的设备档案</td></tr>';
                return;
            }
            
            let tableHtml = '';
            let deviceSelectHtml = '<option value="">请选择设备</option>';
            
            data.forEach(device => {
                const deviceId = device.DeviceID || device.device_id;
                const deviceName = device.DeviceName || device.device_name || '未知设备';
                const deviceStatus = device.Status || device.status || '正常';
                
                // 检查当前用户角色
                const userRole = getCurrentUser().Role;
                const isAdmin = userRole === '管理员' || userRole === '系统管理员';
                
                // 填充设备档案表格
                tableHtml += `
                    <tr>
                        <td>${deviceId || '--'}</td>
                        <td>${deviceName}</td>
                        <td>${device.DeviceType || device.device_type || '--'}</td>
                        <td>${device.ModelSpecification || device.model_specification || '--'}</td>
                        <td>${device.PurchaseTime || device.purchase_time || '--'}</td>
                        <td>${device.RegionID || device.region_id || '--'}</td>`;
                
                // 非管理员显示设备状态列
                if (!isAdmin) {
                    tableHtml += `<td>${deviceStatus}</td>`;
                }
                
                tableHtml += `
                        <td>
                            `; 
                            
                // 只有管理员和系统管理员可以编辑设备
                if (isAdmin) {
                    tableHtml += `<button class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" onclick="editEquipment('${deviceId}')">编辑</button>`;
                }
                
                tableHtml += `<button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; ${isAdmin ? 'margin-left: 0.5rem;' : ''}" onclick="viewEquipmentDetail('${deviceId}')">详情</button>
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
            
            // 更新维护记录的设备选择器
            const maintenanceDeviceSelect = document.getElementById('maintenance-device-id-select');
            if (maintenanceDeviceSelect) {
                maintenanceDeviceSelect.innerHTML = deviceSelectHtml;
            }
            
            // 更新巡检记录的设备选择器
            const inspectionDeviceSelect = document.getElementById('inspection-device-id');
            if (inspectionDeviceSelect) {
                inspectionDeviceSelect.innerHTML = deviceSelectHtml;
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
    
    console.log('查询设备状态参数:');
    console.log('设备ID:', deviceId);
    console.log('开始时间:', formattedStartTime);
    console.log('结束时间:', formattedEndTime);
    
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
                console.log('单个状态数据:', status);
                tableHtml += `
                    <tr>
                        <td>${status.StatusID || status.status_id || '--'}</td>
                        <td>${status.DeviceID || status.device_id || '--'}</td>
                        <td>${status.RunningStatus || status.running_status || '--'}</td>
                        <td>${status.BatteryLevel || status.battery_level || '--'}</td>
                        <td>${status.SignalStrength || status.signal_strength || '--'}</td>
                        <td>${status.CollectionTime || status.collection_time || '--'}</td>
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

// 加载设备维护记录
function loadMaintenanceRecords() {
    const currentUser = getCurrentUser();
    const isSupervisor = currentUser.Role === '监管人员';
    
    // 监管人员不需要设备ID选择器，添加存在性检查
    let deviceId = '';
    const deviceSelect = document.getElementById('maintenance-device-id-select');
    if (deviceSelect) {
        deviceId = deviceSelect.value;
    }
    
    const tableBody = document.getElementById('maintenance-records-table');
    if (!tableBody) {
        console.error('维护记录表格不存在');
        return;
    }
    
    tableBody.innerHTML = '<tr><td colspan="11" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    // 监管人员不需要设备ID，可以加载所有记录
    let url = '/api/equipment_management/get_equipment_inspections';
    if (!isSupervisor && !deviceId) {
        tableBody.innerHTML = '<tr><td colspan="11" style="text-align: center; color: #999;">请选择设备ID</td></tr>';
        return;
    }
    
    // 非监管人员需要设备ID
    if (!isSupervisor) {
        url += `?device_id=${deviceId}`;
        console.log('查询设备维护记录参数:');
        console.log('设备ID:', deviceId);
    } else {
        console.log('监管人员查询所有设备维护记录');
    }
    
    fetch(url, {
        credentials: 'include' // 发送cookie，保持登录状态
    })
        .then(response => response.json())
        .then(data => {
            console.log('获取到的设备维护记录:', data);
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="11" style="text-align: center; color: #999;">未找到匹配的设备维护记录</td></tr>';
                return;
            }
            
            let tableHtml = '';
            // 获取当前用户角色，判断是否为监管人员
            const userRole = window.currentUser ? window.currentUser.Role : '';
            const isSupervisor = userRole === '监管人员';
            
            data.forEach(inspection => {
                console.log('单个维护记录:', inspection);
                const auditStatus = inspection.AuditStatus || inspection.audit_status || '待审核';
                const auditBtn = isSupervisor && auditStatus === '待审核' ? 
                    `<button class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-left: 0.5rem;" onclick="openMaintenanceAuditModal('${inspection.InspectionID || inspection.inspection_id}')">审核</button>` : '';
                
                tableHtml += `
                    <tr>
                        <td>${inspection.InspectionID || inspection.inspection_id || '--'}</td>
                        <td>${inspection.DeviceID || inspection.device_id || '--'}</td>
                        <td>${inspection.InspectionTime || inspection.inspection_time || '--'}</td>
                        <td>${inspection.InspectorID || inspection.inspector_id || '--'}</td>
                        <td>${inspection.MaintenanceType || inspection.maintenance_type || '--'}</td>
                        <td>${inspection.InspectionResult || inspection.inspection_result || '--'}</td>
                        <td>${inspection.ProblemDescription || inspection.problem_description || '--'}</td>
                        <td>${inspection.MaintenanceContent || inspection.maintenance_content || '--'}</td>
                        <td>${inspection.MaintenanceResult || inspection.maintenance_result || '--'}</td>
                        <td>${auditStatus}</td>
                        <td>
                            ${auditBtn}
                        </td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHtml;
        })
        .catch(error => {
            console.error('加载设备维护记录失败:', error);
            tableBody.innerHTML = '<tr><td colspan="11" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
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
    
    // 获取当前用户角色
    const userRole = getCurrentUser().Role;
    const isAdmin = userRole === '管理员' || userRole === '系统管理员';
    
    // 填充编辑模态框表单
    // 设备ID是必填字段，总是填充
    const equipmentIdInput = document.getElementById('edit-equipment_id');
    if (equipmentIdInput) {
        equipmentIdInput.value = device.DeviceID || device.device_id;
    }
    
    // 设备状态字段总是存在，总是填充
    const equipmentStatusSelect = document.getElementById('edit-equipment_status');
    if (equipmentStatusSelect) {
        equipmentStatusSelect.value = device.Status || device.status || '正常';
    }
    
    // 只有管理员可以编辑的字段
    if (isAdmin) {
        // 设备名称
        const equipmentNameInput = document.getElementById('edit-equipment_name');
        if (equipmentNameInput) {
            equipmentNameInput.value = device.DeviceName || device.device_name || '';
        }
        
        // 设备类型
        const equipmentTypeSelect = document.getElementById('edit-equipment_type');
        if (equipmentTypeSelect) {
            equipmentTypeSelect.value = device.DeviceType || device.device_type || '传感器';
        }
        
        // 型号规格
        const modelSpecInput = document.getElementById('edit-model_specification');
        if (modelSpecInput) {
            modelSpecInput.value = device.ModelSpecification || device.model_specification || '';
        }
        
        // 安装位置
        const locationSelect = document.getElementById('edit-installation_location');
        if (locationSelect) {
            // 确保设备的RegionID存在
            const regionId = device.RegionID || device.region_id;
            if (regionId) {
                // 检查该RegionID是否在下拉菜单的选项中
                let regionExists = false;
                for (let i = 0; i < locationSelect.options.length; i++) {
                    if (locationSelect.options[i].value === regionId) {
                        regionExists = true;
                        break;
                    }
                }
                if (regionExists) {
                    locationSelect.value = regionId;
                } else {
                    console.warn(`区域ID ${regionId} 不在下拉菜单选项中`);
                    // 保持当前选中值或默认值
                }
            } else {
                locationSelect.value = ''; // 没有RegionID，设置为空
            }
        }
        
        // 质保期
        const warrantyInput = document.getElementById('edit-warranty_period');
        if (warrantyInput) {
            warrantyInput.value = device.WarrantyPeriod || device.warranty_period || '';
        }
        
        // 格式化购买时间，确保格式正确
        const purchaseTime = device.PurchaseTime || device.purchase_time;
        let formattedPurchaseDate = '';
        if (purchaseTime) {
            try {
                // 处理不同格式的购买时间
                if (typeof purchaseTime === 'string') {
                    // 如果是字符串，尝试解析
                    if (purchaseTime.includes(' ')) {
                        // 格式：YYYY-MM-DD HH:MM:SS
                        formattedPurchaseDate = purchaseTime.split(' ')[0];
                    } else if (purchaseTime.includes('/')) {
                        // 格式：YYYY/MM/DD
                        formattedPurchaseDate = purchaseTime.replace(/\//g, '-');
                    } else {
                        // 格式：YYYY-MM-DD
                        formattedPurchaseDate = purchaseTime;
                    }
                } else {
                    // 如果是Date对象
                    formattedPurchaseDate = purchaseTime.toISOString().split('T')[0];
                }
            } catch (error) {
                console.error('解析购买时间失败:', error);
                formattedPurchaseDate = '';
            }
        }
        
        const purchaseDateInput = document.getElementById('edit-purchase_date');
        if (purchaseDateInput) {
            purchaseDateInput.value = formattedPurchaseDate;
        }
    }
    
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
            
            console.log('提交的设备数据:', deviceData);
            
            // 调用API保存设备信息
            fetch('/api/equipment_management/add_device', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(deviceData),
                credentials: 'same-origin' // 确保携带会话信息
            })
            .then(response => {
                console.log('响应状态:', response.status);
                console.log('响应URL:', response.url);
                if (!response.ok) {
                    // 非200响应，尝试读取响应内容
                    return response.text().then(text => {
                        throw new Error(`HTTP ${response.status}: ${text}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('设备保存结果:', data);
                if (data.success) {
                    alert('设备信息保存成功！');
                    this.reset();
                    // 刷新设备列表
                    loadDevices();
                } else {
                    alert('设备信息保存失败：' + data.error);
                }
            })
            .catch(error => {
                console.error('设备保存失败:', error);
                alert('设备信息保存失败：' + error.message);
            });
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
            
            console.log('提交的编辑设备数据:', deviceData);
            
            // 调用API更新设备信息
            fetch('/api/equipment_management/update_device', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(deviceData),
                credentials: 'same-origin' // 确保携带会话信息
            })
            .then(response => {
                if (!response.ok) {
                    // 非200响应，尝试读取响应内容
                    return response.text().then(text => {
                        throw new Error(`HTTP ${response.status}: ${text}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('设备更新结果:', data);
                if (data.success) {
                    alert('设备信息更新成功！');
                    // 关闭模态框
                    closeEditModal();
                    // 刷新设备列表
                    loadDevices();
                } else {
                    alert('设备信息更新失败：' + data.error);
                }
            })
            .catch(error => {
                console.error('设备更新失败:', error);
                alert('设备信息更新失败：' + error.message);
            });
        });
    }
}

// 提交设备巡检记录表单
function submitInspectionForm() {
    const inspectionForm = document.getElementById('add-inspection-form');
    if (inspectionForm) {
        inspectionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const inspectionData = Object.fromEntries(formData);
            
            console.log('提交的设备巡检记录:', inspectionData);
            
            // 调用API添加设备巡检记录
            fetch('/api/equipment_management/add_equipment_inspection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(inspectionData),
                credentials: 'same-origin' // 确保携带会话信息
            })
            .then(response => {
                if (!response.ok) {
                    // 非200响应，尝试读取响应内容
                    return response.text().then(text => {
                        throw new Error(`HTTP ${response.status}: ${text}`);
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log('设备巡检记录保存结果:', data);
                if (data.success) {
                    alert('设备巡检记录保存成功！');
                    this.reset();
                    // 刷新设备列表和维护记录
                    loadDevices();
                } else {
                    alert('设备巡检记录保存失败：' + data.error);
                }
            })
            .catch(error => {
                console.error('设备巡检记录保存失败:', error);
                alert('设备巡检记录保存失败：' + error.message);
            });
        });
    }
}

// 打开设备维护审核模态框
function openMaintenanceAuditModal(inspectionId) {
    console.log('打开设备维护审核模态框，巡检ID:', inspectionId);
    document.getElementById('audit-inspection-id').value = inspectionId;
    document.getElementById('maintenance-audit-modal').style.display = 'block';
}

// 关闭设备维护审核模态框
function closeMaintenanceAuditModal() {
    document.getElementById('maintenance-audit-modal').style.display = 'none';
    document.getElementById('maintenance-audit-form').reset();
}

// 处理设备维护审核表单提交
function submitMaintenanceAuditForm() {
    const form = document.getElementById('maintenance-audit-form');
    if (!form) return;
    
    // 移除之前的事件监听器，防止重复绑定
    const newForm = form.cloneNode(true);
    form.parentNode.replaceChild(newForm, form);
    
    newForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const auditData = Object.fromEntries(formData);
        
        console.log('提交的设备维护审核数据:', auditData);
        
        // 提交到服务器
        fetch('/api/equipment_management/audit_equipment_inspection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include', // 发送cookie，保持登录状态
            body: JSON.stringify(auditData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('服务器返回:', data);
            
            if (data.success) {
                alert('审核提交成功！');
                // 关闭模态框
                closeMaintenanceAuditModal();
                
                // 重新加载设备维护记录
                loadMaintenanceRecords();
            } else {
                alert('审核提交失败！' + (data.error || ''));
            }
        })
        .catch(error => {
            console.error('提交审核数据失败:', error);
            alert('提交审核数据失败！' + error.message);
        });
    });
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
    
    // 格式化为YYYY-MM-DDTHH:MM格式（使用本地时间）
    function formatLocalDateTime(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        return `${year}-${month}-${day}T${hours}:${minutes}`;
    }
    
    const formattedStartDate = formatLocalDateTime(startDate);
    const formattedEndDate = formatLocalDateTime(endDate);
    
    console.log('默认时间范围:');
    console.log('开始时间:', formattedStartDate);
    console.log('结束时间:', formattedEndDate);
    
    // 检查元素是否存在，避免因设备状态查询部分被隐藏而导致错误
    const statusStartTimeEl = document.getElementById('status-start-time');
    const statusEndTimeEl = document.getElementById('status-end-time');
    if (statusStartTimeEl && statusEndTimeEl) {
        statusStartTimeEl.value = formattedStartDate;
        statusEndTimeEl.value = formattedEndDate;
    }
    
    // 初始化表单提交处理
    submitDeviceForm();
    
    // 初始化编辑表单提交处理
    submitEditDeviceForm();
    
    // 初始化设备巡检记录表单提交处理
    submitInspectionForm();
    
    // 初始化设备维护审核表单提交处理
    submitMaintenanceAuditForm();
    
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
    
    // 只有非管理员和非系统管理员才为设备状态选择器添加事件监听器
    const currentUser = getCurrentUser();
    if (currentUser.Role !== '管理员' && currentUser.Role !== '系统管理员') {
        const deviceStatusSelect = document.getElementById('device-status-select');
        if (deviceStatusSelect) {
            deviceStatusSelect.addEventListener('change', function() {
                console.log('设备状态选择器变化，自动加载设备列表...');
                loadDevices();
            });
        }
    }
    
    // 点击模态框外部关闭模态框
    window.onclick = function(event) {
        const editModal = document.getElementById('equipment-edit-modal');
        const detailModal = document.getElementById('equipment-detail-modal');
        const auditModal = document.getElementById('maintenance-audit-modal');
        
        if (event.target === editModal) {
            editModal.style.display = 'none';
        }
        
        if (event.target === detailModal) {
            detailModal.style.display = 'none';
        }
        
        if (event.target === auditModal) {
            auditModal.style.display = 'none';
        }
    };
});
