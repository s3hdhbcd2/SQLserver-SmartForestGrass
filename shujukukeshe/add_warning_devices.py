import pyodbc
from datetime import datetime

# 数据库连接参数
conn_str = (
    r'DRIVER={SQL Server};' +
    r'SERVER=.;' +
    r'DATABASE=SmartForestGrass;' +
    r'UID=sa;' +
    r'PWD=123456;' +
    r'Trusted_Connection=no;'
)

try:
    # 连接数据库
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("成功连接到SQL Server数据库")
    
    # 1. 查询当前设备数量，生成新的设备ID
    print("\n1. 查询当前设备数量：")
    cursor.execute("SELECT COUNT(*) FROM DeviceArchive")
    total_devices = cursor.fetchone()[0]
    print(f"当前共有 {total_devices} 台设备")
    
    # 2. 直接执行INSERT语句添加预警器
    print("\n2. 添加预警器设备：")
    
    # 预警器数据
    warning_devices = [
        ('D021', '火灾预警器', '预警器', 'ALARM-001', datetime(2023, 2, 1), 'R001', 'U001', '3'),
        ('D022', '火灾预警器', '预警器', 'ALARM-001', datetime(2023, 2, 2), 'R002', 'U001', '3'),
        ('D023', '病虫害预警器', '预警器', 'ALARM-002', datetime(2023, 2, 3), 'R003', 'U001', '3'),
        ('D024', '病虫害预警器', '预警器', 'ALARM-002', datetime(2023, 2, 4), 'R004', 'U001', '3'),
        ('D025', '火灾预警器', '预警器', 'ALARM-001', datetime(2023, 2, 5), 'R005', 'U001', '3')
    ]
    
    # 插入语句
    insert_sql = """
    INSERT INTO DeviceArchive (DeviceID, DeviceName, DeviceType, ModelSpecification, PurchaseTime, RegionID, InstallerID, WarrantyPeriod)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    # 执行插入
    for device in warning_devices:
        try:
            cursor.execute(insert_sql, device)
            conn.commit()
            print(f"   ✅ 成功添加：{device[0]} - {device[1]} ({device[2]})")
        except Exception as e:
            print(f"   ❌ 添加失败：{device[0]} - {device[1]} ({device[2]}) - 错误：{e}")
            # 继续尝试添加其他设备
    
    # 3. 验证插入结果
    print("\n3. 验证插入结果：")
    
    # 查询设备类型统计
    cursor.execute("SELECT DeviceType, COUNT(*) AS DeviceCount FROM DeviceArchive GROUP BY DeviceType")
    print("设备类型统计：")
    for row in cursor.fetchall():
        print(f"   - {row.DeviceType}: {row.DeviceCount} 台")
    
    # 查询预警器
    cursor.execute("SELECT DeviceID, DeviceName, DeviceType, RegionID FROM DeviceArchive WHERE DeviceType = '预警器' ORDER BY DeviceID")
    warning_devices_result = cursor.fetchall()
    print(f"\n预警器数量：{len(warning_devices_result)} 台")
    for device in warning_devices_result:
        print(f"   - {device.DeviceID}: {device.DeviceName} (类型: {device.DeviceType}, 区域: {device.RegionID})")
    
    # 4. 为预警器添加状态记录
    print("\n4. 为预警器添加初始状态记录：")
    
    status_insert_sql = """
    INSERT INTO DeviceStatus (StatusID, DeviceID, CollectionTime, RunningStatus, BatteryLevel, SignalStrength)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    
    # 为每台预警器添加一条正常状态记录
    for device in warning_devices_result:
        device_id = device.DeviceID
        # 生成状态ID
        cursor.execute("SELECT COUNT(*) FROM DeviceStatus")
        status_count = cursor.fetchone()[0] + 1
        status_id = f"DS{str(status_count).zfill(4)}"
        
        try:
            cursor.execute(
                status_insert_sql,
                (status_id, device_id, datetime.now(), '正常', 100.0, 100)
            )
            conn.commit()
            print(f"   ✅ 成功添加状态记录：{status_id} - {device_id}")
        except Exception as e:
            print(f"   ❌ 添加状态记录失败：{device_id} - 错误：{e}")
    
    print("\n预警器添加完成！")
    
except Exception as e:
    print(f"执行失败：{e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()
