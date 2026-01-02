// 环境监测页面专用JavaScript代码

// 加载区域列表
function loadRegions() {
    fetch('/api/resource_management/get_regions')
        .then(response => response.json())
        .then(data => {
            console.log('获取到的区域列表:', data);
            
            // 填充所有区域选择器
            const regionSelects = [
                {
                    id: 'env-region-select',
                    hasAllOption: true
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
    const regionId = document.getElementById('env-region-select').value;
    const startTime = document.getElementById('start-time').value;
    const endTime = document.getElementById('end-time').value;
    
    // 转换时间格式为YYYY-MM-DD HH:MM:SS
    const formattedStartTime = startTime.replace('T', ' ');
    const formattedEndTime = endTime.replace('T', ' ');
    
    const tableBody = document.getElementById('environment-data-table');
    tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    let url = `/api/environmental_monitoring/get_monitoring_data?region_id=${regionId}&start_time=${formattedStartTime}&end_time=${formattedEndTime}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log('获取到的环境监测数据:', data);
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #999;">未找到匹配的监测数据</td></tr>';
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
                        <td>${item.WindDirection || item.wind_direction || '--'}</td>
                        <td>${item.Rainfall || '--'}</td>
                        <td>${item.DataTime || item.data_time || '--'}</td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHtml;
        })
        .catch(error => {
            console.error('加载环境监测数据失败:', error);
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    // 初始加载区域列表
    loadRegions();
    
    // 设置默认时间范围为最近7天
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    // 格式化为YYYY-MM-DDTHH:MM格式
    const formattedStartDate = startDate.toISOString().slice(0, 16);
    const formattedEndDate = endDate.toISOString().slice(0, 16);
    
    document.getElementById('start-time').value = formattedStartDate;
    document.getElementById('end-time').value = formattedEndDate;
    
    // 初始加载传感器列表
    const sensorTableBody = document.getElementById('sensors-table');
    sensorTableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    fetch('/api/environmental_monitoring/get_sensors')
        .then(response => response.json())
        .then(sensors => {
            if (!Array.isArray(sensors) || sensors.length === 0) {
                sensorTableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">未找到传感器数据</td></tr>';
                return;
            }
            
            let tableHtml = '';
            sensors.forEach(sensor => {
                tableHtml += `
                    <tr>
                        <td>${sensor.SensorID || sensor.sensor_id || '--'}</td>
                        <td>${sensor.DeviceModel || sensor.device_model || '--'}</td>
                        <td>${sensor.MonitoringType || sensor.monitoring_type || '--'}</td>
                        <td>${sensor.InstallTime || sensor.install_time || '--'}</td>
                        <td>${sensor.CommunicationProtocol || sensor.communication_protocol || '--'}</td>
                        <td>${sensor.RegionID || sensor.region_id || '--'}</td>
                    </tr>
                `;
            });
            
            sensorTableBody.innerHTML = tableHtml;
        })
        .catch(error => {
            console.error('加载传感器列表失败:', error);
            sensorTableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
});
