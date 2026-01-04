import pyodbc
from login_module import LoginManager

class DatabaseConnection:
    def __init__(self, db_config=None):
        """
        初始化数据库连接
        :param db_config: 数据库连接配置
        """
        self.db_config = db_config or {}
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """
        连接SQL Server数据库
        :return: 是否连接成功
        """
        try:
            # SQL Server连接
            server = self.db_config.get('server', '.\\SQLEXPRESS')
            database = self.db_config.get('database', 'SmartForestGrass')
            username = self.db_config.get('username', '')
            password = self.db_config.get('password', '')
            
            if username and password:
                # 用户名密码认证
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
            else:
                # Windows认证
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes"
            
            self.connection = pyodbc.connect(conn_str)
            self.cursor = self.connection.cursor()
            
            print("成功连接到SQL Server数据库")
            return True
        except Exception as e:
            print(f"连接数据库失败: {e}")
            return False
    
    def disconnect(self):
        """
        断开数据库连接
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("已断开与SQL Server数据库的连接")
    
    def get_new_connection(self):
        """
        创建并返回一个新的数据库连接对象
        :return: 新的DatabaseConnection对象
        """
        new_conn = DatabaseConnection(self.db_config)
        new_conn.connect()
        return new_conn
    
    def execute(self, sql, params=None):
        """
        执行单条SQL语句
        :param sql: SQL语句
        :param params: 参数
        :return: 是否执行成功
        """
        try:
            # 使用新的游标执行查询，避免共享游标导致的问题
            cursor = self.connection.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"执行SQL语句失败: {e}")
            self.connection.rollback()
            return False
    
    def execute_script(self, sql):
        """
        执行SQL脚本
        :param sql: SQL脚本
        :return: 是否执行成功
        """
        try:
            # SQL Server执行方式，处理GO关键字
            # 先按GO关键字分割脚本
            batches = []
            current_batch = []
            
            for line in sql.splitlines():
                line = line.rstrip('\r\n')
                # 检查是否是GO关键字行（忽略大小写）
                if line.strip().upper() == 'GO':
                    if current_batch:
                        batches.append('\n'.join(current_batch))
                        current_batch = []
                else:
                    current_batch.append(line)
            
            # 添加最后一个批次（如果有）
            if current_batch:
                batches.append('\n'.join(current_batch))
            
            # 执行每个批次
            for batch in batches:
                batch = batch.strip()
                if batch:
                    # 使用新的游标执行每个批次，避免共享游标导致的问题
                    cursor = self.connection.cursor()
                    # 按分号分割批次内的语句
                    statements = batch.split(';')
                    for statement in statements:
                        statement = statement.strip()
                        if statement:
                            cursor.execute(statement)
                    cursor.close()
            
            self.connection.commit()
            return True
        except Exception as e:
            print(f"执行SQL脚本失败: {e}")
            self.connection.rollback()
            return False
    
    def fetch_one(self, sql, params=None):
        """
        获取单条查询结果
        :param sql: SQL查询语句
        :param params: 参数
        :return: 查询结果
        """
        try:
            # 使用新的游标执行查询，避免共享游标导致的问题
            cursor = self.connection.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            result = cursor.fetchone()
            cursor.close()
            return result
        except Exception as e:
            print(f"查询失败: {e}")
            return None
    
    def fetch_all(self, sql, params=None):
        """
        获取所有查询结果
        :param sql: SQL查询语句
        :param params: 参数
        :return: 查询结果列表
        """
        try:
            # 使用新的游标执行查询，避免共享游标导致的问题
            cursor = self.connection.cursor()
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            print(f"查询失败: {e}")
            return []

class DisasterWarningTerminal:
    def __init__(self, db_config=None):
        """
        初始化灾害预警终端
        :param db_config: 数据库配置
        """
        self.db_config = db_config
        self.db_conn = None
        self.db_instance = None
        self.login_manager = None
        self.current_user = None
    
    def run(self):
        """
        运行灾害预警终端
        """
        # 1. 连接数据库
        from login_module import LoginUI
        self.db_conn = DatabaseConnection(self.db_config)
        if not self.db_conn.connect():
            print("无法连接到数据库，程序退出")
            return
        
        # 2. 创建数据库实例
        self.db_instance = DisasterWarningDatabase(self.db_conn)
        
        # 3. 初始化登录管理器和登录界面
        self.login_manager = LoginManager(self.db_instance)
        self.login_ui = LoginUI(self.login_manager)
        
        # 4. 登录认证
        self.current_user = self.login_ui.handle_login()
        if not self.current_user:
            print("登录失败，程序退出")
            self.db_conn.disconnect()
            return
        
        print(f"欢迎，{self.current_user['Name']} ({self.current_user['Role']})")
        
        # 5. 主菜单循环
        while True:
            print("\n=== 智慧林草灾害预警系统 ===")
            
            # 根据用户角色显示不同的菜单
            if self.current_user['Role'] == '监管人员':
                # 监管人员菜单
                print("1. 系统数据监控")
                print("2. 预警流程监督")
                print("3. 资源变动记录列表")
                print("4. 资源变动记录审核")
                print("5. 设备维护记录列表")
                print("6. 设备维护记录审核")
                print("7. 操作日志查询")
                print("0. 退出系统")
            else:
                # 其他角色菜单
                print("1. 环境监测")
                print("2. 灾害预警")
                print("3. 资源管理")
                print("4. 设备管理")
                print("5. 统计分析")
                print("0. 退出系统")
            
            choice = input("请输入您的选择: ")
            
            if choice == '0':
                print("感谢使用智慧林草灾害预警系统，再见！")
                break
            
            # 处理监管人员菜单
            elif self.current_user['Role'] == '监管人员':
                if choice == '1':
                    # 系统数据监控
                    print("\n=== 系统数据监控 ===")
                    print("1. 区域监测数据统计")
                    print("2. 林草资源分布统计")
                    print("3. 设备运行状态统计")
                    monitor_choice = input("请输入您的选择: ")
                    
                    if monitor_choice == '1':
                        # 区域监测数据统计
                        region_id = input("请输入区域ID: ")
                        start_time = input("请输入开始时间 (YYYY-MM-DD HH:MM:SS): ")
                        end_time = input("请输入结束时间 (YYYY-MM-DD HH:MM:SS): ")
                        try:
                            data = self.db_instance.complex_queries(5, start_time=start_time, end_time=end_time)
                            if data:
                                for item in data[:10]:  # 只显示前10条
                                    print(f"类型: {item['MonitoringType']}, 区域: {item['region_name']}, 设备: {item['DeviceName']}, 数据量: {item['DataCount']}, 平均温度: {item['AvgTemperature']:.2f}, 平均湿度: {item['AvgHumidity']:.2f}")
                                if len(data) > 10:
                                    print(f"... 共 {len(data)} 条数据，仅显示前10条")
                            else:
                                print("暂无监测数据统计")
                        except Exception as e:
                            print(f"❌ 获取监测数据统计失败: {e}")
                    elif monitor_choice == '2':
                        # 林草资源分布统计
                        try:
                            resources = self.db_instance.get_forest_resources()
                            if resources:
                                for resource in resources:
                                    print(f"资源ID: {resource['ResourceID']}, 区域ID: {resource['region_id']}, 类型: {resource['ResourceType']}, 面积: {resource['CoverageArea']}, 树种: {resource['TreeSpecies']}, 生长状态: {resource['GrowthStatus']}")
                            else:
                                print("暂无林草资源数据")
                        except Exception as e:
                            print(f"❌ 获取林草资源数据失败: {e}")
                    elif monitor_choice == '3':
                        # 设备运行状态统计
                        try:
                            devices = self.db_instance.get_device_archives()
                            if devices:
                                for device in devices:
                                    print(f"设备ID: {device['DeviceID']}, 名称: {device['DeviceName']}, 类型: {device['DeviceType']}, 区域ID: {device['region_id']}, 状态: {device['Status']}")
                            else:
                                print("暂无设备档案数据")
                        except Exception as e:
                            print(f"❌ 获取设备档案数据失败: {e}")
                    else:
                        print("无效的选择")
                elif choice == '2':
                    # 预警流程监督
                    print("\n=== 预警流程监督 ===")
                    print("1. 火灾预警处理情况")
                    print("2. 区域预警统计")
                    warning_choice = input("请输入您的选择: ")
                    
                    if warning_choice == '1':
                        # 火灾预警处理情况
                        start_time = input("请输入开始时间 (YYYY-MM-DD HH:MM:SS): ")
                        end_time = input("请输入结束时间 (YYYY-MM-DD HH:MM:SS): ")
                        try:
                            warnings = self.db_instance.complex_queries(1, start_time=start_time, end_time=end_time)
                            if warnings:
                                for warning in warnings:
                                    print(f"预警ID: {warning['WarningID']}, 时间: {warning['TriggerTime']}, 类型: {warning['WarningType']}, 级别: {warning['WarningLevel']}, 内容: {warning['WarningContent']}, 状态: {warning['Status']}, 处理结果: {warning['HandleResult']}")
                            else:
                                print("暂无火灾预警记录")
                        except Exception as e:
                            print(f"❌ 获取火灾预警记录失败: {e}")
                    elif warning_choice == '2':
                        # 区域预警统计
                        region_id = input("请输入区域ID: ")
                        try:
                            warnings = self.db_instance.get_warnings_by_area(region_id)
                            if warnings:
                                for warning in warnings[:10]:  # 只显示前10条
                                    print(f"预警ID: {warning['WarningID']}, 时间: {warning['TriggerTime']}, 内容: {warning['WarningContent']}, 状态: {warning['Status']}")
                                if len(warnings) > 10:
                                    print(f"... 共 {len(warnings)} 条预警记录，仅显示前10条")
                            else:
                                print("暂无预警记录")
                        except Exception as e:
                            print(f"❌ 获取区域预警记录失败: {e}")
                    else:
                        print("无效的选择")
                elif choice == '3':
                    # 资源变动记录列表
                    print("\n=== 资源变动记录列表 ===")
                    print("1. 查看所有资源变动记录")
                    print("2. 查看待审核的资源变动记录")
                    print("3. 查看已通过的资源变动记录")
                    print("4. 查看已拒绝的资源变动记录")
                    change_choice = input("请输入您的选择: ")
                    
                    if change_choice == '1':
                        # 查看所有资源变动记录
                        resource_id = input("请输入资源ID (可选): ")
                        try:
                            records = self.db_instance.get_resource_change_records(resource_id if resource_id else None)
                            if records:
                                for record in records[:10]:  # 只显示前10条
                                    print(f"变动ID: {record['ChangeID']}, 资源ID: {record['ResourceID']}, 类型: {record['ChangeType']}, 原因: {record['ChangeReason']}, 时间: {record['ChangeTime']}, 操作人: {record['OperatorID']}, 审核状态: {record['AuditStatus']}")
                                    if record['AuditStatus'] in ['通过', '拒绝']:
                                        print(f"   审核人: {record['AuditorID']}, 审核时间: {record['AuditTime']}")
                                        if record['AuditComments']:
                                            print(f"   审核意见: {record['AuditComments']}")
                                if len(records) > 10:
                                    print(f"... 共 {len(records)} 条资源变动记录，仅显示前10条")
                            else:
                                print("暂无资源变动记录")
                        except Exception as e:
                            print(f"❌ 获取资源变动记录失败: {e}")
                    elif change_choice in ['2', '3', '4']:
                        # 查看特定状态的资源变动记录
                        status_map = {'2': '待审核', '3': '通过', '4': '拒绝'}
                        audit_status = status_map[change_choice]
                        resource_id = input("请输入资源ID (可选): ")
                        try:
                            records = self.db_instance.get_resource_change_records(resource_id if resource_id else None, audit_status)
                            if records:
                                for record in records[:10]:  # 只显示前10条
                                    print(f"变动ID: {record['ChangeID']}, 资源ID: {record['ResourceID']}, 类型: {record['ChangeType']}, 原因: {record['ChangeReason']}, 时间: {record['ChangeTime']}, 操作人: {record['OperatorID']}, 审核状态: {record['AuditStatus']}")
                                if len(records) > 10:
                                    print(f"... 共 {len(records)} 条资源变动记录，仅显示前10条")
                            else:
                                print(f"暂无{audit_status}的资源变动记录")
                        except Exception as e:
                            print(f"❌ 获取资源变动记录失败: {e}")
                    else:
                        print("无效的选择")
                elif choice == '4':
                    # 资源变动记录审核
                    print("\n=== 资源变动记录审核 ===")
                    change_id = input("请输入要审核的资源变动记录ID: ")
                    try:
                        # 先获取该记录的详细信息
                        records = self.db_instance.get_resource_change_records(change_id)
                        if not records:
                            print(f"未找到ID为{change_id}的资源变动记录")
                        else:
                            record = records[0]
                            print(f"\n=== 资源变动记录详情 ===")
                            print(f"变动ID: {record['ChangeID']}")
                            print(f"资源ID: {record['ResourceID']}")
                            print(f"变动类型: {record['ChangeType']}")
                            print(f"变动原因: {record['ChangeReason']}")
                            print(f"变动时间: {record['ChangeTime']}")
                            print(f"操作人: {record['OperatorID']}")
                            print(f"当前审核状态: {record['AuditStatus']}")
                            
                            if record['AuditStatus'] != '待审核':
                                print("该记录已审核，无需重复审核")
                            else:
                                # 进行审核操作
                                print(f"\n=== 审核操作 ===")
                                print("请选择审核结果:")
                                print("1. 通过")
                                print("2. 拒绝")
                                audit_choice = input("请输入您的选择: ")
                                
                                if audit_choice in ['1', '2']:
                                    audit_status = '通过' if audit_choice == '1' else '拒绝'
                                    audit_comments = input("请输入审核意见 (可选): ")
                                    
                                    # 执行审核
                                    result = self.db_instance.audit_resource_change(
                                        change_id, audit_status, self.current_user['UserID'], audit_comments
                                    )
                                    
                                    if result:
                                        print(f"✅ 资源变动记录审核成功，状态已更新为{audit_status}")
                                    else:
                                        print("❌ 资源变动记录审核失败")
                                else:
                                    print("无效的审核结果")
                    except Exception as e:
                        print(f"❌ 审核资源变动记录失败: {e}")
                elif choice == '5':
                    # 设备维护记录列表
                    print("\n=== 设备维护记录列表 ===")
                    print("1. 查看所有设备维护记录")
                    print("2. 查看待审核的设备维护记录")
                    print("3. 查看已通过的设备维护记录")
                    print("4. 查看已拒绝的设备维护记录")
                    inspection_choice = input("请输入您的选择: ")
                    
                    if inspection_choice == '1':
                        # 查看所有设备维护记录
                        device_id = input("请输入设备ID (可选): ")
                        try:
                            inspections = self.db_instance.get_equipment_inspections(device_id if device_id else None)
                            if inspections:
                                for inspection in inspections[:10]:  # 只显示前10条
                                    print(f"巡检ID: {inspection['InspectionID']}, 设备ID: {inspection['DeviceID']}, 时间: {inspection['InspectionTime']}, 巡检人员: {inspection['InspectorID']}, 维护类型: {inspection['MaintenanceType']}, 结果: {inspection['InspectionResult']}, 审核状态: {inspection['AuditStatus']}")
                                    if inspection['ProblemDescription']:
                                        print(f"   问题描述: {inspection['ProblemDescription']}")
                                    if inspection['MaintenanceContent']:
                                        print(f"   维护内容: {inspection['MaintenanceContent']}")
                                    if inspection['AuditStatus'] in ['通过', '拒绝']:
                                        print(f"   审核人: {inspection['AuditorID']}, 审核时间: {inspection['AuditTime']}")
                                        if inspection['AuditComments']:
                                            print(f"   审核意见: {inspection['AuditComments']}")
                                if len(inspections) > 10:
                                    print(f"... 共 {len(inspections)} 条设备维护记录，仅显示前10条")
                            else:
                                print("暂无设备维护记录")
                        except Exception as e:
                            print(f"❌ 获取设备维护记录失败: {e}")
                    elif inspection_choice in ['2', '3', '4']:
                        # 查看特定状态的设备维护记录
                        status_map = {'2': '待审核', '3': '通过', '4': '拒绝'}
                        audit_status = status_map[inspection_choice]
                        device_id = input("请输入设备ID (可选): ")
                        try:
                            inspections = self.db_instance.get_equipment_inspections(device_id if device_id else None, audit_status)
                            if inspections:
                                for inspection in inspections[:10]:  # 只显示前10条
                                    print(f"巡检ID: {inspection['InspectionID']}, 设备ID: {inspection['DeviceID']}, 时间: {inspection['InspectionTime']}, 巡检人员: {inspection['InspectorID']}, 维护类型: {inspection['MaintenanceType']}, 结果: {inspection['InspectionResult']}, 审核状态: {inspection['AuditStatus']}")
                                    if inspection['ProblemDescription']:
                                        print(f"   问题描述: {inspection['ProblemDescription']}")
                                    if inspection['MaintenanceContent']:
                                        print(f"   维护内容: {inspection['MaintenanceContent']}")
                                if len(inspections) > 10:
                                    print(f"... 共 {len(inspections)} 条设备维护记录，仅显示前10条")
                            else:
                                print(f"暂无{audit_status}的设备维护记录")
                        except Exception as e:
                            print(f"❌ 获取设备维护记录失败: {e}")
                elif choice == '6':
                    # 设备维护记录审核
                    print("\n=== 设备维护记录审核 ===")
                    inspection_id = input("请输入要审核的设备维护记录ID: ")
                    try:
                        # 先获取该记录的详细信息
                        inspections = self.db_instance.get_equipment_inspections(inspection_id)
                        if not inspections:
                            print(f"未找到ID为{inspection_id}的设备维护记录")
                        else:
                            inspection = inspections[0]
                            print(f"\n=== 设备维护记录详情 ===")
                            print(f"巡检ID: {inspection['InspectionID']}")
                            print(f"设备ID: {inspection['DeviceID']}")
                            print(f"巡检时间: {inspection['InspectionTime']}")
                            print(f"巡检人员: {inspection['InspectorID']}")
                            print(f"维护类型: {inspection['MaintenanceType']}")
                            print(f"巡检结果: {inspection['InspectionResult']}")
                            if inspection['ProblemDescription']:
                                print(f"问题描述: {inspection['ProblemDescription']}")
                            if inspection['MaintenanceContent']:
                                print(f"维护内容: {inspection['MaintenanceContent']}")
                            if inspection['MaintenanceResult']:
                                print(f"维护结果: {inspection['MaintenanceResult']}")
                            print(f"当前审核状态: {inspection['AuditStatus']}")
                            
                            if inspection['AuditStatus'] != '待审核':
                                print("该记录已审核，无需重复审核")
                            else:
                                # 进行审核操作
                                print(f"\n=== 审核操作 ===")
                                print("请选择审核结果:")
                                print("1. 通过")
                                print("2. 拒绝")
                                audit_choice = input("请输入您的选择: ")
                                
                                if audit_choice in ['1', '2']:
                                    audit_status = '通过' if audit_choice == '1' else '拒绝'
                                    audit_comments = input("请输入审核意见 (可选): ")
                                    
                                    # 执行审核
                                    result = self.db_instance.audit_equipment_inspection(
                                        inspection_id, audit_status, self.current_user['UserID'], audit_comments
                                    )
                                    
                                    if result:
                                        print(f"✅ 设备维护记录审核成功，状态已更新为{audit_status}")
                                    else:
                                        print("❌ 设备维护记录审核失败")
                                else:
                                    print("无效的审核结果")
                    except Exception as e:
                        print(f"❌ 审核设备维护记录失败: {e}")
                elif choice == '7':
                    # 操作日志查询
                    print("\n=== 操作日志查询 ===")
                    print("提示: 当前系统暂未实现操作日志功能")
                    # 这里可以添加操作日志查询逻辑
                else:
                    print("无效的选择")
            
            # 处理其他角色菜单
            else:
                if choice == '1':
                    # 环境监测功能
                    print("\n=== 环境监测功能 ===")
                    print("1. 查看传感器列表")
                    print("2. 添加传感器")
                    print("3. 查看区域监测数据")
                    env_choice = input("请输入您的选择: ")
                    
                    if env_choice == '1':
                        # 查看传感器列表
                        print("\n=== 传感器列表 ===")
                        sensors = self.db_instance.get_sensors()
                        if sensors:
                            for sensor in sensors:
                                print(f"传感器ID: {sensor['SensorID']}, 区域ID: {sensor['region_id']}, 型号: {sensor['DeviceModel']}, 类型: {sensor['MonitoringType']}")
                        else:
                            print("暂无传感器数据")
                    elif env_choice == '2':
                        # 添加传感器
                        print("\n=== 添加传感器 ===")
                        region_id = input("请输入区域ID: ")
                        device_model = input("请输入设备型号: ")
                        monitoring_type = input("请输入监测类型: ")
                        install_time = input("请输入安装时间 (YYYY-MM-DD HH:MM:SS): ")
                        communication_protocol = input("请输入通信协议: ")
                        try:
                            sensor_id = self.db_instance.add_sensor(region_id, device_model, monitoring_type, install_time, communication_protocol)
                            if sensor_id:
                                print(f"✅ 传感器添加成功，ID: {sensor_id}")
                            else:
                                print("❌ 传感器添加失败")
                        except Exception as e:
                            print(f"❌ 传感器添加失败: {e}")
                    elif env_choice == '3':
                        # 查看区域监测数据
                        print("\n=== 区域监测数据 ===")
                        region_id = input("请输入区域ID: ")
                        start_time = input("请输入开始时间 (YYYY-MM-DD HH:MM:SS): ")
                        end_time = input("请输入结束时间 (YYYY-MM-DD HH:MM:SS): ")
                        try:
                            data = self.db_instance.get_monitoring_data_by_area(region_id, start_time, end_time)
                            if data:
                                for item in data[:10]:  # 只显示前10条
                                    print(f"数据ID: {item['DataID']}, 时间: {item['DataTime']}, 温度: {item['Temperature']}, 湿度: {item['Humidity']}")
                                if len(data) > 10:
                                    print(f"... 共 {len(data)} 条数据，仅显示前10条")
                            else:
                                print("暂无监测数据")
                        except Exception as e:
                            print(f"❌ 获取监测数据失败: {e}")
                    else:
                        print("无效的选择")
                elif choice == '2':
                    # 灾害预警功能
                    print("\n=== 灾害预警功能 ===")
                    print("1. 查看预警规则")
                    print("2. 添加预警规则")
                    print("3. 查看预警记录")
                    warning_choice = input("请输入您的选择: ")
                    
                    if warning_choice == '1':
                        # 查看预警规则
                        print("\n=== 预警规则列表 ===")
                        rules = self.db_instance.get_warning_rules()
                        if rules:
                            for rule in rules:
                                print(f"规则ID: {rule['RuleID']}, 类型: {rule['WarningType']}, 级别: {rule['WarningLevel']}, 状态: {'生效' if rule['IsActive'] else '失效'}")
                        else:
                            print("暂无预警规则")
                    elif warning_choice == '2':
                        # 添加预警规则
                        print("\n=== 添加预警规则 ===")
                        warning_type = input("请输入预警类型 (火灾/旱情/病虫害等): ")
                        trigger_condition = input("请输入触发条件: ")
                        warning_level = input("请输入预警级别 (一般/较重/严重/特别严重): ")
                        is_active = input("是否生效 (1:生效, 0:失效, 默认1): ") or '1'
                        try:
                            rule_id = self.db_instance.add_warning_rule(warning_type, trigger_condition, warning_level, int(is_active))
                            if rule_id:
                                print(f"✅ 预警规则添加成功，ID: {rule_id}")
                            else:
                                print("❌ 预警规则添加失败")
                        except Exception as e:
                            print(f"❌ 预警规则添加失败: {e}")
                    elif warning_choice == '3':
                        # 查看预警记录
                        print("\n=== 预警记录 ===")
                        region_id = input("请输入区域ID: ")
                        try:
                            warnings = self.db_instance.get_warnings_by_area(region_id)
                            if warnings:
                                for warning in warnings:
                                    print(f"预警ID: {warning['WarningID']}, 时间: {warning['TriggerTime']}, 内容: {warning['WarningContent']}, 状态: {warning['Status']}")
                            else:
                                print("暂无预警记录")
                        except Exception as e:
                            print(f"❌ 获取预警记录失败: {e}")
                    else:
                        print("无效的选择")
                elif choice == '3':
                    # 资源管理功能
                    print("\n=== 资源管理功能 ===")
                    print("1. 查看林草资源")
                    print("2. 添加林草资源")
                    print("3. 查看资源变动记录")
                    resource_choice = input("请输入您的选择: ")
                    
                    if resource_choice == '1':
                        # 查看林草资源
                        print("\n=== 林草资源列表 ===")
                        resources = self.db_instance.get_forest_resources()
                        if resources:
                            for resource in resources:
                                print(f"资源ID: {resource['ResourceID']}, 区域ID: {resource['RegionID']}, 类型: {resource['ResourceType']}, 面积: {resource['CoverageArea']}")
                        else:
                            print("暂无林草资源数据")
                    elif resource_choice == '2':
                        # 添加林草资源
                        print("\n=== 添加林草资源 ===")
                        region_id = input("请输入区域ID: ")
                        resource_type = input("请输入资源类型: ")
                        coverage_area = input("请输入覆盖面积: ")
                        tree_species = input("请输入树种: ")
                        growth_status = input("请输入生长状态: ")
                        updated_by = input("请输入更新人ID: ")
                        try:
                            resource_id = self.db_instance.add_forest_resource(region_id, resource_type, coverage_area, tree_species, growth_status, updated_by)
                            if resource_id:
                                print(f"✅ 林草资源添加成功，ID: {resource_id}")
                            else:
                                print("❌ 林草资源添加失败")
                        except Exception as e:
                            print(f"❌ 林草资源添加失败: {e}")
                    elif resource_choice == '3':
                        # 查看资源变动记录
                        print("\n=== 资源变动记录 ===")
                        resource_id = input("请输入资源ID (可选): ")
                        try:
                            records = self.db_instance.get_resource_change_records(resource_id if resource_id else None)
                            if records:
                                for record in records:
                                    print(f"变动ID: {record['ChangeID']}, 资源ID: {record['ResourceID']}, 类型: {record['ChangeType']}, 时间: {record['ChangeTime']}")
                            else:
                                print("暂无资源变动记录")
                        except Exception as e:
                            print(f"❌ 获取资源变动记录失败: {e}")
                    else:
                        print("无效的选择")
                elif choice == '4':
                    # 设备管理功能
                    print("\n=== 设备管理功能 ===")
                    print("1. 查看设备档案")
                    print("2. 查看设备状态")
                    equipment_choice = input("请输入您的选择: ")
                    
                    if equipment_choice == '1':
                        # 查看设备档案
                        print("\n=== 设备档案列表 ===")
                        devices = self.db_instance.get_device_archives()
                        if devices:
                            for device in devices:
                                print(f"设备ID: {device['DeviceID']}, 名称: {device['DeviceName']}, 类型: {device['DeviceType']}, 区域ID: {device['RegionID']}")
                        else:
                            print("暂无设备档案数据")
                    elif equipment_choice == '2':
                        # 查看设备状态
                        print("\n=== 设备状态 ===")
                        device_id = input("请输入设备ID: ")
                        try:
                            status = self.db_instance.get_device_status(device_id)
                            if status:
                                for item in status[:5]:  # 只显示最近5条
                                    print(f"状态ID: {item['StatusID']}, 时间: {item['CollectionTime']}, 运行状态: {item['RunningStatus']}")
                            else:
                                print("暂无设备状态数据")
                        except Exception as e:
                            print(f"❌ 获取设备状态失败: {e}")
                    else:
                        print("无效的选择")
                elif choice == '5':
                    # 统计分析功能
                    print("\n=== 统计分析功能 ===")
                    print("1. 查看报表模板")
                    print("2. 生成报表")
                    stats_choice = input("请输入您的选择: ")
                    
                    if stats_choice == '1':
                        # 查看报表模板
                        print("\n=== 报表模板列表 ===")
                        templates = self.db_instance.get_report_templates()
                        if templates:
                            for template in templates:
                                print(f"模板ID: {template['TemplateID']}, 名称: {template['TemplateName']}, 类型: {template['ReportType']}")
                        else:
                            print("暂无报表模板")
                    elif stats_choice == '2':
                        # 生成报表
                        print("\n=== 生成报表 ===")
                        template_id = input("请输入模板ID: ")
                        region_id = input("请输入区域ID: ")
                        start_time = input("请输入开始时间 (YYYY-MM-DD HH:MM:SS): ")
                        end_time = input("请输入结束时间 (YYYY-MM-DD HH:MM:SS): ")
                        generated_by = input("请输入生成人ID: ")
                        try:
                            import datetime
                            start_time_dt = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                            end_time_dt = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                            report_id = self.db_instance.generate_report_from_template(template_id, region_id, start_time_dt, end_time_dt, generated_by)
                            if report_id:
                                print(f"✅ 报表生成成功，ID: {report_id}")
                            else:
                                print("❌ 报表生成失败")
                        except ValueError as e:
                            print(f"❌ 时间格式错误: {e}")
                        except Exception as e:
                            print(f"❌ 报表生成失败: {e}")
                    else:
                        print("无效的选择")
                else:
                    print("无效的选择，请重新输入")
        
        # 6. 断开数据库连接
        self.db_conn.disconnect()

class DisasterWarningDatabase:
    def __init__(self, db_connection):
        """
        初始化灾害预警数据库
        :param db_connection: 数据库连接对象
        """
        # 为self.db创建独立的数据库连接，避免直接使用传入的连接导致的并发问题
        self.db = db_connection.get_new_connection()
        
        # 初始化各个业务线模块，每个模块使用独立的数据库连接
        from modules.environmental_monitoring import EnvironmentalMonitoringModule
        from modules.disaster_warning import DisasterWarningModule
        from modules.resource_management import ResourceManagementModule
        from modules.equipment_management import EquipmentManagementModule
        from modules.statistical_analysis import StatisticalAnalysisModule
        
        # 为每个模块创建独立的数据库连接
        self.env_module = EnvironmentalMonitoringModule(db_connection.get_new_connection())
        self.warning_module = DisasterWarningModule(db_connection.get_new_connection())
        self.resource_module = ResourceManagementModule(db_connection.get_new_connection())
        self.equipment_module = EquipmentManagementModule(db_connection.get_new_connection())
        self.statistics_module = StatisticalAnalysisModule(db_connection.get_new_connection())
    
    def create_tables(self):
        """
        创建灾害预警相关的数据库表
        """
        print("开始创建所有业务线数据库表...")
        
        # 按顺序创建各个业务线的表
        if not self.env_module.create_tables():
            print("创建环境监测表失败")
            return False
        print("环境监测表创建成功")
        
        if not self.warning_module.create_tables():
            print("创建灾害预警表失败")
            return False
        print("灾害预警表创建成功")
        
        if not self.resource_module.create_tables():
            print("创建资源管理表失败")
            return False
        print("资源管理表创建成功")
        
        if not self.equipment_module.create_tables():
            print("创建设备管理表失败")
            return False
        print("设备管理表创建成功")
        
        if not self.statistics_module.create_tables():
            print("创建统计分析表失败")
            return False
        print("统计分析表创建成功")
        
        print("所有业务线数据库表创建成功！")
        return True
    
    # 环境监测业务线 - 传感器管理
    def add_sensor(self, region_id, device_model, monitoring_type, install_time, communication_protocol):
        """
        添加传感器
        :param region_id: 区域ID
        :param device_model: 设备型号
        :param monitoring_type: 监测类型
        :param install_time: 安装时间
        :param communication_protocol: 通信协议
        :return: 传感器ID
        """
        return self.env_module.add_sensor(region_id, device_model, monitoring_type, install_time, communication_protocol)
    
    def get_sensors(self, region_id=None):
        """
        获取传感器列表
        :param region_id: 区域ID（可选）
        :return: 传感器列表
        """
        return self.env_module.get_sensors(region_id)
    
    # 环境监测业务线 - 监测数据管理
    def add_monitoring_data(self, sensor_id, region_id, data_time, temperature=None, humidity=None, wind_speed=None, rainfall=None, pest_disease_value=None, smoke_value=None, soil_moisture=None, image_path=None):
        """
        添加监测数据
        :param sensor_id: 传感器ID
        :param region_id: 区域ID
        :param data_time: 数据时间
        :param temperature: 温度
        :param humidity: 湿度
        :param wind_speed: 风速
        :param rainfall: 降雨量
        :param pest_disease_value: 病虫害指数
        :param smoke_value: 烟雾值
        :param soil_moisture: 土壤湿度
        :param image_path: 图像路径
        :return: 数据ID
        """
        return self.env_module.add_monitoring_data(sensor_id, region_id, data_time, temperature, humidity, wind_speed, rainfall, pest_disease_value, smoke_value, soil_moisture, image_path)
    
    def get_monitoring_data_by_area(self, region_id, start_time, end_time):
        """
        按区域获取监测数据
        :param region_id: 区域ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: 监测数据列表
        """
        return self.env_module.get_monitoring_data_by_area(region_id, start_time, end_time)
    
    # 灾害预警业务线 - 预警规则管理
    def add_warning_rule(self, warning_type, trigger_condition, warning_level, is_active=1):
        """
        添加预警规则
        :param warning_type: 预警类型
        :param trigger_condition: 触发条件
        :param warning_level: 预警级别
        :param is_active: 是否生效
        :return: 规则ID
        """
        return self.warning_module.add_warning_rule(warning_type, trigger_condition, warning_level, is_active)
    
    def update_warning_rule(self, rule_id, warning_type, trigger_condition, warning_level, is_active):
        """
        更新预警规则
        :param rule_id: 规则ID
        :param warning_type: 预警类型
        :param trigger_condition: 触发条件
        :param warning_level: 预警级别
        :param is_active: 是否生效
        :return: 是否更新成功
        """
        return self.warning_module.update_warning_rule(rule_id, warning_type, trigger_condition, warning_level, is_active)
    
    def get_warning_rules(self, warning_type=None):
        """
        获取预警规则列表
        :param warning_type: 预警类型（可选）
        :return: 预警规则列表
        """
        return self.warning_module.get_warning_rules(warning_type)
    
    # 灾害预警业务线 - 预警记录管理
    def add_warning_record(self, rule_id, region_id, trigger_time, warning_content, status='未处理', handler_id=None, handle_result=None):
        """
        添加预警记录
        :param rule_id: 规则ID
        :param region_id: 区域ID
        :param trigger_time: 触发时间
        :param warning_content: 预警内容
        :param status: 处理状态
        :param handler_id: 处理人ID
        :param handle_result: 处理结果
        :return: 预警ID
        """
        return self.warning_module.add_warning_record(rule_id, region_id, trigger_time, warning_content, status, handler_id, handle_result)
    
    def update_warning_status(self, warning_id, status, handler_id, handle_result=None):
        """
        更新预警状态
        :param warning_id: 预警ID
        :param status: 处理状态
        :param handler_id: 处理人ID
        :param handle_result: 处理结果
        :return: 是否更新成功
        """
        return self.warning_module.update_warning_status(warning_id, status, handler_id, handle_result)
    
    def get_warnings_by_area(self, region_id):
        """
        按区域获取预警记录
        :param region_id: 区域ID
        :return: 预警记录列表
        """
        return self.warning_module.get_warnings_by_area(region_id)
    
    # 资源管理业务线 - 林草资源管理
    def add_forest_resource(self, region_id, resource_type, coverage_area, tree_species, growth_status, updated_by):
        """
        添加林草资源
        :param region_id: 区域ID
        :param resource_type: 资源类型
        :param coverage_area: 覆盖面积
        :param tree_species: 树种
        :param growth_status: 生长状态
        :param updated_by: 更新人ID
        :return: 资源ID
        """
        return self.resource_module.add_forest_resource(region_id, resource_type, coverage_area, tree_species, growth_status, updated_by)
    
    def update_forest_resource(self, resource_id, coverage_area=None, tree_species=None, growth_status=None, updated_by=None):
        """
        更新林草资源
        :param resource_id: 资源ID
        :param coverage_area: 覆盖面积（可选）
        :param tree_species: 树种（可选）
        :param growth_status: 生长状态（可选）
        :param updated_by: 更新人ID（可选）
        :return: 是否更新成功
        """
        return self.resource_module.update_forest_resource(resource_id, coverage_area, tree_species, growth_status, updated_by)
    
    def get_forest_resources(self, region_id=None):
        """
        获取林草资源列表
        :param region_id: 区域ID（可选）
        :return: 林草资源列表
        """
        return self.resource_module.get_forest_resources(region_id)
    
    # 资源管理业务线 - 资源变动记录
    def add_resource_change_record(self, resource_id, change_type, change_reason, change_time, operator_id):
        """
        添加资源变动记录
        :param resource_id: 资源ID
        :param change_type: 变动类型
        :param change_reason: 变动原因
        :param change_time: 变动时间
        :param operator_id: 操作人ID
        :return: 变动ID
        """
        return self.resource_module.add_resource_change_record(resource_id, change_type, change_reason, change_time, operator_id)
    
    def get_resource_change_records(self, resource_id=None, audit_status=None):
        """
        获取资源变动记录
        :param resource_id: 资源ID（可选）
        :param audit_status: 审核状态（可选）
        :return: 资源变动记录列表
        """
        return self.resource_module.get_resource_change_records(resource_id, audit_status)
    
    def audit_resource_change(self, change_id, audit_status, auditor_id, audit_comments=None):
        """
        审核资源变动记录
        :param change_id: 变动记录ID
        :param audit_status: 审核状态
        :param auditor_id: 审核人ID
        :param audit_comments: 审核意见（可选）
        :return: 是否审核成功
        """
        return self.resource_module.audit_resource_change(change_id, audit_status, auditor_id, audit_comments)
    
    # 统计分析业务线 - 报表模板管理
    def get_report_templates(self, report_type=None, audit_status=None, is_active=None):
        """
        获取报表模板列表
        :param report_type: 报表类型（可选）
        :param audit_status: 审核状态（可选）
        :param is_active: 是否启用（可选）
        :return: 报表模板列表
        """
        return self.statistics_module.get_report_templates(report_type, audit_status, is_active)
    
    def generate_report_from_template(self, template_id, region_id, start_time, end_time, generated_by):
        """
        基于模板生成报表
        :param template_id: 模板ID
        :param region_id: 区域ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param generated_by: 生成人员ID
        :return: 生成的报表ID
        """
        return self.statistics_module.generate_report_from_template(template_id, region_id, start_time, end_time, generated_by)
    
    def get_generated_reports(self, region_id=None, report_type=None, start_time=None, end_time=None):
        """
        获取生成的报表列表
        :param region_id: 区域ID（可选）
        :param report_type: 报表类型（可选）
        :param start_time: 开始时间（可选）
        :param end_time: 结束时间（可选）
        :return: 生成的报表列表
        """
        return self.statistics_module.get_generated_reports(region_id, report_type, start_time, end_time)
    
    def audit_resource_change(self, change_id, audit_status, auditor_id, audit_comments=None):
        """
        审核资源变动记录
        :param change_id: 变动记录ID
        :param audit_status: 审核状态（通过/拒绝）
        :param auditor_id: 审核人ID
        :param audit_comments: 审核意见
        :return: 是否审核成功
        """
        return self.resource_module.audit_resource_change(change_id, audit_status, auditor_id, audit_comments)
    
    def get_equipment_inspections(self, device_id=None, inspector_id=None, audit_status=None):
        """
        获取设备巡检记录
        :param device_id: 设备ID（可选）
        :param inspector_id: 巡检人员ID（可选）
        :param audit_status: 审核状态（可选）
        :return: 设备巡检记录列表
        """
        return self.equipment_module.get_equipment_inspections(device_id, inspector_id, audit_status)
    
    def audit_equipment_inspection(self, inspection_id, audit_status, auditor_id, audit_comments=None):
        """
        审核设备巡检记录
        :param inspection_id: 巡检记录ID
        :param audit_status: 审核状态（通过/拒绝）
        :param auditor_id: 审核人ID
        :param audit_comments: 审核意见
        :return: 是否审核成功
        """
        return self.equipment_module.audit_equipment_inspection(inspection_id, audit_status, auditor_id, audit_comments)
    
    # 设备管理业务线 - 设备档案管理
    def add_device_archive(self, device_name, device_type, model_specification, purchase_time, region_id, installer_id, warranty_period):
        """
        添加设备档案
        :param device_name: 设备名称
        :param device_type: 设备类型
        :param model_specification: 型号规格
        :param purchase_time: 采购时间
        :param region_id: 区域ID
        :param installer_id: 安装人员ID
        :param warranty_period: 质保期
        :return: 设备ID
        """
        return self.equipment_module.add_device_archive(device_name, device_type, model_specification, purchase_time, region_id, installer_id, warranty_period)
    
    def get_device_archives(self, region_id=None, device_type=None, status=None):
        """
        获取设备档案列表
        :param region_id: 区域ID（可选）
        :param device_type: 设备类型（可选）
        :param status: 设备状态（可选）
        :return: 设备档案列表
        """
        return self.equipment_module.get_device_archives(region_id, device_type, status)
    
    # 设备管理业务线 - 设备状态管理
    def add_device_status(self, device_id, running_status, battery_level=None, signal_strength=None):
        """
        添加设备状态
        :param device_id: 设备ID
        :param running_status: 运行状态
        :param battery_level: 电池电量
        :param signal_strength: 信号强度
        :return: 状态ID
        """
        return self.equipment_module.add_device_status(device_id, running_status, battery_level, signal_strength)
    
    def get_device_status(self, device_id, start_time=None, end_time=None):
        """
        获取设备状态记录
        :param device_id: 设备ID
        :param start_time: 开始时间（可选）
        :param end_time: 结束时间（可选）
        :return: 设备状态记录列表
        """
        return self.equipment_module.get_device_status(device_id, start_time, end_time)
    
    # 设备管理业务线 - 设备巡检记录管理
    def add_equipment_inspection(self, device_id, inspection_time, inspector_id, maintenance_type, inspection_result, problem_description=None, maintenance_content=None, maintenance_result=None):
        """
        添加设备巡检记录
        :param device_id: 设备ID
        :param inspection_time: 巡检时间
        :param inspector_id: 巡检人员ID
        :param maintenance_type: 维护类型
        :param inspection_result: 巡检结果
        :param problem_description: 问题描述（可选）
        :param maintenance_content: 维护内容（可选）
        :param maintenance_result: 维护结果（可选）
        :return: 巡检ID
        """
        return self.equipment_module.add_equipment_inspection(device_id, inspection_time, inspector_id, maintenance_type, inspection_result, problem_description, maintenance_content, maintenance_result)
    
    def get_equipment_inspections(self, device_id=None, inspector_id=None):
        """
        获取设备巡检记录
        :param device_id: 设备ID（可选）
        :param inspector_id: 巡检人员ID（可选）
        :return: 设备巡检记录列表
        """
        return self.equipment_module.get_equipment_inspections(device_id, inspector_id)
    
    # 统计分析业务线 - 报表模板管理
    def add_report_template(self, template_name, report_type, statistical_indicators, description=None, 
                           statistical_dimension='区域/时间/类型', generation_cycle='月'):
        """
        添加报表模板
        :param template_name: 模板名称
        :param report_type: 报表类型
        :param statistical_indicators: 统计指标（JSON格式）
        :param description: 模板描述（可选）
        :param statistical_dimension: 统计维度（区域/时间/类型）
        :param generation_cycle: 生成周期（日/周/月）
        :return: 模板ID
        """
        return self.statistics_module.add_report_template(template_name, report_type, statistical_indicators, description, 
                                                         statistical_dimension, generation_cycle)
    
    def get_report_templates(self, report_type=None, audit_status=None, is_active=None):
        """
        获取报表模板列表
        :param report_type: 报表类型（可选）
        :param audit_status: 审核状态（可选）
        :param is_active: 是否启用（可选）
        :return: 报表模板列表
        """
        return self.statistics_module.get_report_templates(report_type, audit_status, is_active)
    
    def get_report_template(self, template_id):
        """
        获取单个报表模板
        :param template_id: 模板ID
        :return: 报表模板信息或None
        """
        return self.statistics_module.get_report_template(template_id)
    
    def audit_report_template(self, template_id, audit_status, audit_by, audit_comments=None):
        """
        审核报表模板
        :param template_id: 模板ID
        :param audit_status: 审核状态（已通过/已拒绝）
        :param audit_by: 审核人ID
        :param audit_comments: 审核意见（可选）
        :return: 是否审核成功
        """
        return self.statistics_module.audit_report_template(template_id, audit_status, audit_by, audit_comments)
    
    def update_report_template_status(self, template_id, is_active):
        """
        更新报表模板状态（启用/禁用）
        :param template_id: 模板ID
        :param is_active: 是否启用
        :return: 是否更新成功
        """
        return self.statistics_module.update_report_template_status(template_id, is_active)
    
    # 统计分析业务线 - 生成报表管理
    def generate_report_from_template(self, template_id, region_id, start_time, end_time, generated_by):
        """
        基于模板生成报表
        :param template_id: 模板ID
        :param region_id: 区域ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param generated_by: 生成人员ID
        :return: 生成的报表ID
        """
        return self.statistics_module.generate_report_from_template(template_id, region_id, start_time, end_time, generated_by)
    
    def get_generated_reports(self, region_id=None, report_type=None, start_time=None, end_time=None):
        """
        获取生成的报表列表
        :param region_id: 区域ID（可选）
        :param report_type: 报表类型（可选）
        :param start_time: 开始时间（可选）
        :param end_time: 结束时间（可选）
        :return: 生成的报表列表
        """
        return self.statistics_module.get_generated_reports(region_id, report_type, start_time, end_time)
    
    # 获取用户信息
    def get_user_by_username(self, username):
        """
        根据用户名获取用户信息（用户名不区分大小写）
        :param username: 用户名
        :return: 用户信息字典
        """
        try:
            # SQL Server表名引用（User是关键字，需要用[]括起来）
            table_name = "[User]"
            
            # 用户名不区分大小写查询（SQL Server）
            sql = f"SELECT * FROM {table_name} WHERE Username = ? COLLATE SQL_Latin1_General_CP1_CI_AS"
            
            result = self.db.fetch_one(sql, (username,))
            
            if result:
                # 正确映射数据库字段，根据实际数据库结构调整
                # 实际数据库结构：UserID, Username, Password, Name, Contact, Role, Status
                user_info = {
                    'UserID': result[0],
                    'Username': result[1],
                    'Password': result[2],  # 第3列是密码
                    'Name': result[3],       # 第4列是姓名
                    'Contact': result[4],    # 第5列是联系方式
                    'Role': result[5],       # 第6列是角色
                    'Status': result[6]      # 第7列是状态
                }
                return user_info
            return None
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None
    
    # 获取用户列表
    def get_users(self, role=None):
        """
        获取用户列表，支持按角色过滤
        :param role: 角色（可选）
        :return: 用户列表
        """
        try:
            # SQL Server表名引用（User是关键字，需要用[]括起来）
            table_name = "[User]"
            # 实际数据库结构：UserID, Username, Password, Name, Contact, Role, Status
            if role:
                sql = f"SELECT * FROM {table_name} WHERE Role = ?"
                users = self.db.fetch_all(sql, (role,))
            else:
                # 获取所有用户
                sql = f"SELECT * FROM {table_name}"
                users = self.db.fetch_all(sql)
            
            user_list = []
            for user in users:
                # 正确映射数据库字段，根据实际数据库结构调整
                user_info = {
                    'UserID': user[0],
                    'Username': user[1],
                    'Name': user[3],       # 第4列是姓名
                    'Role': user[5],       # 第6列是角色
                    'Contact': user[4],    # 第5列是联系方式
                    'Status': user[6]      # 第7列是状态
                }
                user_list.append(user_info)
            return user_list
        except Exception as e:
            print(f"获取用户列表失败: {e}")
            return []
    
    # 反馈管理功能
    def add_feedback(self, feedback_type, region_id, description, contact):
        """
        添加反馈记录
        :param feedback_type: 反馈类型
        :param region_id: 区域ID
        :param description: 详细描述
        :param contact: 联系方式
        :return: 反馈ID
        """
        try:
            # 生成唯一的FeedbackID
            count = self.db.fetch_one("SELECT COUNT(*) FROM Feedback")[0]
            feedback_id = f"FB{str(count + 1).zfill(3)}"
            
            # 插入反馈记录
            sql = """
            INSERT INTO Feedback (FeedbackID, FeedbackType, RegionID, Description, Contact)
            VALUES (?, ?, ?, ?, ?)
            """
            params = (feedback_id, feedback_type, region_id, description, contact)
            
            if self.db.execute(sql, params):
                print(f"反馈添加成功，ID: {feedback_id}")
                return feedback_id
            else:
                return None
        except Exception as e:
            print(f"添加反馈失败: {e}")
            return None
    
    def get_feedbacks(self, status=None, region_id=None):
        """
        获取反馈列表，支持按状态和区域过滤
        :param status: 状态（可选）
        :param region_id: 区域ID（可选）
        :return: 反馈列表
        """
        try:
            # 使用LEFT JOIN连接Region表，获取区域名称
            sql = "SELECT f.*, r.RegionName FROM Feedback f LEFT JOIN Region r ON f.RegionID = r.RegionID WHERE 1=1"
            params = []
            
            if status:
                sql += " AND f.Status = ?"
                params.append(status)
            
            if region_id:
                sql += " AND f.RegionID = ?"
                params.append(region_id)
            
            sql += " ORDER BY f.SubmitTime DESC"
            
            results = self.db.fetch_all(sql, tuple(params))
            
            feedback_list = []
            for row in results:
                feedback_list.append({
                    'FeedbackID': row[0],
                    'FeedbackType': row[1],
                    'RegionID': row[2],
                    'RegionName': row[10],  # 添加区域名称
                    'Description': row[3],
                    'Contact': row[4],
                    'SubmitTime': row[5],
                    'Status': row[6],
                    'HandlerID': row[7],
                    'HandleTime': row[8],
                    'HandleResult': row[9]
                })
            
            return feedback_list
        except Exception as e:
            print(f"获取反馈列表失败: {e}")
            return []
    
    def update_feedback_status(self, feedback_id, status, handler_id=None, handle_result=None):
        """
        更新反馈状态
        :param feedback_id: 反馈ID
        :param status: 状态
        :param handler_id: 处理人ID（可选）
        :param handle_result: 处理结果（可选）
        :return: 是否更新成功
        """
        try:
            sql = "UPDATE Feedback SET Status = ?"
            params = [status]
            
            if handler_id:
                sql += ", HandlerID = ?, HandleTime = GETDATE()"
                params.extend([handler_id,])
            
            if handle_result:
                sql += ", HandleResult = ?"
                params.append(handle_result)
            
            sql += " WHERE FeedbackID = ?"
            params.append(feedback_id)
            
            return self.db.execute(sql, params)
        except Exception as e:
            print(f"更新反馈状态失败: {e}")
            return False
    
    # 复杂SQL查询方法 - 覆盖不同业务场景
    def complex_queries(self, query_type, **kwargs):
        """
        执行复杂SQL查询，覆盖不同业务场景
        :param query_type: 查询类型
        :param kwargs: 查询参数
        :return: 查询结果
        """
        try:
            if query_type == 1:
                # 查询1: 查询某区域近7天火灾预警及处理情况
                # 连接表: WarningRecord, WarningRule
                sql = """
                SELECT 
                    wr.WarningID, wr.TriggerTime, wr.WarningContent, wr.Status, 
                    wr.HandleResult, wrule.WarningType, wrule.WarningLevel,
                    NULL AS HandlerName, NULL AS region_name
                FROM WarningRecord wr
                JOIN WarningRule wrule ON wr.RuleID = wrule.RuleID
                WHERE 1=1
                AND wr.TriggerTime BETWEEN ? AND ?
                AND wrule.WarningType = '火灾'
                ORDER BY wr.TriggerTime DESC
                """
                params = (kwargs['start_time'], kwargs['end_time'])
                results = self.db.fetch_all(sql, params)
                
                return [{
                    'WarningID': r[0],
                    'TriggerTime': r[1],
                    'WarningContent': r[2],
                    'Status': r[3],
                    'HandleResult': r[4],
                    'WarningType': r[5],
                    'WarningLevel': r[6],
                    'HandlerName': r[7],
                    'region_name': r[8]
                } for r in results]
            
            elif query_type == 2:
                # 查询2: 统计各区域设备故障次数及维护成本
                # 连接表: Region, DeviceArchive, DeviceStatus
                sql = """
                SELECT 
                    r.region_name, 
                    COUNT(DISTINCT da.DeviceID) AS DeviceCount,
                    SUM(CASE WHEN ds.RunningStatus = '故障' THEN 1 ELSE 0 END) AS FaultCount,
                    0 AS InspectionCount
                FROM Region r
                LEFT JOIN DeviceArchive da ON r.RegionID = da.RegionID
                LEFT JOIN DeviceStatus ds ON da.DeviceID = ds.DeviceID
                WHERE ds.CollectionTime BETWEEN ? AND ?
                GROUP BY r.region_name
                ORDER BY FaultCount DESC
                """
                params = (kwargs['start_time'], kwargs['end_time'])
                results = self.db.fetch_all(sql, params)
                
                return [{
                    'region_name': r[0],
                    'DeviceCount': r[1],
                    'FaultCount': r[2],
                    'InspectionCount': r[3]
                } for r in results]
            
            elif query_type == 3:
                # 查询3: 查询某区域传感器数据及相关设备状态
                # 连接表: Sensor, MonitoringData, DeviceArchive, DeviceStatus, Region
                sql = """
                SELECT 
                    s.SensorID, s.DeviceModel, s.MonitoringType,
                    md.DataTime, md.Temperature, md.Humidity, md.WindSpeed,
                    ds.RunningStatus, ds.BatteryLevel, ds.SignalStrength,
                    da.DeviceName, r.RegionName
                FROM Sensor s
                JOIN MonitoringData md ON s.SensorID = md.SensorID
                JOIN DeviceArchive da ON s.SensorID = da.DeviceID
                LEFT JOIN DeviceStatus ds ON da.DeviceID = ds.DeviceID
                JOIN Region r ON s.RegionID = r.RegionID
                WHERE s.RegionID = ?
                AND md.DataTime BETWEEN ? AND ?
                ORDER BY md.DataTime DESC, s.SensorID
                """
                params = (kwargs['region_id'], kwargs['start_time'], kwargs['end_time'])
                results = self.db.fetch_all(sql, params)
                
                return [{
                    'SensorID': r[0],
                    'DeviceModel': r[1],
                    'MonitoringType': r[2],
                    'DataTime': r[3],
                    'Temperature': r[4],
                    'Humidity': r[5],
                    'WindSpeed': r[6],
                    'RunningStatus': r[7],
                    'BatteryLevel': r[8],
                    'SignalStrength': r[9],
                    'DeviceName': r[10],
                    'region_name': r[11]
                } for r in results]
            
            elif query_type == 4:
                # 查询4: 查询某区域林草资源变动及相关预警情况
                # 连接表: ForestResource, ResourceChangeRecord, WarningRecord, Region, User
                sql = """
                SELECT 
                    fr.ResourceID, fr.ResourceType, fr.CoverageArea, fr.TreeSpecies,
                    rc.ChangeID, rc.ChangeType, rc.ChangeReason, rc.ChangeTime,
                    u.Name AS OperatorName,
                    COUNT(wr.WarningID) AS WarningCount,
                    r.RegionName
                FROM ForestResource fr
                JOIN ResourceChangeRecord rc ON fr.ResourceID = rc.ResourceID
                LEFT JOIN [User] u ON rc.OperatorID = u.UserID
                LEFT JOIN WarningRecord wr ON fr.RegionID = wr.RegionID AND wr.TriggerTime BETWEEN rc.ChangeTime AND DATEADD(day, 7, rc.ChangeTime)
                JOIN Region r ON fr.RegionID = r.RegionID
                WHERE fr.RegionID = ?
                AND rc.ChangeTime BETWEEN ? AND ?
                GROUP BY fr.ResourceID, rc.ChangeID
                ORDER BY rc.ChangeTime DESC
                """
                params = (kwargs['region_id'], kwargs['start_time'], kwargs['end_time'])
                results = self.db.fetch_all(sql, params)
                
                return [{
                    'ResourceID': r[0],
                    'ResourceType': r[1],
                    'CoverageArea': r[2],
                    'TreeSpecies': r[3],
                    'ChangeID': r[4],
                    'ChangeType': r[5],
                    'ChangeReason': r[6],
                    'ChangeTime': r[7],
                    'OperatorName': r[8],
                    'WarningCount': r[9],
                    'region_name': r[10]
                } for r in results]
            
            elif query_type == 5:
                # 查询5: 查询某时间段内各类型传感器监测数据统计
                # 连接表: Sensor, MonitoringData, Region, DeviceArchive
                sql = """
                SELECT 
                    s.MonitoringType, 
                    r.RegionName,
                    da.DeviceName,
                    COUNT(md.DataID) AS DataCount,
                    AVG(md.Temperature) AS AvgTemperature,
                    AVG(md.Humidity) AS AvgHumidity,
                    MAX(md.Temperature) AS MaxTemperature,
                    MIN(md.Temperature) AS MinTemperature
                FROM Sensor s
                JOIN MonitoringData md ON s.SensorID = md.SensorID
                JOIN Region r ON s.RegionID = r.RegionID
                JOIN DeviceArchive da ON s.SensorID = da.DeviceID
                WHERE md.DataTime BETWEEN ? AND ?
                GROUP BY s.MonitoringType, r.RegionName, da.DeviceName
                ORDER BY s.MonitoringType, r.RegionName
                """
                params = (kwargs['start_time'], kwargs['end_time'])
                results = self.db.fetch_all(sql, params)
                
                return [{
                    'MonitoringType': r[0],
                    'region_name': r[1],
                    'DeviceName': r[2],
                    'DataCount': r[3],
                    'AvgTemperature': r[4],
                    'AvgHumidity': r[5],
                    'MaxTemperature': r[6],
                    'MinTemperature': r[7]
                } for r in results]
            
            return None
        except Exception as e:
            print(f"执行复杂查询失败: {e}")
            return None
