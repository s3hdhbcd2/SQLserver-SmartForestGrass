// 统计分析页面专用JavaScript代码

// 加载报表模板
function loadReportTemplates() {
    const reportType = document.getElementById('template-type-select').value;
    const tableBody = document.getElementById('report-templates-table');
    tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    let url = '/api/statistical_analysis/get_report_templates';
    if (reportType) {
        url += `?report_type=${reportType}`;
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log('获取到的报表模板:', data);
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #999;">未找到匹配的报表模板</td></tr>';
                return;
            }
            
            let tableHtml = '';
            data.forEach(template => {
                tableHtml += `
                    <tr>
                        <td>${template.TemplateID || template.template_id || '--'}</td>
                        <td>${template.TemplateName || template.template_name || '--'}</td>
                        <td>${template.ReportType || template.report_type || '--'}</td>
                        <td>${template.Description || template.description || '--'}</td>
                        <td>${template.CreatedBy || template.created_by || '--'}</td>
                        <td>${template.CreateTime || template.create_time || '--'}</td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHtml;
        })
        .catch(error => {
            console.error('加载报表模板失败:', error);
            tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
}

// 加载已生成报表
function loadGeneratedReports() {
    const regionId = document.getElementById('report-region-select').value;
    const reportType = document.getElementById('report-type-select').value;
    const startTime = document.getElementById('report-start-time').value;
    const endTime = document.getElementById('report-end-time').value;
    const tableBody = document.getElementById('generated-reports-table');
    tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    // 转换时间格式为YYYY-MM-DD HH:MM:SS
    const formattedStartTime = startTime.replace('T', ' ');
    const formattedEndTime = endTime.replace('T', ' ');
    
    let url = `/api/statistical_analysis/get_generated_reports?start_time=${formattedStartTime}&end_time=${formattedEndTime}`;
    
    if (regionId) {
        url += `&region_id=${regionId}`;
    }
    if (reportType) {
        url += `&report_type=${reportType}`;
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log('获取到的已生成报表:', data);
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #999;">未找到匹配的已生成报表</td></tr>';
                return;
            }
            
            let tableHtml = '';
            data.forEach(report => {
                tableHtml += `
                    <tr>
                        <td>${report.ReportID || report.report_id || '--'}</td>
                        <td>${report.ReportName || report.report_name || '--'}</td>
                        <td>${report.RegionID || report.region_id || '--'}</td>
                        <td>${report.GeneratedTime || report.generated_time || '--'}</td>
                        <td>${report.GeneratedBy || report.generated_by || '--'}</td>
                        <td>${report.ReportStatus || report.report_status || '--'}</td>
                        <td>
                            <button class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">查看</button>
                            <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-left: 0.5rem;">下载</button>
                        </td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHtml;
        })
        .catch(error => {
            console.error('加载已生成报表失败:', error);
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
}

// 生成报表
function generateReport() {
    document.getElementById('generate-report-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const reportData = Object.fromEntries(formData);
        
        // 转换时间格式为YYYY-MM-DD HH:MM:SS
        reportData.start_time = reportData.start_time.replace('T', ' ');
        reportData.end_time = reportData.end_time.replace('T', ' ');
        
        // 这里可以添加提交到服务器的逻辑
        console.log('提交的报表生成数据:', reportData);
        
        // 模拟生成成功
        alert('报表生成成功！');
        this.reset();
        // 刷新已生成报表列表
        loadGeneratedReports();
    });
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    // 初始加载报表模板
    loadReportTemplates();
    
    // 设置默认时间范围为最近30天
    const endDate = new Date();
    const startDate = new Date(endDate.getTime() - 30 * 24 * 60 * 60 * 1000);
    
    // 格式化为YYYY-MM-DDTHH:MM格式
    const formattedStartDate = startDate.toISOString().slice(0, 16);
    const formattedEndDate = endDate.toISOString().slice(0, 16);
    
    document.getElementById('report-start-time').value = formattedStartDate;
    document.getElementById('report-end-time').value = formattedEndDate;
    document.getElementById('start_time').value = formattedStartDate;
    document.getElementById('end_time').value = formattedEndDate;
    
    // 初始化表单提交处理
    generateReport();
});
