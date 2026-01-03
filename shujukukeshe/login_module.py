class LoginManager:
    """
    登录管理类，负责处理用户登录、角色权限管理等功能
    """
    def __init__(self, disaster_db):
        """
        初始化登录管理器
        :param disaster_db: 灾害预警数据库对象
        """
        self.disaster_db = disaster_db
    
    def user_login(self, username, password):
        """
        用户登录验证
        :param username: 用户名
        :param password: 密码
        :return: 登录成功返回用户信息，失败返回None
        """
        try:
            # 获取用户信息
            user = self.disaster_db.get_user_by_username(username)
            if not user:
                print("用户名不存在")
                return None
            
            # 检查用户状态
            if user['Status'] != '启用':
                print("账号已被禁用")
                return None
            
            # 验证密码
            if user['Password'] != password:
                print("密码错误")
                return None
            
            print(f"登录成功！欢迎 {user['Name']}（{user['Role']}）")
            return user
        except Exception as e:
            print(f"登录失败: {e}")
            return None
    
    def get_role_menu(self, role):
        """
        根据用户角色获取功能菜单
        :param role: 用户角色
        :return: 功能菜单列表
        """
        menus = {
            '系统管理员': [
                {'code': '1', 'name': '用户账号管理', 'desc': '维护所有角色的账号信息与权限分配'},
                {'code': '2', 'name': '预警规则管理', 'desc': '管理设备档案与预警规则'},
                {'code': '3', 'name': '报表模板审核', 'desc': '审核统计报表模板'},
                {'code': '4', 'name': '系统设置', 'desc': '系统参数配置与维护'}
            ],
            '数据管理员': [
                {'code': '1', 'name': '林草资源管理', 'desc': '录入、校验林草资源基础信息'},
                {'code': '2', 'name': '监测数据处理', 'desc': '处理监测数据的异常情况'},
                {'code': '3', 'name': '统计报表生成', 'desc': '生成并发布统计报表'},
                {'code': '4', 'name': '数据质量监控', 'desc': '监控数据质量与完整性'}
            ],
            '区域护林员': [
                {'code': '1', 'name': '监测数据查询', 'desc': '查看负责区域的实时监测数据与历史记录'},
                {'code': '2', 'name': '灾害预警处理', 'desc': '接收并处理相关灾害预警'},
                {'code': '3', 'name': '设备巡检记录', 'desc': '记录设备巡检与维护情况'},
                {'code': '4', 'name': '林草资源更新', 'desc': '更新区域内林草资源变动信息'}
            ],
            '公众用户': [
                {'code': '1', 'name': '林草资源查询', 'desc': '查看公开的林草资源统计数据'},
                {'code': '2', 'name': '环境监测浏览', 'desc': '浏览非涉密的环境监测信息'},
                {'code': '3', 'name': '异常情况反馈', 'desc': '提交林草资源异常情况反馈'},
                {'code': '4', 'name': '个人信息管理', 'desc': '管理个人账号信息'}
            ],
            '监管人员': [
                {'code': '1', 'name': '系统数据监控', 'desc': '查看全系统业务数据与操作记录'},
                {'code': '2', 'name': '预警流程监督', 'desc': '监督预警处理流程的及时性与规范性'},
                {'code': '3', 'name': '资源变动审核', 'desc': '审核资源变动与设备维护记录的真实性'},
                {'code': '4', 'name': '操作日志查询', 'desc': '查询系统操作日志'}
            ]
        }
        
        return menus.get(role, [])
    
    def has_permission(self, role, permission):
        """
        检查用户角色是否拥有指定权限
        :param role: 用户角色
        :param permission: 权限代码
        :return: 是否拥有权限
        """
        # 权限映射表
        permissions = {
            '系统管理员': ['user_manage', 'rule_manage', 'report_audit', 'system_setting'],
            '数据管理员': ['resource_manage', 'data_process', 'report_generate', 'data_monitor'],
            '区域护林员': ['monitor_query', 'warning_handle', 'device_record', 'resource_update'],
            '公众用户': ['resource_query', 'env_browse', 'feedback_submit', 'profile_manage'],
            '监管人员': ['system_monitor', 'process_supervise', 'record_audit', 'log_query']
        }
        
        return permission in permissions.get(role, [])

class LoginUI:
    """
    登录界面类，负责处理登录相关的用户界面
    """
    def __init__(self, login_manager):
        """
        初始化登录界面
        :param login_manager: 登录管理器对象
        """
        self.login_manager = login_manager
        self.current_user = None
    
    def display_login(self):
        """
        显示登录界面
        """
        print("\n" + "="*50)
        print("           智慧林草灾害预警系统")
        print("="*50)
        print("                用户登录")
        print("-"*50)
        
    def handle_login(self):
        """
        处理用户登录
        :return: 登录成功返回用户信息，失败返回None
        """
        self.display_login()
        
        while True:
            username = input("请输入用户名: ").strip()
            if not username:
                print("用户名不能为空！")
                continue
                
            # 在所有环境下使用普通input函数获取密码
            print("注意：当前环境下密码将明文显示")
            password = input("请输入密码: ").strip()
                
            if not password:
                print("密码不能为空！")
                continue
            
            user = self.login_manager.user_login(username, password)
            if user:
                self.current_user = user
                return user
            
            choice = input("是否重新登录？(y/n): ").strip().lower()
            if choice != 'y':
                return None
