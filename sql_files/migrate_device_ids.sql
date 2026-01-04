-- 设备ID格式迁移脚本 - 将DEV+4位数字格式转换为D+4位数字格式
-- SQL Server版本

-- 1. 检查是否需要迁移
SELECT DeviceID FROM DeviceArchive WHERE DeviceID LIKE 'DEV%';

-- 2. 创建临时表存储映射关系
IF OBJECT_ID('tempdb..#DeviceIDMapping') IS NOT NULL
    DROP TABLE #DeviceIDMapping;

CREATE TABLE #DeviceIDMapping (
    OldDeviceID VARCHAR(20),
    NewDeviceID VARCHAR(20)
);

-- 3. 生成新设备ID映射
INSERT INTO #DeviceIDMapping (OldDeviceID, NewDeviceID)
SELECT 
    DeviceID AS OldDeviceID,
    'D' + RIGHT('0000' + SUBSTRING(DeviceID, 4, 4), 4) AS NewDeviceID
FROM DeviceArchive
WHERE DeviceID LIKE 'DEV%';

-- 4. 显示映射关系
SELECT * FROM #DeviceIDMapping;

-- 5. 禁用外键约束
ALTER TABLE DeviceStatus NOCHECK CONSTRAINT FK__DeviceStatus__DeviceID;
ALTER TABLE EquipmentInspection NOCHECK CONSTRAINT FK__EquipmentInspection__DeviceID;
ALTER TABLE MaintenanceRecord NOCHECK CONSTRAINT FK__MaintenanceRecord__DeviceID;

-- 6. 更新相关表中的设备ID

-- 更新DeviceStatus表
UPDATE ds
SET ds.DeviceID = map.NewDeviceID
FROM DeviceStatus ds
JOIN #DeviceIDMapping map ON ds.DeviceID = map.OldDeviceID;

-- 更新EquipmentInspection表
UPDATE ei
SET ei.DeviceID = map.NewDeviceID
FROM EquipmentInspection ei
JOIN #DeviceIDMapping map ON ei.DeviceID = map.OldDeviceID;

-- 更新MaintenanceRecord表
UPDATE mr
SET mr.DeviceID = map.NewDeviceID
FROM MaintenanceRecord mr
JOIN #DeviceIDMapping map ON mr.DeviceID = map.OldDeviceID;

-- 7. 更新DeviceArchive表中的设备ID
UPDATE da
SET da.DeviceID = map.NewDeviceID
FROM DeviceArchive da
JOIN #DeviceIDMapping map ON da.DeviceID = map.OldDeviceID;

-- 8. 启用外键约束
ALTER TABLE DeviceStatus CHECK CONSTRAINT FK__DeviceStatus__DeviceID;
ALTER TABLE EquipmentInspection CHECK CONSTRAINT FK__EquipmentInspection__DeviceID;
ALTER TABLE MaintenanceRecord CHECK CONSTRAINT FK__MaintenanceRecord__DeviceID;

-- 9. 验证更新结果
SELECT DeviceID FROM DeviceArchive ORDER BY DeviceID;

-- 10. 清理临时表
DROP TABLE #DeviceIDMapping;

-- 11. 插入测试数据（使用新格式）
-- 注意：只有在需要插入新数据时才执行以下语句
/*
INSERT INTO DeviceArchive (DeviceID, DeviceName, DeviceType, ModelSpecification, PurchaseTime, RegionID, InstallerID, WarrantyPeriod)
VALUES
('D0026', '测试设备1', '温度传感器', '默认型号', GETDATE(), 'R001', 'ADMIN001', '3年'),
('D0027', '测试设备2', '湿度传感器', '默认型号', GETDATE(), 'R002', 'ADMIN001', '3年');
*/
