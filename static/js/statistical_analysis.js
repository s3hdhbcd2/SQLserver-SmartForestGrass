// 统计分析页面专用JavaScript代码

// 加载公开林草资源统计数据
function loadPublicForestResources() {
    const tableBody = document.getElementById('forest-resources-table');
    // 如果表格不存在，直接返回，避免报错
    if (!tableBody) {
        return;
    }
    
    tableBody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    // 获取林草资源数据
    fetch('/api/resource_management/get_public_resources')
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

// 加载报表模板
function loadReportTemplates() {
    // 禁用缓存，确保获取最新数据
    const url = '/api/statistical_analysis/get_report_templates?' + new Date().getTime();
    
    fetch(url, {
        method: 'GET',
        cache: 'no-cache',
        headers: {
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP错误! 状态: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('获取到的报表模板数据:', data);
        
        const templateSelect = document.getElementById('template-select');
        if (templateSelect) {
            // 清空选择框
            templateSelect.innerHTML = '<option value="">请选择报表模板</option>';
            
            if (Array.isArray(data) && data.length > 0) {
                data.forEach(template => {
                    // 兼容不同的字段命名格式
                    const templateId = template.TemplateID || template.template_id;
                    const reportName = template.ReportName || template.template_name;
                    const auditStatus = template.AuditStatus || '未知状态';
                    
                    console.log(`处理模板: ${templateId} - ${reportName} - ${auditStatus}`);
                    
                    if (templateId && reportName) {
                        templateSelect.innerHTML += `<option value="${templateId}">${reportName}</option>`;
                    }
                });
            } else {
                console.log('没有获取到报表模板数据');
                templateSelect.innerHTML += '<option value="">无可用报表模板</option>';
            }
            
            // 添加调试信息
            console.log(`模板选择框已更新，共有 ${templateSelect.options.length - 1} 个可用模板`);
        } else {
            console.error('未找到模板选择框元素');
        }
    })
    .catch(error => {
        console.error('加载报表模板失败:', error);
        
        // 显示错误信息给用户
        const templateSelect = document.getElementById('template-select');
        if (templateSelect) {
            templateSelect.innerHTML = '<option value="">加载模板失败，请刷新页面重试</option>';
        }
    });
}

// 加载区域列表
function loadRegions() {
    // 禁用缓存，确保获取最新数据
    const url = '/api/resource_management/get_regions?' + new Date().getTime();
    
    fetch(url, {
        method: 'GET',
        cache: 'no-cache',
        headers: {
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP错误! 状态: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('获取到的区域数据:', data);
        
        const regionSelect = document.getElementById('region-select');
        if (regionSelect) {
            // 清空选择框
            regionSelect.innerHTML = '<option value="">请选择区域</option>';
            
            if (Array.isArray(data) && data.length > 0) {
                // 检查数据格式
                console.log('区域数据长度:', data.length);
                
                data.forEach(region => {
                    // 兼容不同的字段命名格式
                    const regionId = region.RegionID || region.region_id;
                    const regionName = region.RegionName || region.region_name || `未知区域${regionId}`;
                    
                    console.log(`处理区域: ${regionId} - ${regionName}`);
                    
                    if (regionId && regionName) {
                        regionSelect.innerHTML += `<option value="${regionId}">${regionName}</option>`;
                    } else {
                        console.warn('无效的区域数据:', region);
                    }
                });
            } else {
                console.log('没有获取到区域数据或数据格式不正确');
                regionSelect.innerHTML += '<option value="">无可用区域</option>';
            }
            
            // 添加调试信息
            console.log(`区域选择框已更新，共有 ${regionSelect.options.length - 1} 个可用区域`);
        } else {
            console.error('未找到区域选择框元素');
        }
    })
    .catch(error => {
        console.error('加载区域列表失败:', error);
        
        // 显示错误信息给用户
        const regionSelect = document.getElementById('region-select');
        if (regionSelect) {
            regionSelect.innerHTML = '<option value="">加载区域失败，请刷新页面重试</option>';
        }
    });
}

// 加载已生成报表
function loadGeneratedReports() {
    const tableBody = document.getElementById('generated-reports-table');
    if (!tableBody) return;
    
    // 根据用户角色设置正确的colspan
    const userRole = document.getElementById('user-role').value;
    const isAdmin = userRole === '系统管理员' || userRole === '数据管理员';
    const colspan = isAdmin ? 8 : 2;
    
    tableBody.innerHTML = `<tr><td colspan="${colspan}" style="text-align: center; color: #999;">数据加载中...</td></tr>`;
    
    fetch('/api/statistical_analysis/get_generated_reports')
        .then(response => response.json())
        .then(data => {
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="${colspan}" style="text-align: center; color: #999;">未找到已生成报表</td></tr>`;
                return;
            }
            
            let tableHtml = '';
            data.forEach(report => {
                    // 构建表格行
                    let tableRow = '<tr>';
                    
                    // 获取用户角色
                    const userRole = document.getElementById('user-role').value;
                    
                    // 系统管理员和非管理员只显示名称，数据管理员显示完整信息
                    if (userRole === '数据管理员') {
                        // 格式化发布状态
                        const publishStatus = report.IsPublished ? '<span style="color: green;">已发布</span>' : '<span style="color: orange;">未发布</span>';
                        
                        tableRow += `
                            <td>${report.report_id}</td>
                            <td>${report.report_name}</td>
                            <td>${report.template_name}</td>
                            <td>${report.RegionID}</td>
                            <td>${new Date(report.generated_time).toLocaleString()}</td>
                            <td>${publishStatus}</td>
                        `;
                        
                        // 只有数据管理员才显示操作列
                        // 格式化操作按钮
                        const actions = report.IsPublished ? 
                            '<button class="btn btn-sm btn-secondary" disabled>已发布</button>' : 
                            `<button class="btn btn-sm btn-primary" onclick="publishReport('${report.report_id}')">发布</button>`;
                        tableRow += `<td>${actions}</td>`;
                    } else {
                        // 系统管理员和非管理员只显示名称
                        tableRow += `
                            <td>${report.report_name}</td>
                        `;
                    }
                    
                    // 所有用户都显示详情按钮
                    tableRow += `<td><button class="btn btn-sm btn-info view-report-detail-btn" data-report-id="${report.report_id}" data-report-name="${report.report_name}">查看详情</button></td>`;
                    
                    tableRow += '</tr>';
                    tableHtml += tableRow;
                });
            
            tableBody.innerHTML = tableHtml;
            
            // 添加详情按钮事件监听器
            const detailButtons = document.querySelectorAll('.view-report-detail-btn');
            detailButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const reportId = this.dataset.reportId;
                    const reportName = this.dataset.reportName;
                    viewReportDetail(reportId, reportName);
                });
            });
        })
        .catch(error => {
            console.error('加载已生成报表失败:', error);
            // 使用之前定义的colspan变量，确保错误信息也能正确显示
            tableBody.innerHTML = `<tr><td colspan="${colspan}" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>`;
        });
}

// 发布报表
function publishReport(reportId) {
    if (!confirm('确定要发布该报表吗？')) return;
    
    fetch('/api/statistical_analysis/publish_report', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ report_id: reportId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('报表发布成功！');
            loadGeneratedReports();
        } else {
            alert('报表发布失败：' + (data.error || '未知错误'));
        }
    })
    .catch(error => {
        console.error('发布报表失败:', error);
        alert('报表发布失败：' + error.message);
    });
}

// 处理报表生成表单提交
function handleReportGenerationForm() {
    const form = document.getElementById('report-generation-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const templateId = document.getElementById('template-select').value;
        const regionId = document.getElementById('region-select').value;
        const startTime = document.getElementById('start-time').value;
        const endTime = document.getElementById('end-time').value;
        
        // 将datetime-local转换为标准格式
        const formattedStartTime = new Date(startTime).toISOString().slice(0, 19).replace('T', ' ');
        const formattedEndTime = new Date(endTime).toISOString().slice(0, 19).replace('T', ' ');
        
        fetch('/api/statistical_analysis/generate_report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                template_id: templateId,
                region_id: regionId,
                start_time: formattedStartTime,
                end_time: formattedEndTime
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('报表生成成功！');
                loadGeneratedReports();
                // 清空表单
                form.reset();
            } else {
                alert('报表生成失败：' + (data.error || '未知错误'));
            }
        })
        .catch(error => {
            console.error('生成报表失败:', error);
            alert('报表生成失败：' + error.message);
        });
    });
}

// 加载报表模板列表（系统管理员）
function loadReportTemplatesForAudit() {
    const tableBody = document.getElementById('report-templates-table');
    if (!tableBody) {
        console.log('report-templates-table元素不存在');
        return;
    }
    
    console.log('开始加载报表模板审核列表');
    tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    fetch('/api/statistical_analysis/get_report_templates')
        .then(response => {
            console.log('API响应状态:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('获取到的报表模板数据:', data);
            if (Array.isArray(data) && data.length > 0) {
                let tableHtml = '';
                data.forEach(template => {
                    const templateId = template.TemplateID || template.template_id;
                    const reportName = template.ReportName || template.template_name;
                    const reportType = template.ReportType;
                    const auditStatus = template.AuditStatus || '待审核';
                    
                    // 添加状态颜色区分
                    let statusStyle = '';
                    if (auditStatus === '待审核') {
                        statusStyle = 'style="color: #fa8c16; font-weight: 500;"';
                    } else if (auditStatus === '已通过' || auditStatus === '通过') {
                        statusStyle = 'style="color: #52c41a; font-weight: 500;"';
                    }
                    
                    tableHtml += `
                        <tr>
                            <td>${templateId}</td>
                            <td>${reportName}</td>
                            <td>${reportType}</td>
                            <td ${statusStyle}>${auditStatus}</td>
                            <td>
                                <button class="btn btn-primary btn-sm" onclick="openTemplateAuditModal('${templateId}', '${reportName}')">审核</button>
                            </td>
                        </tr>
                    `;
                });
                tableBody.innerHTML = tableHtml;
            } else {
                console.log('没有找到报表模板数据');
                tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #999;">未找到报表模板数据</td></tr>';
            }
        })
        .catch(error => {
            console.error('加载报表模板列表失败:', error);
            tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
}

// 打开报表模板审核模态框
let currentAuditTemplate = null;
function openTemplateAuditModal(templateId, reportName) {
    currentAuditTemplate = { templateId, reportName };
    
    const modal = document.getElementById('template-audit-modal');
    const templateIdInput = document.getElementById('audit-template-id');
    const templateNameInput = document.getElementById('audit-template-name');
    
    if (modal && templateIdInput && templateNameInput) {
        templateIdInput.value = templateId;
        templateNameInput.value = reportName;
        modal.style.display = 'block';
    }
}

// 关闭报表模板审核模态框
function closeTemplateAuditModal() {
    const modal = document.getElementById('template-audit-modal');
    if (modal) {
        modal.style.display = 'none';
        currentAuditTemplate = null;
        document.getElementById('template-audit-form').reset();
    }
}

// 查看报表详情
function viewReportDetail(reportId, reportName) {
    const modal = document.getElementById('report-detail-modal');
    const detailContent = document.getElementById('report-detail-content');
    
    if (modal && detailContent) {
        // 显示加载状态
        detailContent.innerHTML = '<p>正在加载报表详情...</p>';
        modal.style.display = 'block';
        
        // 获取所有报表数据，找到对应的报表
        fetch('/api/statistical_analysis/get_generated_reports')
            .then(response => response.json())
            .then(reports => {
                const report = reports.find(r => r.report_id === reportId);
                if (report) {
                    // 格式化报表内容
                    let contentHtml = `<h4>${report.report_name}</h4>`;
                    
                    try {
                        // 尝试解析JSON格式的报表内容
                        const reportData = JSON.parse(report.report_content);
                        
                        // 添加报表基本信息
                        contentHtml += `
                            <div class="report-info" style="margin-bottom: 1.5rem;">
                                <h5>报表信息</h5>
                                <p><strong>类型:</strong> ${reportData.type}</p>
                                <p><strong>区域ID:</strong> ${reportData.region_id}</p>
                                <p><strong>时间范围:</strong> ${reportData.time_range}</p>
                                <p><strong>数据总量:</strong> ${reportData.total_data} 条</p>
                                <p><strong>说明:</strong> ${reportData.message}</p>
                            </div>
                        `;
                        
                        // 添加图表容器
                        contentHtml += `
                            <div class="chart-container" style="position: relative; height: 400px; margin-bottom: 1.5rem;">
                                <canvas id="report-chart-${reportId}"></canvas>
                            </div>
                        `;
                        
                        // 添加原始数据表格
                        contentHtml += `
                            <div class="raw-data" style="margin-top: 1.5rem;">
                                <h5>原始数据</h5>
                                <div style="max-height: 300px; overflow-y: auto;">
                                    <table class="table table-sm">
                                        <thead>
                                            <tr>
                                                <th>时间</th>
                                                <th>温度</th>
                                                <th>湿度</th>
                                                <th>风速</th>
                                                <th>降雨量</th>
                                            </tr>
                                        </thead>
                                        <tbody id="raw-data-table-${reportId}">
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        `;
                        
                        detailContent.innerHTML = contentHtml;
                        
                        // 渲染图表
                        renderChart(reportId, reportData.chart_data);
                        
                        // 渲染原始数据表格
                        renderRawData(reportId, reportData.raw_data);
                        
                    } catch (e) {
                        // 如果不是JSON格式，显示原始文本
                        contentHtml += `
                            <div style="background-color: #f5f5f5; padding: 1rem; border-radius: 5px; white-space: pre-wrap; font-family: monospace;">
                                ${report.report_content || '该报表暂无详细内容'}
                            </div>
                        `;
                        detailContent.innerHTML = contentHtml;
                    }
                } else {
                    detailContent.innerHTML = '<p style="color: red;">未找到该报表</p>';
                }
            })
            .catch(error => {
                console.error('获取报表详情失败:', error);
                detailContent.innerHTML = '<p style="color: red;">加载报表详情失败</p>';
            });
    }
}

// 渲染图表
function renderChart(reportId, chartData) {
    const canvas = document.getElementById(`report-chart-${reportId}`);
    if (!canvas) return;
    
    // 销毁已有图表
    const existingChart = Chart.getChart(canvas);
    if (existingChart) {
        existingChart.destroy();
    }
    
    // 创建新图表
    new Chart(canvas, {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: '环境监测数据趋势'
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '数值'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '时间'
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

// 渲染原始数据表格
function renderRawData(reportId, rawData) {
    const tbody = document.getElementById(`raw-data-table-${reportId}`);
    if (!tbody) return;
    
    if (!rawData || rawData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #999;">无原始数据</td></tr>';
        return;
    }
    
    let tableHtml = '';
    rawData.forEach(data => {
        // 处理不同格式的数据
        if (Array.isArray(data)) {
            // 数组格式（数据库查询结果）
            tableHtml += `
                <tr>
                    <td>${data[3] ? new Date(data[3]).toLocaleString() : '-'}</td>
                    <td>${data[4] || '-'}</td>
                    <td>${data[5] || '-'}</td>
                    <td>${data[6] || '-'}</td>
                    <td>${data[7] || '-'}</td>
                </tr>
            `;
        } else {
            // 对象格式
            tableHtml += `
                <tr>
                    <td>${data.DataTime ? new Date(data.DataTime).toLocaleString() : '-'}</td>
                    <td>${data.Temperature || '-'}</td>
                    <td>${data.Humidity || '-'}</td>
                    <td>${data.WindSpeed || '-'}</td>
                    <td>${data.Rainfall || '-'}</td>
                </tr>
            `;
        }
    });
    
    tbody.innerHTML = tableHtml;
}

// 关闭报表详情模态框
function closeReportDetailModal() {
    const modal = document.getElementById('report-detail-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// 处理报表模板审核表单提交
function handleTemplateAuditForm() {
    const form = document.getElementById('template-audit-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const templateId = document.getElementById('audit-template-id').value;
        const auditStatus = document.getElementById('audit-status').value;
        const auditComments = document.getElementById('audit-comments').value;
        
        fetch('/api/statistical_analysis/audit_report_template', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                template_id: templateId,
                audit_status: auditStatus,
                audit_comments: auditComments
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('报表模板审核成功！');
                closeTemplateAuditModal();
                loadReportTemplatesForAudit();
            } else {
                alert('报表模板审核失败：' + (data.error || '未知错误'));
            }
        })
        .catch(error => {
            console.error('审核报表模板失败:', error);
            alert('审核报表模板失败：' + error.message);
        });
    });
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    // 获取用户角色
    const userRole = document.getElementById('user-role').value;
    
    // 初始加载林草资源数据 - 数据管理员、系统管理员、区域护林员和监管人员不需要
    if (!['数据管理员', '系统管理员', '区域护林员', '监管人员'].includes(userRole)) {
        loadPublicForestResources();
    }
    
    // 所有用户都加载已发布报表
    if (document.getElementById('generated-reports-table')) {
        loadGeneratedReports();
    }
    
    // 如果是数据管理员，加载报表生成相关数据
    if (document.getElementById('report-generation-form')) {
        loadReportTemplates();
        loadRegions();
        handleReportGenerationForm();
    }
    
    // 如果是系统管理员，加载报表模板审核相关数据
    if (document.getElementById('report-templates-table')) {
        loadReportTemplatesForAudit();
        handleTemplateAuditForm();
    }
});
