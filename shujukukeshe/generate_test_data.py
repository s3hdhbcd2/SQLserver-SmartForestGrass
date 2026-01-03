import pyodbc
import datetime
import random

# 数据库连接参数
server = '.\SQLEXPRESS'
database = 'SmartForestGrass'
trusted_connection = 'yes'
driver = '{ODBC Driver 17 for SQL Server}'

def connect_db():
    """
    连接到数据库
    :return: 数据库连接对象
    """
    try:
        conn = pyodbc.connect(
            f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection={trusted_connection}'
        )
        return conn
    except Exception as e:
        print(f"连接数据库失败: {e}")
        return None

def execute_sql_file(conn, file_path):
    """
    执行SQL文件
    :param conn: 数据库连接对象
    :param file_path: SQL文件路径
    :return: 是否执行成功
    """
    try:
        cursor = conn.cursor()
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 按GO关键字分割SQL语句
        sql_batches = sql_content.split('GO\n')
        
        for batch in sql_batches:
            batch = batch.strip()
            if batch:
                cursor.execute(batch)
        
        conn.commit()
        print(f"✅ 成功执行SQL文件: {file_path}")
        return True
    except Exception as e:
        print(f"❌ 执行SQL文件失败 {file_path}: {e}")
        return False

def generate_resource_change_test_data(conn, count=10):
    """
    生成资源变动记录测试数据
    :param conn: 数据库连接对象
    :param count: 生成记录数量
    """
    try:
        cursor = conn.cursor()
        
        # 先获取现有的资源ID和用户ID
        cursor.execute("SELECT ResourceID FROM ForestResource")
        resource_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT UserID FROM [User]")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        if not resource_ids or not user_ids:
            print("⚠️  缺少基础数据，无法生成资源变动记录测试数据")
            return False
        
        # 生成测试数据
        change_types = ['新增', '更新', '删除']
        audit_statuses = ['待审核', '通过', '拒绝']
        
        print(f"\n=== 生成 {count} 条资源变动记录测试数据 ===")
        
        for i in range(count):
            # 生成唯一的ChangeID
            change_id = f"CHG{str(i+1).zfill(4)}"
            
            # 随机选择资源ID和用户ID
            resource_id = random.choice(resource_ids)
            operator_id = random.choice(user_ids)
            
            # 随机生成变动类型
            change_type = random.choice(change_types)
            change_reason = f"{change_type}资源测试数据"
            
            # 随机生成变动时间（过去30天内）
            days_ago = random.randint(0, 30)
            change_time = datetime.datetime.now() - datetime.timedelta(days=days_ago)
            
            # 随机生成审核状态
            audit_status = random.choice(audit_statuses)
            
            if audit_status in ['通过', '拒绝']:
                # 已审核的记录
                auditor_id = random.choice(user_ids)
                audit_time = change_time + datetime.timedelta(hours=random.randint(1, 48))
                audit_comments = f"{audit_status}测试审核"
            else:
                # 待审核的记录
                auditor_id = None
                audit_time = None
                audit_comments = None
            
            # 插入数据
            sql = """
            INSERT INTO ResourceChangeRecord (
                ChangeID, ResourceID, ChangeType, ChangeReason, ChangeTime, OperatorID, 
                AuditStatus, AuditorID, AuditTime, AuditComments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                change_id, resource_id, change_type, change_reason, change_time,
                operator_id, audit_status, auditor_id, audit_time, audit_comments
            )
            
            cursor.execute(sql, params)
        
        conn.commit()
        print(f"✅ 成功生成 {count} 条资源变动记录测试数据")
        return True
    except Exception as e:
        print(f"❌ 生成资源变动记录测试数据失败: {e}")
        return False

def generate_equipment_inspection_test_data(conn, count=10):
    """
    生成设备巡检记录测试数据
    :param conn: 数据库连接对象
    :param count: 生成记录数量
    """
    try:
        cursor = conn.cursor()
        
        # 先获取现有的设备ID和用户ID
        cursor.execute("SELECT DeviceID FROM DeviceArchive")
        device_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT UserID FROM [User]")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        if not device_ids or not user_ids:
            print("⚠️  缺少基础数据，无法生成设备巡检记录测试数据")
            return False
        
        # 生成测试数据
        maintenance_types = ['巡检', '维护', '维修', '更换']
        inspection_results = ['正常', '异常', '故障']
        audit_statuses = ['待审核', '通过', '拒绝']
        
        print(f"\n=== 生成 {count} 条设备巡检记录测试数据 ===")
        
        for i in range(count):
            # 生成唯一的InspectionID
            inspection_id = f"INSP{str(i+1).zfill(4)}"
            
            # 随机选择设备ID和用户ID
            device_id = random.choice(device_ids)
            inspector_id = random.choice(user_ids)
            
            # 随机生成巡检时间（过去30天内）
            days_ago = random.randint(0, 30)
            inspection_time = datetime.datetime.now() - datetime.timedelta(days=days_ago)
            
            # 随机生成维护类型和结果
            maintenance_type = random.choice(maintenance_types)
            inspection_result = random.choice(inspection_results)
            
            # 根据结果生成问题描述和维护内容
            if inspection_result == '正常':
                problem_description = None
                maintenance_content = f"常规{maintenance_type}，设备运行正常"
                maintenance_result = "正常"
            else:
                problem_description = f"设备{inspection_result}，需要{maintenance_type}"
                maintenance_content = f"进行了{maintenance_type}，处理了{inspection_result}问题"
                maintenance_result = "已修复"
            
            # 随机生成审核状态
            audit_status = random.choice(audit_statuses)
            
            if audit_status in ['通过', '拒绝']:
                # 已审核的记录
                auditor_id = random.choice(user_ids)
                audit_time = inspection_time + datetime.timedelta(hours=random.randint(1, 48))
                audit_comments = f"{audit_status}测试审核"
            else:
                # 待审核的记录
                auditor_id = None
                audit_time = None
                audit_comments = None
            
            # 插入数据
            sql = """
            INSERT INTO EquipmentInspection (
                InspectionID, DeviceID, InspectionTime, InspectorID, MaintenanceType, InspectionResult, 
                ProblemDescription, MaintenanceContent, MaintenanceResult, AuditStatus, 
                AuditorID, AuditTime, AuditComments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                inspection_id, device_id, inspection_time, inspector_id, maintenance_type, inspection_result,
                problem_description, maintenance_content, maintenance_result, audit_status,
                auditor_id, audit_time, audit_comments
            )
            
            cursor.execute(sql, params)
        
        conn.commit()
        print(f"✅ 成功生成 {count} 条设备巡检记录测试数据")
        return True
    except Exception as e:
        print(f"❌ 生成设备巡检记录测试数据失败: {e}")
        return False

