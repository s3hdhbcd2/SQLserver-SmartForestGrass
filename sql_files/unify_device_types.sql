-- 统一设备类型脚本
-- 将现有设备类型统一修改为：传感器、摄像头、预警器

-- 1. 查看当前设备类型分布情况
SELECT DISTINCT DeviceType FROM DeviceArchive;

-- 2. 更新设备类型
-- 使用更直接的方法统一设备类型
UPDATE DeviceArchive
SET DeviceType = CASE 
    WHEN DeviceType LIKE '%监控%' THEN '摄像头'
    WHEN DeviceType LIKE '%预警%' OR DeviceType LIKE '%警报%' THEN '预警器'
    ELSE '传感器' -- 所有其他类型都映射为传感器
END;

-- 3. 再次查看设备类型分布，确认修改结果
SELECT DISTINCT DeviceType FROM DeviceArchive;

-- 4. 查看修改后的设备数量统计
SELECT DeviceType, COUNT(*) AS DeviceCount 
FROM DeviceArchive 
GROUP BY DeviceType;