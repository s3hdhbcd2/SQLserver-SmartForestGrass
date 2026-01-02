import requests

# 调试登录和会话管理问题
def debug_login():
    # 测试用户列表
    test_users = [
        {'username': 'admin', 'password': '123456'},
        {'username': 'data_admin', 'password': '123456'}
    ]
    
    for user in test_users:
        print(f"\n🔍 调试用户: {user['username']}")
        
        # 创建会话对象
        session = requests.Session()
        
        try:
            # 1. 测试登录
            login_data = {
                'username': user['username'],
                'password': user['password']
            }
            
            print(f"   发送登录请求: {login_data}")
            login_response = session.post('http://127.0.0.1:5000/login', data=login_data, allow_redirects=True)
            print(f"   登录响应状态码: {login_response.status_code}")
            print(f"   最终URL: {login_response.url}")
            
            # 2. 查看会话cookie
            cookies = session.cookies.get_dict()
            print(f"   会话Cookie: {cookies}")
            
            # 3. 尝试直接访问dashboard，查看是否真的登录成功
            dashboard_response = session.get('http://127.0.0.1:5000/dashboard', allow_redirects=True)
            print(f"   访问dashboard状态码: {dashboard_response.status_code}")
            print(f"   访问dashboard最终URL: {dashboard_response.url}")
            
            # 4. 测试获取菜单
            menu_response = session.get('http://127.0.0.1:5000/api/get_menu')
            print(f"   获取菜单状态码: {menu_response.status_code}")
            
            if menu_response.status_code == 200:
                menu_data = menu_response.json()
                print(f"   菜单数据: {menu_data}")
            else:
                print(f"   菜单响应内容: {menu_response.text}")
            
        except Exception as e:
            print(f"   调试过程中发生错误: {e}")
        finally:
            # 退出登录
            session.get('http://127.0.0.1:5000/logout')

if __name__ == '__main__':
    debug_login()