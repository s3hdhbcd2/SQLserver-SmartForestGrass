// 系统首页页面专用JavaScript代码

// 获取当前URL路径，用于高亮当前菜单项
const currentPath = window.location.pathname;

// 从API获取菜单数据
fetch('/api/get_menu')
    .then(response => {
        console.log('菜单API响应状态:', response.status);
        if (!response.ok) {
            throw new Error('获取菜单失败，状态码: ' + response.status);
        }
        return response.json();
    })
    .then(menus => {
        console.log('获取到的菜单数据:', menus);
        const menuContainer = document.getElementById('menu');
        
        if (!Array.isArray(menus) || menus.length === 0) {
            menuContainer.innerHTML = '<div style="padding: 1rem; color: #999;">当前角色没有可访问的菜单</div>';
            return;
        }
        
        // 遍历菜单数据，生成菜单HTML
        menus.forEach(menu => {
            const menuItem = document.createElement('a');
            menuItem.className = `menu-item ${menu.href === currentPath ? 'active' : ''}`;
            menuItem.href = menu.href;
            menuItem.innerHTML = `<span class="icon">${menu.icon}</span>${menu.name}`;
            menuContainer.appendChild(menuItem);
        });
    })
    .catch(error => {
        console.error('获取菜单失败:', error);
        const menuContainer = document.getElementById('menu');
        menuContainer.innerHTML = `<div style="padding: 1rem; color: #e74c3c;">菜单加载失败：${error.message}，请刷新页面重试</div>`;
    });