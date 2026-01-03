// 统计分析页面专用JavaScript代码

// 加载公开林草资源统计数据
function loadPublicForestResources() {
    const tableBody = document.getElementById('forest-resources-table');
    tableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    // 获取林草资源数据
    fetch('/api/resource_management/get_resources')
        .then(response => response.json())
        .then(data => {
            console.log('获取到的林草资源数据:', data);
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #999;">未找到林草资源数据</td></tr>';
                return;
            }
            
            let tableHtml = '';
            data.forEach(resource => {
                tableHtml += `
                    <tr>
                        <td>${resource.RegionID || resource.region_id || '--'}</td>
                        <td>${resource.ResourceType || resource.resource_type || '--'}</td>
                        <td>${resource.CoverageArea || resource.coverage_area || '--'}</td>
                        <td>${resource.GrowthStatus || resource.growth_status || '--'}</td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHtml;
        })
        .catch(error => {
            console.error('加载林草资源数据失败:', error);
            tableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    // 初始加载林草资源数据
    loadPublicForestResources();
});
