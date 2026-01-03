// 用户管理页面专用JavaScript代码

// 获取当前URL路径，用于高亮当前菜单项
const currentPath = window.location.pathname;

// 保存用户数据，用于编辑时快速获取
let usersData = [];

// 加载用户列表
function loadUsers() {
    // 获取角色过滤参数
    const role = document.getElementById('role-filter').value;
    const tableBody = document.querySelector('#users-table tbody');
    tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #999;">数据加载中...</td></tr>';
    
    let url = '/api/user_management/get_users';
    if (role) {
        url += `?role=${role}`;
    }
    
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('获取用户列表失败');
            }
            return response.json();
        })
        .then(data => {
            // 保存用户数据到全局变量
            usersData = data;
            
            if (!Array.isArray(data) || data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #999;">未找到匹配的用户信息</td></tr>';
                return;
            }
            
            let tableHtml = '';
            data.forEach(user => {
                tableHtml += `
                    <tr>
                        <td>${user.UserID || '--'}</td>
                        <td>${user.Username || '--'}</td>
                        <td>${user.Name || '--'}</td>
                        <td>${user.Role || '--'}</td>
                        <td>${user.Contact || '--'}</td>
                        <td>${user.Status || '--'}</td>
                        <td>---</td>
                        <td>
                            <button class="btn btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;" onclick="editUser('${user.UserID}')">编辑</button>
                            <button class="btn btn-danger" style="padding: 0.25rem 0.5rem; font-size: 0.8rem; margin-left: 0.5rem;" onclick="deleteUser('${user.UserID}')">删除</button>
                        </td>
                    </tr>
                `;
            });
            
            tableBody.innerHTML = tableHtml;
        })
        .catch(error => {
            console.error('加载用户列表失败:', error);
            tableBody.innerHTML = '<tr><td colspan="8" style="text-align: center; color: #e74c3c;">数据加载失败，请刷新页面重试</td></tr>';
        });
}

// 编辑用户
function editUser(userId) {
    // 根据用户ID查找用户数据
    const user = usersData.find(u => u.UserID === userId);
    if (!user) {
        console.error('未找到用户数据:', userId);
        alert('未找到用户数据！');
        return;
    }
    
    console.log('编辑用户:', userId, user);
    
    // 填充编辑模态框表单
    document.getElementById('edit-user-id').value = user.UserID;
    document.getElementById('edit-username').value = user.Username || '';
    document.getElementById('edit-name').value = user.Name || '';
    document.getElementById('edit-role').value = user.Role || '管理员';
    document.getElementById('edit-contact').value = user.Contact || '';
    document.getElementById('edit-status').value = user.Status || '启用';
    
    // 显示编辑模态框
    const modal = document.getElementById('user-edit-modal');
    modal.style.display = 'block';
}

// 关闭编辑模态框
function closeEditModal() {
    const modal = document.getElementById('user-edit-modal');
    modal.style.display = 'none';
}

// 删除用户
function deleteUser(userId) {
    if (confirm('确定要删除这个用户吗？')) {
        // 发送删除用户请求
        fetch('/api/user_management/delete_user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ user_id: userId }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('删除用户失败');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                alert('用户删除成功！');
                // 刷新用户列表
                loadUsers();
            } else {
                alert(`删除用户失败: ${data.error || '未知错误'}`);
            }
        })
        .catch(error => {
            console.error('删除用户失败:', error);
            alert('删除用户失败，请重试！');
        });
    }
}

// 提交编辑用户表单
function submitEditUserForm() {
    const editForm = document.getElementById('edit-user-form');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const userData = Object.fromEntries(formData);
            
            console.log('提交的编辑用户数据:', userData);
            
            // 检查必填字段
            if (!userData.user_id || !userData.username || !userData.name || !userData.contact) {
                alert('请填写所有必填字段！');
                return;
            }
            
            // 发送编辑用户请求
            fetch('/api/user_management/edit_user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('编辑用户失败');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert('用户编辑成功！');
                    // 关闭模态框
                    closeEditModal();
                    // 刷新用户列表
                    loadUsers();
                } else {
                    alert(`编辑用户失败: ${data.error || '未知错误'}`);
                }
            })
            .catch(error => {
                console.error('编辑用户失败:', error);
                alert('编辑用户失败，请重试！');
            });
        });
    }
}

// 从API获取菜单数据
fetch('/api/get_menu')
    .then(response => response.json())
    .then(menus => {
        const menuContainer = document.getElementById('menu');
        menus.forEach(menu => {
            const menuItem = document.createElement('a');
            menuItem.className = `menu-item ${menu.href === currentPath ? 'active' : ''}`;
            menuItem.href = menu.href;
            menuItem.innerHTML = `<span class="icon">${menu.icon}</span>${menu.name}`;
            menuContainer.appendChild(menuItem);
        });
    });

// 添加用户表单提交处理
function addUser() {
    const addForm = document.querySelector('.card form');
    if (addForm) {
        addForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const userData = Object.fromEntries(formData);
            
            console.log('提交的添加用户数据:', userData);
            
            // 检查必填字段
            if (!userData.username || !userData.password || !userData.name || !userData.contact_info) {
                alert('请填写所有必填字段！');
                return;
            }
            
            // 发送添加用户请求
            fetch('/api/user_management/add_user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData),
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('添加用户失败');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert('用户添加成功！');
                    // 重置表单
                    addForm.reset();
                    // 刷新用户列表
                    loadUsers();
                } else {
                    alert(`添加用户失败: ${data.error || '未知错误'}`);
                }
            })
            .catch(error => {
                console.error('添加用户失败:', error);
                alert('添加用户失败，请重试！');
            });
        });
    }
}

// 页面加载完成后初始化
window.addEventListener('DOMContentLoaded', function() {
    // 初始加载用户列表
    loadUsers();
    
    // 初始化编辑表单提交处理
    submitEditUserForm();
    
    // 初始化添加用户表单提交处理
    addUser();
    
    // 添加角色过滤选择器变化事件监听器
    const roleFilter = document.getElementById('role-filter');
    if (roleFilter) {
        roleFilter.addEventListener('change', function() {
            console.log('角色过滤条件变化，重新加载用户列表...');
            loadUsers();
        });
    }
});

// 点击模态框外部关闭模态框
window.onclick = function(event) {
    const editModal = document.getElementById('user-edit-modal');
    if (event.target === editModal) {
        editModal.style.display = 'none';
    }
};