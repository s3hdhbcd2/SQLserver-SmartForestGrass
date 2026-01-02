from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from smart_forest_grass_business import DatabaseConnection, DisasterWarningDatabase
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'smart_forest_grass_secret_key'

# 数据库连接
db_conn = DatabaseConnection()
db_instance = None

# 初始化数据库连接
def init_db():
    global db_instance
    db_conn.connect()
    db_instance = DisasterWarningDatabase(db_conn)
    
    # 创建数据库表
    if not db_instance.create_tables():
        print("创建数据库表失败")
    
    # 检查并添加必要的用户
    try:
        # 定义需要添加的用户列表
        users = [
            {'username': 'admin', 'password': '123456', 'name': '管理员', 'contact': 'admin@example.com', 'role': '管理员', 'status': '启用'},
            {'username': 'data_admin', 'password': '123456', 'name': '数据管理员', 'contact': 'data@example.com', 'role': '数据管理员', 'status': '启用'},
            {'username': 'ranger1', 'password': '123456', 'name': '区域护林员1', 'contact': 'ranger1@example.com', 'role': '区域护林员', 'status': '启用'},
            {'username': 'public1', 'password': '123456', 'name': '公众用户1', 'contact': 'public1@example.com', 'role': '公众用户', 'status': '启用'},
            {'username': 'supervisor1', 'password': '123456', 'name': '监管人员1', 'contact': 'supervisor1@example.com', 'role': '监管人员', 'status': '启用'}
        ]
        
        # 为每个用户执行插入操作
        for user_info in users:
            username = user_info['username']
            # 先检查用户名是否存在
            check_sql = "SELECT COUNT(*) FROM [User] WHERE Username = ?"
            result = db_conn.fetch_one(check_sql, (username,))
            if result and result[0] == 0:
                # 用户名不存在，执行插入
                # 生成唯一的UserID
                user_id = f"U{str(db_conn.fetch_one('SELECT COUNT(*) FROM [User]')[0] + 1).zfill(3)}"
                insert_sql = "INSERT INTO [User] (UserID, Username, Password, Name, Contact, Role, Status) VALUES (?, ?, ?, ?, ?, ?, ?)"
                insert_params = (user_id, username, user_info['password'], user_info['name'], user_info['contact'], user_info['role'], user_info['status'])
                if db_conn.execute(insert_sql, insert_params):
                    print(f"成功插入用户: {username} (UserID: {user_id})")
                else:
                    print(f"插入用户失败: {username}")
            else:
                print(f"用户名已存在: {username}")
        
        print("初始化用户数据成功")
    except Exception as e:
        print(f"初始化用户数据失败: {e}")

# 关闭数据库连接
def close_db():
    db_conn.disconnect()

# 应用上下文处理器，确保数据库连接初始化
@app.before_request
def before_request():
    global db_instance
    if db_instance is None:
        init_db()

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_ip = request.remote_addr
        
        # 使用现有的用户认证逻辑
        user = db_instance.get_user_by_username(username)
        
        if user and user['Password'] == password and (user['Status'] == '启用' or user['Status'] == '1' or user['Status'] == 1):
            # 登录成功，记录登录日志
            try:
                # 调用存储过程记录登录日志
                sql = "EXEC sp_log_login_attempt @user_id=?, @username=?, @login_ip=?, @login_status=?"
                db_instance.db.execute(sql, (user['UserID'], username, login_ip, '成功'))
            except Exception as e:
                print(f"记录登录日志失败: {e}")
            
            session['user'] = {
                'UserID': user['UserID'],
                'Username': user['Username'],
                'Name': user['Name'],
                'Role': user['Role'],
                'Status': user['Status']
            }
            
            # 如果是区域护林员，获取其负责的区域信息
            if user['Role'] == '区域护林员':
                # 查询该护林员负责的所有区域
                sql = "SELECT RegionID, RegionName FROM Region WHERE ManagerID = ?"
                regions = db_instance.db.fetch_all(sql, (user['UserID'],))
                session['user']['ManagedRegions'] = [{'RegionID': r[0], 'RegionName': r[1]} for r in regions]
            
            return redirect(url_for('dashboard'))
        else:
            # 登录失败，记录登录日志
            try:
                user_id = user['UserID'] if user else 'NULL'
                sql = "EXEC sp_log_login_attempt @user_id=?, @username=?, @login_ip=?, @login_status=?, @error_message=?"
                db_instance.db.execute(sql, (user_id, username, login_ip, '失败', '用户名或密码错误'))
            except Exception as e:
                print(f"记录登录日志失败: {e}")
            
            return render_template('login.html', error='用户名或密码错误')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    user = session['user']
    return render_template('dashboard.html', user=user)

