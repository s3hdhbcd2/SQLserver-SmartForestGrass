// 通用JavaScript代码，适用于所有页面

// 确认退出登录函数
function confirmLogout() {
    if (confirm('确定要退出登录吗？')) {
        window.location.href = '/logout';
    }
}

// 从API获取菜单数据
function loadMenu() {
    console.log('开始加载菜单...');
    fetch('/api/get_menu')
        .then(response => {
            console.log('菜单API响应:', response);
            return response.json();
        })
        .then(menus => {
            console.log('获取到的菜单数据:', menus);
            const menuContainer = document.getElementById('menu');
            menuContainer.innerHTML = ''; // 清空现有菜单
            
            if (!Array.isArray(menus)) {
                console.error('菜单数据不是数组:', menus);
                menuContainer.innerHTML = '<div style="padding: 1rem; color: #e74c3c;">菜单数据格式错误</div>';
                return;
            }
            
            menus.forEach(menu => {
                console.log('处理菜单:', menu);
                const menuItem = document.createElement('a');
                menuItem.className = `menu-item ${menu.href === window.location.pathname ? 'active' : ''}`;
                menuItem.href = menu.href;
                menuItem.innerHTML = `<span class="icon">${menu.icon}</span>${menu.name}`;
                
                // 移除不必要的点击事件处理，让浏览器默认处理链接跳转
                // 这样可以避免JavaScript导致的请求中止问题
                
                menuContainer.appendChild(menuItem);
            });
        })
        .catch(error => {
            console.error('加载菜单失败:', error);
            const menuContainer = document.getElementById('menu');
            menuContainer.innerHTML = `<div style="padding: 1rem; color: #e74c3c;">菜单加载失败: ${error.message}</div>`;
        });
}

// 页面加载完成后加载菜单
document.addEventListener('DOMContentLoaded', function() {
    // 只有包含菜单的页面才加载菜单
    if (document.getElementById('menu')) {
        loadMenu();
    }
});

// 通用的数据加载函数
function loadData(url, tableBodyId, templateFunction, loadingMessage = '数据加载中...', emptyMessage = '未找到匹配的数据') {
    const tableBody = document.getElementById(tableBodyId);
    tableBody.innerHTML = `<tr><td colspan="100%" style="text-align: center; color: #999;">${loadingMessage}</td></tr>`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = `<tr><td colspan="100%" style="text-align: center; color: #999;">${emptyMessage}</td></tr>`;
                return;
            }
            
            let tableHtml = '';
            data.forEach(item => {
                tableHtml += templateFunction(item);
            });
            
            tableBody.innerHTML = tableHtml;
            
            // 数据加载完成后检查并隐藏空列
            hideEmptyColumns(tableBody.closest('.table'));
        })
        .catch(error => {
            console.error('加载数据失败:', error);
            tableBody.innerHTML = `<tr><td colspan="100%" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>`;
        });
}

// 检查并隐藏表格中的空列
function hideEmptyColumns(table) {
    if (!table) return;
    
    const tbody = table.querySelector('tbody');
    const thead = table.querySelector('thead');
    if (!tbody || !thead) return;
    
    const rows = tbody.querySelectorAll('tr');
    const headerCells = thead.querySelectorAll('th');
    const numColumns = headerCells.length;
    
    // 如果没有数据行，直接返回
    if (rows.length === 0) return;
    
    // 检查每一列是否为空
    for (let colIndex = 0; colIndex < numColumns; colIndex++) {
        let isColumnEmpty = true;
        
        // 检查该列的所有数据单元格
        rows.forEach(row => {
            const cell = row.cells[colIndex];
            if (cell) {
                const cellText = cell.textContent.trim();
                // 如果单元格内容不是空值标记，则该列不为空
                if (cellText !== '--' && cellText !== '未知' && cellText !== '') {
                    isColumnEmpty = false;
                }
            }
        });
        
        // 如果列为空，则隐藏该列的表头和所有数据单元格
        if (isColumnEmpty) {
            // 隐藏表头
            headerCells[colIndex].style.display = 'none';
            
            // 隐藏所有数据行的对应单元格
            rows.forEach(row => {
                const cell = row.cells[colIndex];
                if (cell) {
                    cell.style.display = 'none';
                }
            });
        } else {
            // 如果列不为空，确保显示该列
            headerCells[colIndex].style.display = '';
            
            // 确保所有数据行的对应单元格显示
            rows.forEach(row => {
                const cell = row.cells[colIndex];
                if (cell) {
                    cell.style.display = '';
                }
            });
        }
    }
}

// 通用的表单提交处理函数
function handleFormSubmit(formId, submitUrl, successMessage = '操作成功！') {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const data = Object.fromEntries(formData);
        
        fetch(submitUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                alert(successMessage);
                form.reset();
                // 如果页面有数据列表，可以在这里刷新数据
            } else {
                alert('操作失败: ' + (result.message || '未知错误'));
            }
        })
        .catch(error => {
            console.error('提交表单失败:', error);
            alert('操作失败: 网络错误');
        });
    });
}
