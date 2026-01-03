import requests
import time

# 验证系统是否能够正确运行
def verify_system():
    base_url = 'http://127.0.0.1:5000'
    
    print("=== 开始验证系统运行状态 ===")
    print(f"验证时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"系统URL: {base_url}")
    print("=" * 60)
    
    # 测试结果记录
    test_results = []
    
    # 1. 测试首页访问
    print("\n1. 测试首页访问...")
    try:
        response = requests.get(base_url)
        if response.status_code in [200, 302]:
            print(f"   ✅ 首页访问成功，状态码: {response.status_code}")
            test_results.append(('首页访问', '成功'))
        else:
            print(f"   ❌ 首页访问失败，状态码: {response.status_code}")
            test_results.append(('首页访问', '失败'))
    except Exception as e:
        print(f"   ❌ 首页访问异常: {e}")
        test_results.append(('首页访问', '异常'))
    
    # 2. 测试登录页面
    print("\n2. 测试登录页面...")
    try:
        response = requests.get(f"{base_url}/login")
        if response.status_code == 200:
            print(f"   ✅ 登录页面访问成功")
            test_results.append(('登录页面', '成功'))
        else:
            print(f"   ❌ 登录页面访问失败，状态码: {response.status_code}")
            test_results.append(('登录页面', '失败'))
    except Exception as e:
        print(f"   ❌ 登录页面访问异常: {e}")
        test_results.append(('登录页面', '异常'))
    
    # 3. 测试登录功能
    print("\n3. 测试登录功能...")
    session = requests.Session()
    login_data = {
        'username': 'admin',
        'password': '123456'
    }
    
    try:
        login_response = session.post(f"{base_url}/login", data=login_data, allow_redirects=True)
        if login_response.status_code == 200 and '/dashboard' in login_response.url:
            print(f"   ✅ 登录成功，重定向到仪表盘")
            test_results.append(('登录功能', '成功'))
            
            # 4. 测试获取菜单API
            print("\n4. 测试获取菜单API...")
            try:
                menu_response = session.get(f"{base_url}/api/get_menu")
                if menu_response.status_code == 200:
                    menu_data = menu_response.json()
                    print(f"   ✅ 获取菜单成功，共 {len(menu_data)} 个菜单")
                    menu_names = [menu['name'] for menu in menu_data]
                    print(f"   菜单列表: {', '.join(menu_names)}")
                    test_results.append(('获取菜单API', '成功'))
                else:
                    print(f"   ❌ 获取菜单失败，状态码: {menu_response.status_code}")
                    test_results.append(('获取菜单API', '失败'))
            except Exception as e:
                print(f"   ❌ 获取菜单异常: {e}")
                test_results.append(('获取菜单API', '异常'))
            
            # 5. 测试仪表盘访问
            print("\n5. 测试仪表盘访问...")
            try:
                dashboard_response = session.get(f"{base_url}/dashboard")
                if dashboard_response.status_code == 200:
                    print(f"   ✅ 仪表盘访问成功")
                    test_results.append(('仪表盘访问', '成功'))
                else:
                    print(f"   ❌ 仪表盘访问失败，状态码: {dashboard_response.status_code}")
                    test_results.append(('仪表盘访问', '失败'))
            except Exception as e:
                print(f"   ❌ 仪表盘访问异常: {e}")
                test_results.append(('仪表盘访问', '异常'))
            
            # 6. 测试环境监测页面
            print("\n6. 测试环境监测页面...")
            try:
                env_response = session.get(f"{base_url}/environmental_monitoring")
                if env_response.status_code == 200:
                    print(f"   ✅ 环境监测页面访问成功")
                    test_results.append(('环境监测页面', '成功'))
                else:
                    print(f"   ❌ 环境监测页面访问失败，状态码: {env_response.status_code}")
                    test_results.append(('环境监测页面', '失败'))
            except Exception as e:
                print(f"   ❌ 环境监测页面访问异常: {e}")
                test_results.append(('环境监测页面', '异常'))
            
            # 7. 测试环境监测API
            print("\n7. 测试环境监测API...")
            try:
                api_response = session.get(f"{base_url}/api/environmental_monitoring/get_sensors")
                if api_response.status_code == 200:
                    data = api_response.json()
                    print(f"   ✅ 环境监测API访问成功，返回 {len(data)} 条数据")
                    test_results.append(('环境监测API', '成功'))
                else:
                    print(f"   ❌ 环境监测API访问失败，状态码: {api_response.status_code}")
                    test_results.append(('环境监测API', '失败'))
            except Exception as e:
                print(f"   ❌ 环境监测API访问异常: {e}")
                test_results.append(('环境监测API', '异常'))
            
        else:
            print(f"   ❌ 登录失败，最终URL: {login_response.url}")
            test_results.append(('登录功能', '失败'))
    except Exception as e:
        print(f"   ❌ 登录异常: {e}")
        test_results.append(('登录功能', '异常'))
    
    # 8. 测试灾害预警页面
    print("\n8. 测试灾害预警页面...")
    try:
        warning_response = session.get(f"{base_url}/disaster_warning")
        if warning_response.status_code == 200:
            print(f"   ✅ 灾害预警页面访问成功")
            test_results.append(('灾害预警页面', '成功'))
        else:
            print(f"   ❌ 灾害预警页面访问失败，状态码: {warning_response.status_code}")
            test_results.append(('灾害预警页面', '失败'))
    except Exception as e:
        print(f"   ❌ 灾害预警页面访问异常: {e}")
        test_results.append(('灾害预警页面', '异常'))
    
    # 9. 测试资源管理页面
    print("\n9. 测试资源管理页面...")
    try:
        resource_response = session.get(f"{base_url}/resource_management")
        if resource_response.status_code == 200:
            print(f"   ✅ 资源管理页面访问成功")
            test_results.append(('资源管理页面', '成功'))
        else:
            print(f"   ❌ 资源管理页面访问失败，状态码: {resource_response.status_code}")
            test_results.append(('资源管理页面', '失败'))
    except Exception as e:
        print(f"   ❌ 资源管理页面访问异常: {e}")
        test_results.append(('资源管理页面', '异常'))
    
    # 10. 测试设备管理页面
    print("\n10. 测试设备管理页面...")
    try:
        device_response = session.get(f"{base_url}/equipment_management")
        if device_response.status_code == 200:
            print(f"   ✅ 设备管理页面访问成功")
            test_results.append(('设备管理页面', '成功'))
        else:
            print(f"   ❌ 设备管理页面访问失败，状态码: {device_response.status_code}")
            test_results.append(('设备管理页面', '失败'))
    except Exception as e:
        print(f"   ❌ 设备管理页面访问异常: {e}")
        test_results.append(('设备管理页面', '异常'))
    
    # 11. 测试统计分析页面
    print("\n11. 测试统计分析页面...")
    try:
        stats_response = session.get(f"{base_url}/statistical_analysis")
        if stats_response.status_code == 200:
            print(f"   ✅ 统计分析页面访问成功")
            test_results.append(('统计分析页面', '成功'))
        else:
            print(f"   ❌ 统计分析页面访问失败，状态码: {stats_response.status_code}")
            test_results.append(('统计分析页面', '失败'))
    except Exception as e:
        print(f"   ❌ 统计分析页面访问异常: {e}")
        test_results.append(('统计分析页面', '异常'))
    
    # 12. 测试用户管理页面（仅管理员可访问）
    print("\n12. 测试用户管理页面...")
    try:
        user_response = session.get(f"{base_url}/user_management")
        if user_response.status_code == 200:
            print(f"   ✅ 用户管理页面访问成功")
            test_results.append(('用户管理页面', '成功'))
        elif user_response.status_code == 302:
            print(f"   ⚠️  用户管理页面被重定向（权限控制生效）")
            test_results.append(('用户管理页面', '权限控制生效'))
        else:
            print(f"   ❌ 用户管理页面访问失败，状态码: {user_response.status_code}")
            test_results.append(('用户管理页面', '失败'))
    except Exception as e:
        print(f"   ❌ 用户管理页面访问异常: {e}")
        test_results.append(('用户管理页面', '异常'))
    
    # 13. 测试退出登录功能
    print("\n13. 测试退出登录功能...")
    try:
        logout_response = session.get(f"{base_url}/logout", allow_redirects=True)
        if logout_response.status_code == 200 and '/login' in logout_response.url:
            print(f"   ✅ 退出登录成功，重定向到登录页面")
            test_results.append(('退出登录', '成功'))
        else:
            print(f"   ❌ 退出登录失败，最终URL: {logout_response.url}")
            test_results.append(('退出登录', '失败'))
    except Exception as e:
        print(f"   ❌ 退出登录异常: {e}")
        test_results.append(('退出登录', '异常'))
    
    # 汇总测试结果
    print("\n" + "=" * 60)
    print("          系统验证结果汇总")
    print("=" * 60)
    
    success_count = sum(1 for _, result in test_results if result in ['成功', '权限控制生效'])
    total_count = len(test_results)
    
    print(f"\n测试项目总数: {total_count}")
    print(f"成功项目数: {success_count}")
    print(f"失败项目数: {total_count - success_count}")
    print(f"成功率: {round(success_count / total_count * 100, 2)}%")
    
    print("\n详细测试结果:")
    print("-" * 50)
    for i, (test_name, result) in enumerate(test_results, 1):
        status = "✅" if result in ['成功', '权限控制生效'] else "❌"
        print(f"{i:2d}. {test_name:<15} | {status} {result}")
    
    print("\n" + "=" * 60)
    
    if success_count == total_count:
        print("🎉 系统验证通过！所有功能均能正常运行。")
        return True
    else:
        print("⚠️  系统验证未完全通过，请检查失败项目。")
        return False

if __name__ == '__main__':
    verify_system()