@app.route('/api/get_menu')
def get_menu():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = session['user']
    role = user['Role']
    username = user['Username']
    
    print(f"当前用户: {username}, 角色: '{role}'")
    
    # 系统管理员和管理员特殊处理 - 确保他们始终获得完整菜单
    if username == 'admin' or role in ['管理员', '系统管理员', 'admin', 'system_admin']:
        menu = [
            {'code': '1', 'name': '环境监测', 'icon': '🌡️', 'href': '/environmental_monitoring'},
            {'code': '2', 'name': '灾害预警', 'icon': '⚠️', 'href': '/disaster_warning'},
            {'code': '3', 'name': '资源管理', 'icon': '🌲', 'href': '/resource_management'},
            {'code': '4', 'name': '设备管理', 'icon': '🔧', 'href': '/equipment_management'},
            {'code': '5', 'name': '统计分析', 'icon': '📊', 'href': '/statistical_analysis'},
            {'code': '6', 'name': '用户管理', 'icon': '👥', 'href': '/user_management'}
        ]
        print(f"系统管理员或管理员账号，返回6个完整菜单")
        return jsonify(menu)
    
    # 定义所有角色的菜单配置
    menus = {
        '数据管理员': [
            {'code': '1', 'name': '环境监测', 'icon': '🌡️', 'href': '/environmental_monitoring'},
            {'code': '3', 'name': '资源管理', 'icon': '🌲', 'href': '/resource_management'},
            {'code': '5', 'name': '统计分析', 'icon': '📊', 'href': '/statistical_analysis'},
            {'code': '7', 'name': '反馈管理', 'icon': '📨', 'href': '/feedback_management'}
        ],
        '区域护林员': [
            {'code': '1', 'name': '环境监测', 'icon': '🌡️', 'href': '/environmental_monitoring'},
            {'code': '2', 'name': '灾害预警', 'icon': '⚠️', 'href': '/disaster_warning'},
            {'code': '4', 'name': '设备管理', 'icon': '🔧', 'href': '/equipment_management'}
        ],
        '公众用户': [
            {'code': '1', 'name': '环境监测', 'icon': '🌡️', 'href': '/environmental_monitoring'},
            {'code': '5', 'name': '统计分析', 'icon': '📊', 'href': '/statistical_analysis'}
        ],
        '监管人员': [
            {'code': '1', 'name': '环境监测', 'icon': '🌡️', 'href': '/environmental_monitoring'},
            {'code': '2', 'name': '灾害预警', 'icon': '⚠️', 'href': '/disaster_warning'},
            {'code': '3', 'name': '资源管理', 'icon': '🌲', 'href': '/resource_management'},
            {'code': '4', 'name': '设备管理', 'icon': '🔧', 'href': '/equipment_management'},
            {'code': '5', 'name': '统计分析', 'icon': '📊', 'href': '/statistical_analysis'},
            {'code': '7', 'name': '反馈管理', 'icon': '📨', 'href': '/feedback_management'}
        ]
    }
    
    print(f"菜单配置中的角色: {list(menus.keys())}")
    
    # 尝试匹配角色，支持精确匹配和去除空格
    normalized_role = role.strip()
    
    # 处理其他角色
    if normalized_role in menus:
        menu = menus[normalized_role]
        print(f"匹配到角色 '{normalized_role}'，返回 {len(menu)} 个菜单")
        return jsonify(menu)
    else:
        # 为未知角色提供默认菜单
        menu = [
            {'code': '1', 'name': '环境监测', 'icon': '🌡️', 'href': '/environmental_monitoring'},
            {'code': '2', 'name': '灾害预警', 'icon': '⚠️', 'href': '/disaster_warning'}
        ]
        print(f"未匹配到角色，返回默认菜单")
        return jsonify(menu)

# 环境监测页面
@app.route('/environmental_monitoring')
def environmental_monitoring():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('environmental_monitoring.html', user=session['user'])

# 灾害预警页面
@app.route('/disaster_warning')
def disaster_warning():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('disaster_warning.html', user=session['user'])

# 资源管理页面
@app.route('/resource_management')
def resource_management():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # 检查权限：只有管理员、系统管理员、数据管理员和监管人员可以访问资源管理
    role = session['user']['Role']
    if role not in ['管理员', '系统管理员', '数据管理员', '监管人员']:
        return redirect(url_for('dashboard'))
    return render_template('resource_management.html', user=session['user'])

# 设备管理页面
@app.route('/equipment_management')
def equipment_management():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # 检查权限：只有管理员、系统管理员、区域护林员和监管人员可以访问设备管理
    role = session['user']['Role']
    if role not in ['管理员', '系统管理员', '区域护林员', '监管人员']:
        return redirect(url_for('dashboard'))
    return render_template('equipment_management.html', user=session['user'])

# 统计分析页面
@app.route('/statistical_analysis')
def statistical_analysis():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # 检查权限：只有管理员、系统管理员、数据管理员和监管人员可以访问统计分析
    role = session['user']['Role']
    if role not in ['管理员', '系统管理员', '数据管理员', '监管人员', '公众用户']:
        return redirect(url_for('dashboard'))
    return render_template('statistical_analysis.html', user=session['user'])

