// 通用JavaScript代码，适用于所有页面

// 从API获取菜单数据
function loadMenu() {
    fetch('/api/get_menu')
        .then(response => response.json())
        .then(menus => {
            const menuContainer = document.getElementById('menu');
            menuContainer.innerHTML = ''; // 清空现有菜单
            
            menus.forEach(menu => {
                const menuItem = document.createElement('a');
                menuItem.className = `menu-item ${menu.href === window.location.pathname ? 'active' : ''}`;
                menuItem.href = menu.href;
                menuItem.innerHTML = `<span class="icon">${menu.icon}</span>${menu.name}`;
                menuContainer.appendChild(menuItem);
            });
        })
        .catch(error => {
            console.error('加载菜单失败:', error);
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
        })
        .catch(error => {
            console.error('加载数据失败:', error);
            tableBody.innerHTML = `<tr><td colspan="100%" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>`;
        });
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