def generate_maintenance_record_test_data(conn, count=10):
    """
    生成维护记录测试数据
    :param conn: 数据库连接对象
    :param count: 生成记录数量
    """
    try:
        cursor = conn.cursor()
        
        # 先获取现有的设备ID和用户ID
        cursor.execute("SELECT DeviceID FROM DeviceArchive")
        device_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT UserID FROM [User]")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        if not device_ids or not user_ids:
            print("⚠️  缺少基础数据，无法生成维护记录测试数据")
            return False
        
        # 生成测试数据
        maintenance_types = ['日常维护', '故障维修', '设备更换', '软件更新']
        audit_statuses = ['待审核', '通过', '拒绝']
        
        print(f"\n=== 生成 {count} 条维护记录测试数据 ===")
        
        for i in range(count):
            # 生成唯一的MaintenanceID
            maintenance_id = f"MNT{str(i+1).zfill(4)}"
            
            # 随机选择设备ID和用户ID
            device_id = random.choice(device_ids)
            maintainer_id = random.choice(user_ids)
            
            # 随机生成维护时间（过去30天内）
            days_ago = random.randint(0, 30)
            maintenance_time = datetime.datetime.now() - datetime.timedelta(days=days_ago)
            
            # 随机生成维护类型
            maintenance_type = random.choice(maintenance_types)
            maintenance_content = f"{maintenance_type}测试数据"
            maintenance_result = "已完成"
            
            # 随机生成审核状态
            audit_status = random.choice(audit_statuses)
            
            if audit_status in ['通过', '拒绝']:
                # 已审核的记录
                auditor_id = random.choice(user_ids)
                audit_time = maintenance_time + datetime.timedelta(hours=random.randint(1, 48))
                audit_comments = f"{audit_status}测试审核"
            else:
                # 待审核的记录
                auditor_id = None
                audit_time = None
                audit_comments = None
            
            # 插入数据
            sql = """
            INSERT INTO MaintenanceRecord (
                MaintenanceID, DeviceID, MaintenanceType, MaintenanceTime, MaintainerID, 
                MaintenanceContent, MaintenanceResult, AuditStatus, AuditorID, AuditTime, AuditComments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                maintenance_id, device_id, maintenance_type, maintenance_time, maintainer_id,
                maintenance_content, maintenance_result, audit_status, auditor_id, audit_time, audit_comments
            )
            
            cursor.execute(sql, params)
        
        conn.commit()
        print(f"✅ 成功生成 {count} 条维护记录测试数据")
        return True
    except Exception as e:
        print(f"❌ 生成维护记录测试数据失败: {e}")
        return False

def main():
    """
    主函数，执行数据库更新和测试数据生成
    """
    print("=== 开始更新数据库并生成测试数据 ===")
    
    # 1. 连接数据库
    conn = connect_db()
    if not conn:
        return
    
    try:
        # 2. 执行SQL文件更新表结构
        sql_files = [
            'sql_files/resource_management.sql',
            'sql_files/equipment_management.sql'
        ]
        
        for sql_file in sql_files:
            if not execute_sql_file(conn, sql_file):
                print(f"❌ 执行SQL文件 {sql_file} 失败，程序退出")
                return
        
        # 3. 生成测试数据
        generate_resource_change_test_data(conn, 10)
        generate_equipment_inspection_test_data(conn, 10)
        generate_maintenance_record_test_data(conn, 10)
        
        print("\n=== 数据库更新和测试数据生成完成 ===")
    finally:
        # 4. 关闭数据库连接
        conn.close()

if __name__ == "__main__":
    main()