from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from smart_forest_grass_business import DatabaseConnection, DisasterWarningDatabase
import json

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
    return redirect(url_for('login'))

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
            {'code': '5', 'name': '统计分析', 'icon': '📊', 'href': '/statistical_analysis'}
        ],
        '区域护林员': [
            {'code': '1', 'name': '环境监测', 'icon': '🌡️', 'href': '/environmental_monitoring'},
            {'code': '2', 'name': '灾害预警', 'icon': '⚠️', 'href': '/disaster_warning'},
            {'code': '3', 'name': '资源管理', 'icon': '🌲', 'href': '/resource_management'},
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
            {'code': '5', 'name': '统计分析', 'icon': '📊', 'href': '/statistical_analysis'}
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
    
    # 检查权限：只有管理员、系统管理员、数据管理员、区域护林员和监管人员可以访问资源管理
    role = session['user']['Role']
    if role not in ['管理员', '系统管理员', '数据管理员', '区域护林员', '监管人员']:
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

# 环境监测API
@app.route('/api/environmental_monitoring/get_sensors')
def get_sensors():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    region_id = request.args.get('region_id')
    sensors = db_instance.get_sensors(region_id)
    return jsonify(sensors)

@app.route('/api/environmental_monitoring/get_monitoring_data')
def get_monitoring_data():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    region_id = request.args.get('region_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    # 只检查start_time和end_time是否存在，允许region_id为空字符串表示全部区域
    if not start_time or not end_time:
        return jsonify({'error': '缺少必要参数'}), 400
    
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
    
    region_id = request.args.get('region_id')
    warnings = db_instance.get_warnings_by_area(region_id)
    return jsonify(warnings)

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
    
    region_id = request.args.get('region_id')
    resources = db_instance.get_forest_resources(region_id)
    return jsonify(resources)

@app.route('/api/resource_management/get_resource_changes')
def get_resource_changes():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    resource_id = request.args.get('resource_id')
    records = db_instance.get_resource_change_records(resource_id)
    return jsonify(records)

@app.route('/api/resource_management/get_regions')
def get_regions():
    # 获取所有区域信息
    try:
        sql = "SELECT RegionID, RegionName FROM Region ORDER BY RegionID"
        
        # 使用新的游标执行查询，避免共享游标导致的问题
        cursor = db_instance.db.connection.cursor()
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
    
    data = request.get_json()
    try:
        resource_id = data.get('resource_id')
        coverage_area = data.get('coverage_area')
        tree_species = data.get('tree_species')
        growth_status = data.get('growth_status')
        updated_by = data.get('updated_by')
        
        if not resource_id:
            return jsonify({'error': '缺少资源ID', 'success': False}), 400
        
        success = db_instance.update_forest_resource(resource_id, coverage_area, tree_species, growth_status, updated_by)
        return jsonify({'success': success})
    except Exception as e:
        print(f"更新资源失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 设备管理API
@app.route('/api/equipment_management/get_devices')
def get_devices():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    # 检查权限：只有系统管理员、管理员、区域护林员和监管人员可以访问设备管理API
    role = session['user']['Role']
    if role not in ['管理员', '系统管理员', '区域护林员', '监管人员']:
        return jsonify({'error': '没有权限访问该API'}), 403
    
    region_id = request.args.get('region_id')
    device_type = request.args.get('device_type')
    devices = db_instance.get_device_archives(region_id, device_type)
    return jsonify(devices)

@app.route('/api/equipment_management/get_device_status')
def get_device_status():
    if 'user' not in session:
        return jsonify({'error': '未登录'}), 401
    
    # 检查权限：只有系统管理员、管理员、区域护林员和监管人员可以访问设备状态API
    role = session['user']['Role']
    if role not in ['管理员', '系统管理员', '区域护林员', '监管人员']:
        return jsonify({'error': '没有权限访问该API'}), 403
    
    device_id = request.args.get('device_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    if not device_id:
        return jsonify({'error': '缺少设备ID'}), 400
    
    status = db_instance.get_device_status(device_id, start_time, end_time)
    return jsonify(status)

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
