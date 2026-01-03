import pyodbc

# 数据库连接参数
server = 'localhost'
database = 'SmartForestGrass'
trusted_connection = 'yes'
driver = '{ODBC Driver 17 for SQL Server}'

def execute_sql_file(file_path):
    """
    执行SQL文件
    :param file_path: SQL文件路径
    :return: 是否执行成功
    """
    try:
        # 连接数据库
        conn = pyodbc.connect(
            f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection={trusted_connection}'
        )
        cursor = conn.cursor()
        
        print(f"=== 执行SQL迁移文件: {file_path} ===")
        
        # 直接执行迁移逻辑，不依赖文件中的GO分隔符
        print("\n1. 检查需要迁移的设备ID:")
        cursor.execute("SELECT DeviceID FROM DeviceArchive WHERE DeviceID LIKE 'DEV%'")
        dev_device_ids = cursor.fetchall()
        if dev_device_ids:
            print("   需要迁移的设备ID:")
            for device_id in dev_device_ids:
                print(f"   - {device_id[0]}")
        else:
            print("   没有需要迁移的设备ID")
            return True
        
        print("\n2. 创建临时表存储映射关系")
        cursor.execute("""
        IF OBJECT_ID('tempdb..#DeviceIDMapping') IS NOT NULL
            DROP TABLE #DeviceIDMapping;
        CREATE TABLE #DeviceIDMapping (
            OldDeviceID VARCHAR(20),
            NewDeviceID VARCHAR(20)
        )
        """)
        conn.commit()
        
        print("\n3. 生成新设备ID映射")
        cursor.execute("""
        INSERT INTO #DeviceIDMapping (OldDeviceID, NewDeviceID)
        SELECT 
            DeviceID AS OldDeviceID,
            'D' + RIGHT('0000' + SUBSTRING(DeviceID, 4, 4), 4) AS NewDeviceID
        FROM DeviceArchive
        WHERE DeviceID LIKE 'DEV%'
        """)
        conn.commit()
        
        print("\n4. 显示映射关系:")
        cursor.execute("SELECT * FROM #DeviceIDMapping")
        mappings = cursor.fetchall()
        for mapping in mappings:
            print(f"   {mapping[0]} -> {mapping[1]}")
        
        print("\n5. 禁用外键约束")
        cursor.execute("ALTER TABLE DeviceStatus NOCHECK CONSTRAINT ALL")
        cursor.execute("ALTER TABLE EquipmentInspection NOCHECK CONSTRAINT ALL")
        cursor.execute("ALTER TABLE MaintenanceRecord NOCHECK CONSTRAINT ALL")
        conn.commit()
        
        print("\n6. 更新DeviceStatus表中的设备ID")
        cursor.execute("""
        UPDATE ds
        SET ds.DeviceID = map.NewDeviceID
        FROM DeviceStatus ds
        JOIN #DeviceIDMapping map ON ds.DeviceID = map.OldDeviceID
        """)
        conn.commit()
        print(f"   更新了 {cursor.rowcount} 条记录")
        
        print("\n7. 更新EquipmentInspection表中的设备ID")
        cursor.execute("""
        UPDATE ei
        SET ei.DeviceID = map.NewDeviceID
        FROM EquipmentInspection ei
        JOIN #DeviceIDMapping map ON ei.DeviceID = map.OldDeviceID
        """)
        conn.commit()
        print(f"   更新了 {cursor.rowcount} 条记录")
        
        print("\n8. 更新MaintenanceRecord表中的设备ID")
        cursor.execute("""
        UPDATE mr
        SET mr.DeviceID = map.NewDeviceID
        FROM MaintenanceRecord mr
        JOIN #DeviceIDMapping map ON mr.DeviceID = map.OldDeviceID
        """)
        conn.commit()
        print(f"   更新了 {cursor.rowcount} 条记录")
        
        print("\n9. 更新DeviceArchive表中的设备ID")
        cursor.execute("""
        UPDATE da
        SET da.DeviceID = map.NewDeviceID
        FROM DeviceArchive da
        JOIN #DeviceIDMapping map ON da.DeviceID = map.OldDeviceID
        """)
        conn.commit()
        print(f"   更新了 {cursor.rowcount} 条记录")
        
        print("\n10. 启用外键约束")
        cursor.execute("ALTER TABLE DeviceStatus CHECK CONSTRAINT ALL")
        cursor.execute("ALTER TABLE EquipmentInspection CHECK CONSTRAINT ALL")
        cursor.execute("ALTER TABLE MaintenanceRecord CHECK CONSTRAINT ALL")
        conn.commit()
        
        print("\n11. 验证更新结果:")
        cursor.execute("SELECT DeviceID FROM DeviceArchive ORDER BY DeviceID")
        all_device_ids = cursor.fetchall()
        print("   所有设备ID:")
        for device_id in all_device_ids:
            print(f"   - {device_id[0]}")
        
        print("\n12. 清理临时表")
        cursor.execute("DROP TABLE #DeviceIDMapping")
        conn.commit()
        
        print("\n=== SQL迁移执行完成 ===")
        
        conn.close()
        return True
    except Exception as e:
        print(f"\n❌ 执行SQL迁移失败: {e}")
        return False

if __name__ == "__main__":
    # 执行设备ID迁移脚本
    execute_sql_file('sql_files/migrate_device_ids.sql')