# 用户管理页面
@app.route('/user_management')
def user_management():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # 系统管理员和管理员都可以访问用户管理页面
    role = session['user']['Role']
    if role not in ['管理员', '系统管理员']:
        return redirect(url_for('dashboard'))
    return render_template('user_management.html', user=session['user'])

# 反馈管理页面
@app.route('/feedback_management')
def feedback_management():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # 系统管理员、管理员、数据管理员和监管人员都可以访问反馈管理页面
    role = session['user']['Role']
    if role not in ['管理员', '系统管理员', '数据管理员', '监管人员']:
        return redirect(url_for('dashboard'))
    return render_template('feedback_management.html', user=session['user'])

# 环境监测API
@app.route('/api/environmental_monitoring/get_sensors')
def get_sensors():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = session['user']
    role = user['Role']
    user_id = user['UserID']
    
    # 对于区域护林员，只能查看自己负责区域的传感器
    region_id = request.args.get('region_id')
    if role == '区域护林员':
        # 查询该护林员负责的所有区域
        sql = "SELECT RegionID FROM Region WHERE ManagerID = ?"
        regions = db_instance.db.fetch_all(sql, (user_id,))
        user_regions = [r[0] for r in regions]
        
        if not regions:
            # 如果没有负责区域，返回空列表
            return jsonify([])
        
        if not region_id:
            # 如果没有指定区域ID，返回所有负责区域的传感器
            all_sensors = []
            for region in user_regions:
                sensors = db_instance.get_sensors(region)
                all_sensors.extend(sensors)
            return jsonify(all_sensors)
        else:
            # 如果指定了区域ID，检查该区域是否属于该护林员负责
            if region_id not in user_regions:
                # 如果指定区域不属于该护林员负责，返回空列表
                return jsonify([])
    
    sensors = db_instance.get_sensors(region_id)
    return jsonify(sensors)

