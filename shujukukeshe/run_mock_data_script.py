import pyodbc

# 数据库连接参数
conn_str = (
    r'DRIVER={SQL Server};' +
    r'SERVER=.;' +
    r'DATABASE=SmartForestGrass;' +
    r'UID=sa;' +
    r'PWD=123456;' +
    r'Trusted_Connection=no;'
)

# 执行SQL脚本
def execute_sql_script(script_path):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("成功连接到SQL Server数据库")
    
    try:
        # 读取SQL脚本文件
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 分割SQL脚本为多个语句
        sql_statements = sql_script.split('GO')
        
        for statement in sql_statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                print(f"执行SQL语句: {statement[:100]}...")
                cursor.execute(statement)
                conn.commit()
        
        print('SQL脚本执行成功！')
        return True
        
    except Exception as e:
        print(f'执行SQL脚本失败：{e}')
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# 只执行设备档案相关的SQL语句
def execute_device_archive_script(script_path):
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("成功连接到SQL Server数据库")
    
    try:
        # 读取SQL脚本文件
        with open(script_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 找到设备档案插入部分
        start_marker = '-- 2.5 插入设备档案表(DeviceArchive)数据（20条）'
        end_marker = '-- 2.6 插入林草资源表(ForestResource)数据（20条）'
        
        start_idx = sql_script.find(start_marker)
        end_idx = sql_script.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            print("未找到设备档案插入部分")
            return False
        
        # 提取设备档案插入SQL
        device_archive_sql = sql_script[start_idx:end_idx]
        
        # 分割并执行SQL语句
        sql_statements = device_archive_sql.split('GO')
        
        for statement in sql_statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                print(f"执行设备档案SQL语句...")
                cursor.execute(statement)
                conn.commit()
        
        print('设备档案SQL脚本执行成功！')
        return True
        
    except Exception as e:
        print(f'执行设备档案SQL脚本失败：{e}')
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    script_path = 'sql_files/generate_mock_data.sql'
    
    print("执行设备档案插入脚本...")
    execute_device_archive_script(script_path)
    
    print("\n验证插入结果...")
    # 执行验证查询
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # 查询设备类型统计
    cursor.execute("SELECT DeviceType, COUNT(*) AS DeviceCount FROM DeviceArchive GROUP BY DeviceType")
    print("\n设备类型统计：")
    for row in cursor.fetchall():
        print(f"   - {row.DeviceType}: {row.DeviceCount} 台")
    
    # 查询预警器
    cursor.execute("SELECT DeviceID, DeviceName, DeviceType FROM DeviceArchive WHERE DeviceType = '预警器'")
    warning_devices = cursor.fetchall()
    print(f"\n预警器数量：{len(warning_devices)} 台")
    for device in warning_devices:
        print(f"   - {device.DeviceID}: {device.DeviceName} (类型: {device.DeviceType})")
    
    cursor.close()
    conn.close()