@app.route('/api/environmental_monitoring/get_monitoring_data')
def get_monitoring_data():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = session['user']
    role = user['Role']
    user_id = user['UserID']
    
    region_id = request.args.get('region_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    # 只检查start_time和end_time是否存在，允许region_id为空字符串表示全部区域
    if not start_time or not end_time:
        return jsonify({'error': '缺少必要参数'}), 400
    
    # 对于区域护林员，只能查看自己负责区域的监测数据
    if role == '区域护林员':
        # 查询该护林员负责的所有区域
        sql = "SELECT RegionID FROM Region WHERE ManagerID = ?"
        regions = db_instance.db.fetch_all(sql, (user_id,))
        user_regions = [r[0] for r in regions]
        
        if not regions:
            # 如果没有负责区域，返回空列表
            return jsonify([])
        
        if not region_id:
            # 如果没有指定区域ID，返回所有负责区域的监测数据
            all_data = []
            for region in user_regions:
                data = db_instance.get_monitoring_data_by_area(region, start_time, end_time)
                all_data.extend(data)
            return jsonify(all_data)
        else:
            # 如果指定了区域ID，检查该区域是否属于该护林员负责
            if region_id not in user_regions:
                # 如果指定区域不属于该护林员负责，返回空列表
                return jsonify([])
    
    data = db_instance.get_monitoring_data_by_area(region_id, start_time, end_time)
    return jsonify(data)

# 灾害预警API
@app.route('/api/disaster_warning/get_warning_rules')
def get_warning_rules():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    warning_type = request.args.get('warning_type')
    rules = db_instance.get_warning_rules(warning_type)
    return jsonify(rules)

@app.route('/api/disaster_warning/get_warnings')
def get_warnings():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = session['user']
    role = user['Role']
    user_id = user['UserID']
    
    region_id = request.args.get('region_id')
    
    # 对于区域护林员，只能查看自己负责区域的预警
    if role == '区域护林员':
        # 查询该护林员负责的所有区域
        sql = "SELECT RegionID FROM Region WHERE ManagerID = ?"
        regions = db_instance.db.fetch_all(sql, (user_id,))
        user_regions = [r[0] for r in regions]
        
        if not region_id:
            # 如果没有指定区域ID，使用第一个负责的区域
            if regions:
                region_id = regions[0][0]
            else:
                # 如果没有负责区域，返回空列表
                return jsonify([])
        else:
            # 如果指定了区域ID，检查该区域是否属于该护林员负责
            if region_id not in user_regions:
                # 如果指定区域不属于该护林员负责，返回空列表
                return jsonify([])
    
    warnings = db_instance.get_warnings_by_area(region_id)
    return jsonify(warnings)

@app.route('/api/disaster_warning/publish_warning', methods=['POST'])
def publish_warning():
    if 'user' not in session:
        return jsonify({'error': '未登录', 'success': False}), 401
    
    user = session['user']
    role = user['Role']
    user_id = user['UserID']
    
    # 解析请求数据
    data = request.get_json()
    warning_type = data.get('warning_type')
    warning_level = data.get('warning_level')
    warning_content = data.get('warning_content')
    region_id = data.get('affected_area')
    
    # 验证必填字段
    if not warning_type or not warning_level or not warning_content or not region_id:
        return jsonify({'error': '缺少必填字段', 'success': False}), 400
    
    # 验证区域护林员只能发布自己负责区域的预警
    if role == '区域护林员':
        # 查询该护林员负责的所有区域
        sql = "SELECT RegionID FROM Region WHERE ManagerID = ?"
        regions = db_instance.db.fetch_all(sql, (user_id,))
        user_regions = [r[0] for r in regions]
        
        # 检查该区域是否属于该护林员负责
        if region_id not in user_regions:
            return jsonify({'error': '只能发布自己负责区域的预警', 'success': False}), 403
    
    try:
        print(f"开始发布预警，类型: {warning_type}, 级别: {warning_level}, 区域: {region_id}")
        
        # 获取或创建预警规则
        # 首先尝试获取现有的预警规则
        sql = "SELECT RuleID FROM WarningRule WHERE WarningType = ? AND WarningLevel = ?"
        rule = db_instance.db.fetch_one(sql, (warning_type, warning_level))
        rule_id = rule[0] if rule else None
        
        print(f"获取到的规则ID: {rule_id}")
        
        if not rule_id:
            # 如果没有对应的规则，创建一个新的
            trigger_condition = f"手动发布的{warning_type}预警，级别{warning_level}"
            is_active = 0  # 手动创建的规则默认不激活
            rule_id = db_instance.add_warning_rule(warning_type, trigger_condition, warning_level, is_active)
            print(f"创建新规则，ID: {rule_id}")
        
        # 调用数据库方法发布预警
        trigger_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"准备添加预警记录，规则ID: {rule_id}, 时间: {trigger_time}")
        
        # 使用封装好的方法添加预警记录
        warning_id = db_instance.add_warning_record(rule_id, region_id, trigger_time, warning_content)
        print(f"添加预警记录返回ID: {warning_id}")
        
        if warning_id:
            print(f"预警记录添加成功，ID: {warning_id}")
            return jsonify({'success': True, 'message': '预警信息发布成功', 'warning_id': warning_id})
        else:
            print("预警记录添加失败")
            return jsonify({'error': '预警发布失败，无法创建预警记录', 'success': False}), 500
    except Exception as e:
        print(f"发布预警失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'预警发布失败: {str(e)}', 'success': False}), 500

@app.route('/api/disaster_warning/update_warning_status', methods=['POST'])
def update_warning_status():
    if 'user' not in session:
        return jsonify({'error': '未登录', 'success': False}), 401
    
    data = request.get_json()
    try:
        warning_id = data.get('warning_id')
        status = data.get('status')
        handler_id = data.get('handler_id')
        handle_result = data.get('handle_result')
        
        if not warning_id or not status or not handler_id:
            return jsonify({'error': '缺少必要参数', 'success': False}), 400
        
        # 对于区域护林员，只能处理自己负责区域的预警
        user = session['user']
        role = user['Role']
        user_id = user['UserID']
        if role == '区域护林员':
            # 检查该预警是否属于该护林员负责的区域
            sql = """
            SELECT w.RegionID FROM WarningRecord w 
            INNER JOIN Region r ON w.RegionID = r.RegionID 
            WHERE w.WarningID = ? AND r.ManagerID = ?
            """
            result = db_instance.db.fetch_one(sql, (warning_id, user_id))
            if not result:
                return jsonify({'error': '没有权限处理该预警', 'success': False}), 403
        
        success = db_instance.update_warning_status(warning_id, status, handler_id, handle_result)
        return jsonify({'success': success})
    except Exception as e:
        print(f"更新预警状态失败: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

# 资源管理API
@app.route('/api/resource_management/get_resources')
def get_resources():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = session['user']
    role = user['Role']
    
    # 检查权限：只有管理员、系统管理员、数据管理员和监管人员可以访问资源管理API
    if role not in ['管理员', '系统管理员', '数据管理员', '监管人员']:
        return jsonify({'error': '没有权限访问该API', 'success': False}), 403
    
    user_id = user['UserID']
    region_id = request.args.get('region_id')
    
    # 对于区域护林员，只能查看自己负责的区域资源（已被上面的权限检查拒绝）
    if role == '区域护林员':
        # 查询该护林员负责的所有区域
        sql = "SELECT RegionID FROM Region WHERE ManagerID = ?"
        regions = db_instance.db.fetch_all(sql, (user_id,))
        user_regions = [r[0] for r in regions]
        
        if not regions:
            # 如果没有负责区域，返回空列表
            return jsonify([])
        
        if not region_id:
            # 如果没有指定区域ID，返回所有负责区域的资源
            all_resources = []
            for region in user_regions:
                resources = db_instance.get_forest_resources(region)
                all_resources.extend(resources)
            return jsonify(all_resources)
        else:
            # 如果指定了区域ID，检查该区域是否属于该护林员负责
            if region_id not in user_regions:
                # 如果指定区域不属于该护林员负责，返回空列表
                return jsonify([])
            # 指定了有效的区域ID，返回该区域的资源
            resources = db_instance.get_forest_resources(region_id)
            return jsonify(resources)
    
    resources = db_instance.get_forest_resources(region_id)
    return jsonify(resources)

@app.route('/api/resource_management/get_resource_changes')
def get_resource_changes():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = session['user']
    role = user['Role']
    
    # 检查权限：只有管理员、系统管理员、数据管理员和监管人员可以访问资源管理API
    if role not in ['管理员', '系统管理员', '数据管理员', '监管人员']:
        return jsonify({'error': '没有权限访问该API', 'success': False}), 403
    
    resource_id = request.args.get('resource_id')
    
    user = session['user']
    role = user['Role']
    user_id = user['UserID']
    
    # 对于区域护林员，只能查看自己负责区域的资源变动（已被上面的权限检查拒绝）
    if role == '区域护林员':
        if not resource_id:
            # 如果没有指定资源ID，返回所有负责区域的资源变动记录
            # 查询该护林员负责的所有区域
            regions_sql = "SELECT RegionID FROM Region WHERE ManagerID = ?"
            regions = db_instance.db.fetch_all(regions_sql, (user_id,))
            user_regions = [r[0] for r in regions]
            
            if not user_regions:
                return jsonify([])
            
            # 查询这些区域下的所有资源
            resources_sql = "SELECT ResourceID FROM ForestResource WHERE RegionID IN (" + ",".join(["?"] * len(user_regions)) + ")"
            resources = db_instance.db.fetch_all(resources_sql, tuple(user_regions))
            resource_ids = [r[0] for r in resources]
            
            if not resource_ids:
                return jsonify([])
            
            # 查询这些资源的所有变动记录
            all_records = []
            for res_id in resource_ids:
                records = db_instance.get_resource_change_records(res_id)
                all_records.extend(records)
            return jsonify(all_records)
        else:
            # 检查该资源所属区域是否属于该护林员负责
            sql = """
            SELECT r.RegionID FROM ForestResource f
            JOIN Region r ON f.RegionID = r.RegionID 
            WHERE f.ResourceID = ? AND r.ManagerID = ?
            """
            result = db_instance.db.fetch_one(sql, (resource_id, user_id))
            if not result:
                return jsonify([])
    
    records = db_instance.get_resource_change_records(resource_id)
    return jsonify(records)

@app.route('/api/resource_management/get_regions')
def get_regions():
    # 检查登录状态
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = session['user']
    role = user['Role']
    
    # 检查权限：只有管理员、系统管理员、数据管理员和监管人员可以访问资源管理API
    if role not in ['管理员', '系统管理员', '数据管理员', '监管人员']:
        return jsonify({'error': '没有权限访问该API', 'success': False}), 403
    
    user_id = user['UserID']
    
    try:
        # 根据用户角色获取区域列表
        if role == '区域护林员':
            # 区域护林员只能获取自己负责的区域（已被上面的权限检查拒绝）
            sql = "SELECT RegionID, RegionName FROM Region WHERE ManagerID = ? ORDER BY RegionID"
            params = (user_id,)
        else:
            # 其他角色可以获取所有区域
            sql = "SELECT RegionID, RegionName FROM Region ORDER BY RegionID"
            params = None
        
        # 使用新的游标执行查询，避免共享游标导致的问题
        cursor = db_instance.db.connection.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        # 逐行获取数据，避免一次性加载所有数据
        regions_list = []
        row = cursor.fetchone()
        while row:
            # 确保行数据有足够的元素
            if len(row) >= 2:
                regions_list.append({
                    'RegionID': row[0],
                    'RegionName': row[1]
                })
            row = cursor.fetchone()
        
        return jsonify(regions_list)
    except Exception as e:
        print(f"获取区域列表失败: {e}")
        return jsonify([])

@app.route('/api/resource_management/add_resource', methods=['POST'])
def add_resource():
    if 'user' not in session:
        return jsonify({'error': '未登录', 'success': False}), 401
    
    user = session['user']
    role = user['Role']
    
    # 检查权限：只有管理员、系统管理员、数据管理员和监管人员可以访问资源管理API
    if role not in ['管理员', '系统管理员', '数据管理员', '监管人员']:
        return jsonify({'error': '没有权限访问该API', 'success': False}), 403
    
    user_id = user['UserID']
    
    data = request.get_json()
    try:
        region_id = data.get('region_id')
        resource_type = data.get('resource_type')
        tree_species = data.get('tree_species')
        coverage_area = data.get('coverage_area')
        growth_status = data.get('growth_status')
        updated_by = data.get('updated_by')
        
        if not region_id or not resource_type or not updated_by:
            return jsonify({'error': '缺少必要参数', 'success': False}), 400
        
        # 对于区域护林员，只能添加自己负责区域的资源（已被上面的权限检查拒绝）
        if role == '区域护林员':
            # 检查该区域是否属于该护林员负责
            sql = "SELECT COUNT(*) FROM Region WHERE RegionID = ? AND ManagerID = ?"
            result = db_instance.db.fetch_one(sql, (region_id, user_id))
            if result[0] == 0:
                return jsonify({'error': '没有权限在该区域添加资源', 'success': False}), 403
        
        resource_id = db_instance.add_forest_resource(region_id, resource_type, coverage_area, tree_species, growth_status, updated_by)
        if resource_id:
            return jsonify({'success': True, 'resource_id': resource_id})
        else:
            return jsonify({'success': False, 'error': '添加资源失败'})
    except Exception as e:
        print(f"添加资源失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/resource_management/update_resource', methods=['PUT'])
def update_resource():
    if 'user' not in session:
        return jsonify({'error': '未登录', 'success': False}), 401
    
    user = session['user']
    role = user['Role']
    
    # 检查权限：只有管理员、系统管理员、数据管理员和监管人员可以访问资源管理API
    if role not in ['管理员', '系统管理员', '数据管理员', '监管人员']:
        return jsonify({'error': '没有权限访问该API', 'success': False}), 403
    
    user_id = user['UserID']
    
    data = request.get_json()
    try:
        resource_id = data.get('resource_id')
        coverage_area = data.get('coverage_area')
        tree_species = data.get('tree_species')
        growth_status = data.get('growth_status')
        updated_by = data.get('updated_by')
        
        if not resource_id:
            return jsonify({'error': '缺少资源ID', 'success': False}), 400
        
        # 对于区域护林员，只能更新自己负责区域的资源（已被上面的权限检查拒绝）
        if role == '区域护林员':
            # 检查该资源所属区域是否属于该护林员负责
            sql = """
            SELECT r.RegionID FROM ForestResource f
            JOIN Region r ON f.RegionID = r.RegionID
            WHERE f.ResourceID = ? AND r.ManagerID = ?
            """
            result = db_instance.db.fetch_one(sql, (resource_id, user_id))
            if not result:
                return jsonify({'error': '没有权限更新该资源', 'success': False}), 403
        
        success = db_instance.update_forest_resource(resource_id, coverage_area, tree_species, growth_status, updated_by)
        return jsonify({'success': success})
    except Exception as e:
        print(f"更新资源失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 设备管理API
@app.route('/api/equipment_management/add_device', methods=['POST'])
def add_device():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = session['user']
    role = user['Role']
    user_id = user['UserID']
    
    # 检查权限：只有系统管理员、管理员、区域护林员可以访问设备管理API
    if role not in ['管理员', '系统管理员', '区域护林员', '监管人员']:
        return jsonify({'error': '没有权限访问该API'}), 403
    
    # 获取请求数据
    device_data = request.get_json()
    
    # 对于区域护林员，验证安装位置是否是其负责的区域
    if role == '区域护林员':
        # 查询该护林员负责的所有区域
        sql = "SELECT RegionID FROM Region WHERE ManagerID = ?"
        regions = db_instance.db.fetch_all(sql, (user_id,))
        user_regions = [r[0] for r in regions]
        
        if device_data.get('installation_location') not in user_regions:
            return jsonify({'success': False, 'error': '只能在自己负责的区域安装设备'}), 403
    
    # 调用业务层添加设备
    try:
        device_id = db_instance.equipment_module.add_device_archive(
            device_name=device_data.get('equipment_name'),
            device_type=device_data.get('equipment_type'),
            model_specification='默认型号',  # 前端表单未提供，使用默认值
            purchase_time=datetime.now(),  # 使用当前时间作为采购时间
            region_id=device_data.get('installation_location'),
            installer_id=user_id,  # 使用当前用户ID作为安装人员ID
            warranty_period='3年'  # 前端表单未提供，使用默认值
        )
        
        if device_id:
            return jsonify({'success': True, 'device_id': device_id})
        else:
            return jsonify({'success': False, 'error': '添加设备失败'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/equipment_management/get_devices')
def get_devices():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = session['user']
    role = user['Role']
    user_id = user['UserID']
    
    # 检查权限：只有系统管理员、管理员、区域护林员和监管人员可以访问设备管理API
    if role not in ['管理员', '系统管理员', '区域护林员', '监管人员']:
        return jsonify({'error': '没有权限访问该API'}), 403
    
    region_id = request.args.get('region_id')
    device_type = request.args.get('device_type')
    
    # 对于区域护林员，只能查看自己负责区域的设备
    if role == '区域护林员':
        # 查询该护林员负责的所有区域
        sql = "SELECT RegionID FROM Region WHERE ManagerID = ?"
        regions = db_instance.db.fetch_all(sql, (user_id,))
        user_regions = [r[0] for r in regions]
        
        if not user_regions:
            # 如果没有负责区域，返回空列表
            return jsonify([])
        
        # 获取所有负责区域的设备
        all_devices = []
        for r_id in user_regions:
            devices = db_instance.get_device_archives(r_id, device_type)
            all_devices.extend(devices)
        
        return jsonify(all_devices)
    else:
        # 非区域护林员，可以查看所有设备或指定区域设备
        devices = db_instance.get_device_archives(region_id, device_type)
        return jsonify(devices)

@app.route('/api/equipment_management/get_device_status')
def get_device_status():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = session['user']
    role = user['Role']
    user_id = user['UserID']
    
    # 检查权限：只有系统管理员、管理员、区域护林员和监管人员可以访问设备状态API
    if role not in ['管理员', '系统管理员', '区域护林员', '监管人员']:
        return jsonify({'error': '没有权限访问该API'}), 403
    
    device_id = request.args.get('device_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    if not device_id:
        return jsonify({'error': '缺少设备ID'}), 400
    
    # 对于区域护林员，只能查看自己负责区域设备的状态
    if role == '区域护林员':
        # 检查该设备是否属于该护林员负责的区域
        sql = """
        SELECT d.RegionID FROM DeviceArchive d 
        INNER JOIN Region r ON d.RegionID = r.RegionID 
        WHERE d.DeviceID = ? AND r.ManagerID = ?
        """
        result = db_instance.db.fetch_one(sql, (device_id, user_id))
        if not result:
            return jsonify({'error': '没有权限查看该设备的状态', 'success': False}), 403
    
    status = db_instance.get_device_status(device_id, start_time, end_time)
    return jsonify(status)

# 设备巡检记录API
@app.route('/api/equipment_management/add_equipment_inspection', methods=['POST'])
def add_equipment_inspection():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = session['user']
    role = user['Role']
    user_id = user['UserID']
    
    # 检查权限：只有系统管理员、管理员、区域护林员和监管人员可以访问设备巡检API
    if role not in ['管理员', '系统管理员', '区域护林员', '监管人员']:
        return jsonify({'error': '没有权限访问该API'}), 403
    
    # 获取请求数据
    inspection_data = request.get_json()
    
    device_id = inspection_data.get('device_id')
    inspection_time = inspection_data.get('inspection_time')
    inspector_id = inspection_data.get('inspector_id', user_id)  # 默认使用当前用户ID
    maintenance_type = inspection_data.get('maintenance_type')
    inspection_result = inspection_data.get('inspection_result')
    
    if not device_id or not maintenance_type or not inspection_result:
        return jsonify({'error': '缺少必要参数', 'success': False}), 400
    
    # 对于区域护林员，只能为自己负责区域的设备添加巡检记录
    if role == '区域护林员':
        # 检查该设备是否属于该护林员负责的区域
        sql = """
        SELECT d.RegionID FROM DeviceArchive d 
        INNER JOIN Region r ON d.RegionID = r.RegionID 
        WHERE d.DeviceID = ? AND r.ManagerID = ?
        """
        result = db_instance.db.fetch_one(sql, (device_id, user_id))
        if not result:
            return jsonify({'error': '没有权限为该设备添加巡检记录', 'success': False}), 403
    
    # 调用业务层添加巡检记录
    try:
        inspection_id = db_instance.add_equipment_inspection(
            device_id=device_id,
            inspection_time=inspection_time if inspection_time else datetime.now(),
            inspector_id=inspector_id,
            maintenance_type=maintenance_type,
            inspection_result=inspection_result,
            problem_description=inspection_data.get('problem_description'),
            maintenance_content=inspection_data.get('maintenance_content'),
            maintenance_result=inspection_data.get('maintenance_result')
        )
        
        if inspection_id:
            return jsonify({'success': True, 'inspection_id': inspection_id})
        else:
            return jsonify({'success': False, 'error': '添加巡检记录失败'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/equipment_management/get_equipment_inspections')
def get_equipment_inspections():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    user = session['user']
    role = user['Role']
    user_id = user['UserID']
    
    # 检查权限：只有系统管理员、管理员、区域护林员和监管人员可以访问设备巡检API
    if role not in ['管理员', '系统管理员', '区域护林员', '监管人员']:
        return jsonify({'error': '没有权限访问该API'}), 403
    
    device_id = request.args.get('device_id')
    inspector_id = request.args.get('inspector_id')
    
    # 对于区域护林员，只能查看自己负责区域设备的巡检记录
    if role == '区域护林员':
        inspections = []
        # 获取该护林员负责的所有设备
        sql = """
        SELECT d.DeviceID FROM DeviceArchive d 
        INNER JOIN Region r ON d.RegionID = r.RegionID 
        WHERE r.ManagerID = ?
        """
        devices = db_instance.db.fetch_all(sql, (user_id,))
        device_ids = [d[0] for d in devices]
        
        if not device_ids:
            return jsonify([])
        
        # 如果指定了设备ID，检查是否在该护林员负责的设备列表中
        if device_id:
            if device_id not in device_ids:
                return jsonify({'error': '没有权限查看该设备的巡检记录', 'success': False}), 403
            # 只获取该设备的巡检记录
            inspections = db_instance.get_equipment_inspections(device_id=device_id, inspector_id=inspector_id)
        else:
            # 获取所有负责设备的巡检记录
            for d_id in device_ids:
                device_inspections = db_instance.get_equipment_inspections(device_id=d_id, inspector_id=inspector_id)
                inspections.extend(device_inspections)
        
        return jsonify(inspections)
    else:
        # 非区域护林员，可以查看所有巡检记录
        inspections = db_instance.get_equipment_inspections(device_id=device_id, inspector_id=inspector_id)
        return jsonify(inspections)

# 统计分析API
@app.route('/api/statistical_analysis/get_report_templates')
def get_report_templates():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    # 检查权限：只有系统管理员、管理员、数据管理员和监管人员可以访问报表模板API
    role = session['user']['Role']
    if role not in ['管理员', '系统管理员', '数据管理员', '监管人员']:
        return jsonify({'error': '没有权限访问该API'}), 403
    
    report_type = request.args.get('report_type')
    templates = db_instance.get_report_templates(report_type)
    return jsonify(templates)

# 反馈API - 公众用户可以提交反馈
@app.route('/api/feedback/submit', methods=['POST'])
def submit_feedback():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    data = request.get_json()
    try:
        feedback_type = data.get('feedback-type')
        region_id = data.get('feedback-region')
        description = data.get('feedback-description')
        contact = data.get('feedback-contact')
        
        if not feedback_type or not region_id or not description or not contact:
            return jsonify({'error': '缺少必要参数', 'success': False}), 400
        
        # 调用数据库方法添加反馈
        feedback_id = db_instance.add_feedback(feedback_type, region_id, description, contact)
        if feedback_id:
            return jsonify({'success': True, 'feedback_id': feedback_id, 'message': '反馈提交成功！感谢您的参与。'})
        else:
            return jsonify({'error': '添加反馈失败', 'success': False}), 500
    except Exception as e:
        print(f"提交反馈失败: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

# 反馈API - 获取反馈列表（仅限管理员和数据管理员）
@app.route('/api/feedback/get_feedbacks')
def get_feedbacks():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    # 检查权限：只有管理员、系统管理员和数据管理员可以访问反馈列表
    user = session['user']
    role = user['Role']
    user_id = user['UserID']
    
    if role not in ['管理员', '系统管理员', '数据管理员', '监管人员']:
        return jsonify({'error': '没有权限访问该API'}), 403
    
    status = request.args.get('status')
    region_id = request.args.get('region_id')
    
    feedbacks = db_instance.get_feedbacks(status, region_id)
    return jsonify(feedbacks)

# 反馈API - 更新反馈状态（处理反馈）
@app.route('/api/feedback/update_status', methods=['POST'])
def update_feedback_status():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    # 系统管理员、管理员、数据管理员和监管人员都可以访问反馈管理API
    role = session['user']['Role']
    if role not in ['管理员', '系统管理员', '数据管理员', '监管人员']:
        return jsonify({'error': '没有权限访问该API'}), 403
    
    data = request.get_json()
    try:
        feedback_id = data.get('feedback_id')
        status = data.get('status')
        handle_result = data.get('handle_result')
        handler_id = session['user']['UserID']
        
        if not feedback_id or not status:
            return jsonify({'error': '缺少必要参数', 'success': False}), 400
        
        # 调用数据库方法更新反馈状态
        success = db_instance.update_feedback_status(feedback_id, status, handler_id, handle_result)
        if success:
            return jsonify({'success': True, 'message': '反馈状态更新成功！'})
        else:
            return jsonify({'error': '更新反馈状态失败', 'success': False}), 500
    except Exception as e:
        print(f"更新反馈状态失败: {e}")
        return jsonify({'error': str(e), 'success': False}), 500

# 用户管理API
@app.route('/api/user_management/get_users')
def get_users():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    # 检查权限：只有系统管理员和管理员可以访问用户管理API
    role = session['user']['Role']
    if role not in ['管理员', '系统管理员']:
        return jsonify({'error': '没有权限访问该API'}), 403
    
    # 获取查询参数
    role_param = request.args.get('role')
    
    # 获取用户列表
    users = db_instance.get_users(role_param)
    return jsonify(users)

@app.route('/api/statistical_analysis/get_generated_reports')
def get_generated_reports():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    # 检查权限：只有系统管理员、管理员、数据管理员和监管人员可以访问生成的报表API
    role = session['user']['Role']
    if role not in ['管理员', '系统管理员', '数据管理员', '监管人员']:
        return jsonify({'error': '没有权限访问该API'}), 403
    
    region_id = request.args.get('region_id')
    report_type = request.args.get('report_type')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    reports = db_instance.get_generated_reports(region_id, report_type, start_time, end_time)
    return jsonify(reports)

# 启动应用
if __name__ == '__main__':
    init_db()
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    finally:
        close_db()
