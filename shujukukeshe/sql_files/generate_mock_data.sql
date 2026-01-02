-- 智慧林草系统-模拟数据生成脚本
-- 该脚本用于生成每个表至少20条模拟数据，并先清空现有数据

-- 注意：请确保在执行此脚本前已备份数据库

-- 设置SQL Server兼容模式
SET NOCOUNT ON;
GO

-- =============================================
-- 1. 清空所有表数据（按外键依赖顺序使用DELETE）
-- =============================================

PRINT '正在清空现有数据...';
GO

-- 按外键依赖顺序删除数据
DELETE FROM Feedback;
DELETE FROM GeneratedReport;
DELETE FROM NotificationRecord;
DELETE FROM EquipmentInspection;
DELETE FROM MaintenanceRecord;
DELETE FROM DeviceStatus;
DELETE FROM WarningRecord;
DELETE FROM ResourceChangeRecord;
DELETE FROM MonitoringData;
DELETE FROM ForestResource;
DELETE FROM DeviceArchive;
DELETE FROM Sensor;
DELETE FROM WarningRule;
DELETE FROM ReportTemplate;
DELETE FROM Region;
DELETE FROM [User];

PRINT '现有数据清空完成！';
GO

-- =============================================
-- 2. 插入模拟数据（按表创建顺序）
-- =============================================

-- 2.1 插入用户表(User)数据（25条）
PRINT '正在插入用户表数据...';
GO

INSERT INTO [User] (UserID, Username, Password, Name, Contact, Role, Status)
VALUES
('U001', 'admin', '123456', '管理员', 'admin@example.com', '管理员', '启用'),
('U002', 'data_admin', '123456', '数据管理员', 'data@example.com', '数据管理员', '启用'),
('U003', 'ranger1', '123456', '区域护林员1', 'ranger1@example.com', '区域护林员', '启用'),
('U004', 'ranger2', '123456', '区域护林员2', 'ranger2@example.com', '区域护林员', '启用'),
('U005', 'ranger3', '123456', '区域护林员3', 'ranger3@example.com', '区域护林员', '启用'),
('U006', 'ranger4', '123456', '区域护林员4', 'ranger4@example.com', '区域护林员', '启用'),
('U007', 'ranger5', '123456', '区域护林员5', 'ranger5@example.com', '区域护林员', '启用'),
('U008', 'ranger6', '123456', '区域护林员6', 'ranger6@example.com', '区域护林员', '启用'),
('U009', 'supervisor1', '123456', '监管人员1', 'supervisor1@example.com', '监管人员', '启用'),
('U010', 'public1', '123456', '公众用户1', 'public1@example.com', '公众用户', '启用'),
('U011', 'user1', '123456', '公众用户2', 'user1@example.com', '公众用户', '启用'),
('U012', 'user2', '123456', '公众用户3', 'user2@example.com', '公众用户', '启用'),
('U013', 'user3', '123456', '公众用户4', 'user3@example.com', '公众用户', '启用'),
('U014', 'user4', '123456', '公众用户5', 'user4@example.com', '公众用户', '启用'),
('U015', 'user5', '123456', '公众用户6', 'user5@example.com', '公众用户', '启用'),
('U016', 'user6', '123456', '公众用户7', 'user6@example.com', '公众用户', '启用'),
('U017', 'user7', '123456', '公众用户8', 'user7@example.com', '公众用户', '启用'),
('U018', 'user8', '123456', '公众用户9', 'user8@example.com', '公众用户', '启用'),
('U019', 'user9', '123456', '公众用户10', 'user9@example.com', '公众用户', '启用'),
('U020', 'user10', '123456', '公众用户11', 'user10@example.com', '公众用户', '启用'),
('U021', 'user11', '123456', '公众用户12', 'user11@example.com', '公众用户', '启用'),
('U022', 'user12', '123456', '公众用户13', 'user12@example.com', '公众用户', '启用'),
('U023', 'user13', '123456', '公众用户14', 'user13@example.com', '公众用户', '启用'),
('U024', 'user14', '123456', '公众用户15', 'user14@example.com', '公众用户', '启用'),
('U025', 'user15', '123456', '公众用户16', 'user15@example.com', '公众用户', '启用');

PRINT '用户表数据插入完成！';
GO

-- 2.2 插入区域表(Region)数据（20条）
PRINT '正在插入区域表数据...';
GO

INSERT INTO Region (RegionID, RegionName, RegionType, Longitude, Latitude, ManagerID, CreateTime)
VALUES
('R001', '华北林区', '森林', 116.4074, 39.9042, 'U003', GETDATE()),
('R002', '东北林区', '森林', 126.6318, 45.7569, 'U004', GETDATE()),
('R003', '华东林区', '森林', 121.4737, 31.2304, 'U005', GETDATE()),
('R004', '华南林区', '森林', 113.2644, 23.1291, 'U006', GETDATE()),
('R005', '西南林区', '森林', 104.0668, 30.5728, 'U007', GETDATE()),
('R006', '西北林区', '森林', 108.9398, 34.3416, 'U008', GETDATE()),
('R007', '内蒙古草原', '草原', 111.6708, 40.8183, 'U003', GETDATE()),
('R008', '新疆草原', '草原', 87.6168, 43.8256, 'U004', GETDATE()),
('R009', '青藏高原草原', '草原', 91.1175, 29.6469, 'U005', GETDATE()),
('R010', '黄土高原', '草原', 109.3326, 36.0611, 'U006', GETDATE()),
('R011', '长江中下游湿地', '湿地', 114.3055, 30.5928, 'U007', GETDATE()),
('R012', '珠江三角洲', '湿地', 113.2806, 23.1251, 'U008', GETDATE()),
('R013', '三江源保护区', '保护区', 96.4551, 35.6785, 'U003', GETDATE()),
('R014', '大熊猫保护区', '保护区', 103.1873, 31.3412, 'U004', GETDATE()),
('R015', '东北虎保护区', '保护区', 130.9751, 44.7321, 'U005', GETDATE()),
('R016', '武夷山保护区', '保护区', 117.7103, 27.6503, 'U006', GETDATE()),
('R017', '长白山保护区', '保护区', 128.1062, 42.0349, 'U007', GETDATE()),
('R018', '西双版纳保护区', '保护区', 101.2798, 22.0049, 'U008', GETDATE()),
('R019', '神农架保护区', '保护区', 110.7847, 31.7439, 'U003', GETDATE()),
('R020', '天山山脉', '森林', 86.9226, 43.8256, 'U004', GETDATE()),
('R021', '祁连山保护区', '保护区', 98.2062, 38.1736, 'U005', GETDATE());

PRINT '区域表数据插入完成！';
GO

-- 2.3 插入传感器表(Sensor)数据（25条）
PRINT '正在插入传感器表数据...';
GO

INSERT INTO Sensor (SensorID, RegionID, DeviceModel, MonitoringType, InstallTime, CommunicationProtocol)
VALUES
('S001', 'R001', 'SENSOR-001', '温度', '2023-01-01 10:00:00', 'HTTP'),
('S002', 'R001', 'SENSOR-002', '湿度', '2023-01-02 11:00:00', 'HTTP'),
('S003', 'R001', 'SENSOR-003', '风速', '2023-01-03 12:00:00', 'MQTT'),
('S004', 'R001', 'SENSOR-004', '降雨量', '2023-01-04 13:00:00', 'MQTT'),
('S005', 'R001', 'SENSOR-005', '烟雾', '2023-01-05 14:00:00', 'HTTP'),
('S006', 'R002', 'SENSOR-001', '温度', '2023-01-06 15:00:00', 'HTTP'),
('S007', 'R002', 'SENSOR-002', '湿度', '2023-01-07 16:00:00', 'HTTP'),
('S008', 'R002', 'SENSOR-003', '风速', '2023-01-08 17:00:00', 'MQTT'),
('S009', 'R002', 'SENSOR-004', '降雨量', '2023-01-09 18:00:00', 'MQTT'),
('S010', 'R002', 'SENSOR-005', '烟雾', '2023-01-10 19:00:00', 'HTTP'),
('S011', 'R003', 'SENSOR-001', '温度', '2023-01-11 20:00:00', 'HTTP'),
('S012', 'R003', 'SENSOR-002', '湿度', '2023-01-12 21:00:00', 'HTTP'),
('S013', 'R003', 'SENSOR-003', '风速', '2023-01-13 22:00:00', 'MQTT'),
('S014', 'R003', 'SENSOR-004', '降雨量', '2023-01-14 23:00:00', 'MQTT'),
('S015', 'R003', 'SENSOR-005', '烟雾', '2023-01-15 00:00:00', 'HTTP'),
('S016', 'R004', 'SENSOR-001', '温度', '2023-01-16 01:00:00', 'HTTP'),
('S017', 'R004', 'SENSOR-002', '湿度', '2023-01-17 02:00:00', 'HTTP'),
('S018', 'R004', 'SENSOR-003', '风速', '2023-01-18 03:00:00', 'MQTT'),
('S019', 'R004', 'SENSOR-004', '降雨量', '2023-01-19 04:00:00', 'MQTT'),
('S020', 'R004', 'SENSOR-005', '烟雾', '2023-01-20 05:00:00', 'HTTP'),
('S021', 'R005', 'SENSOR-001', '温度', '2023-01-21 06:00:00', 'HTTP'),
('S022', 'R005', 'SENSOR-002', '湿度', '2023-01-22 07:00:00', 'HTTP'),
('S023', 'R005', 'SENSOR-003', '风速', '2023-01-23 08:00:00', 'MQTT'),
('S024', 'R005', 'SENSOR-004', '降雨量', '2023-01-24 09:00:00', 'MQTT'),
('S025', 'R005', 'SENSOR-005', '烟雾', '2023-01-25 10:00:00', 'HTTP');

PRINT '传感器表数据插入完成！';
GO

-- 2.4 插入预警规则表(WarningRule)数据（20条）
PRINT '正在插入预警规则表数据...';
GO

INSERT INTO WarningRule (RuleID, WarningType, TriggerCondition, WarningLevel, IsActive)
VALUES
('WR001', '火灾', '温度 > 42 AND 湿度 < 15 AND 烟雾 > 80', '特别严重', 1),
('WR002', '火灾', '温度 > 35 AND 湿度 < 30 AND 烟雾 > 50', '严重', 1),
('WR003', '火灾', '温度 > 30 AND 湿度 < 25 AND 烟雾 > 40', '较重', 1),
('WR004', '火灾', '温度 > 25 AND 湿度 < 20 AND 烟雾 > 30', '一般', 1),
('WR005', '旱情', '湿度 < 10 AND 降雨量 < 2', '特别严重', 1),
('WR006', '旱情', '湿度 < 15 AND 降雨量 < 5', '严重', 1),
('WR007', '旱情', '湿度 < 20 AND 降雨量 < 10', '较重', 1),
('WR008', '旱情', '湿度 < 25 AND 降雨量 < 15', '一般', 1),
('WR009', '病虫害', '病虫害指数 > 95', '特别严重', 1),
('WR010', '病虫害', '病虫害指数 > 80', '严重', 1),
('WR011', '病虫害', '病虫害指数 > 60', '较重', 1),
('WR012', '病虫害', '病虫害指数 > 40', '一般', 1),
('WR013', '大风', '风速 > 30', '特别严重', 1),
('WR014', '大风', '风速 > 20', '严重', 1),
('WR015', '大风', '风速 > 15', '较重', 1),
('WR016', '大风', '风速 > 10', '一般', 1),
('WR017', '洪水', '降雨量 > 70', '特别严重', 1),
('WR018', '洪水', '降雨量 > 50', '严重', 1),
('WR019', '洪水', '降雨量 > 30', '较重', 1),
('WR020', '洪水', '降雨量 > 20', '一般', 1),
('WR021', '高温', '温度 > 45', '特别严重', 1),
('WR022', '高温', '温度 > 40', '严重', 1),
('WR023', '高温', '温度 > 35', '较重', 1),
('WR024', '低温', '温度 < -20', '特别严重', 1),
('WR025', '低温', '温度 < -10', '严重', 1),
('WR026', '低温', '温度 < -5', '较重', 1),
('WR027', '低温', '温度 < 0', '一般', 1);

PRINT '预警规则表数据插入完成！';
GO

-- 2.5 插入设备档案表(DeviceArchive)数据（20条）
PRINT '正在插入设备档案表数据...';
GO

INSERT INTO DeviceArchive (DeviceID, DeviceName, DeviceType, ModelSpecification, PurchaseTime, RegionID, InstallerID, WarrantyPeriod)
VALUES
('D001', '温度传感器', '传感器', 'SENSOR-001', '2023-01-01', 'R001', 'U001', 3),
('D002', '湿度传感器', '传感器', 'SENSOR-002', '2023-01-02', 'R001', 'U001', 3),
('D003', '风速传感器', '传感器', 'SENSOR-003', '2023-01-03', 'R001', 'U001', 3),
('D004', '降雨量传感器', '传感器', 'SENSOR-004', '2023-01-04', 'R001', 'U001', 3),
('D005', '烟雾传感器', '传感器', 'SENSOR-005', '2023-01-05', 'R001', 'U001', 3),
('D006', '病虫害传感器', '传感器', 'SENSOR-006', '2023-01-06', 'R001', 'U001', 3),
('D007', '土壤湿度传感器', '传感器', 'SENSOR-007', '2023-01-07', 'R001', 'U001', 3),
('D008', '摄像头', '监控设备', 'CAM-001', '2023-01-08', 'R001', 'U001', 3),
('D009', '摄像头', '监控设备', 'CAM-002', '2023-01-09', 'R001', 'U001', 3),
('D010', '数据采集器', '采集设备', 'COL-001', '2023-01-10', 'R001', 'U001', 3),
('D011', '温度传感器', '传感器', 'SENSOR-001', '2023-01-11', 'R002', 'U001', 3),
('D012', '湿度传感器', '传感器', 'SENSOR-002', '2023-01-12', 'R002', 'U001', 3),
('D013', '风速传感器', '传感器', 'SENSOR-003', '2023-01-13', 'R002', 'U001', 3),
('D014', '降雨量传感器', '传感器', 'SENSOR-004', '2023-01-14', 'R002', 'U001', 3),
('D015', '烟雾传感器', '传感器', 'SENSOR-005', '2023-01-15', 'R002', 'U001', 3),
('D016', '病虫害传感器', '传感器', 'SENSOR-006', '2023-01-16', 'R002', 'U001', 3),
('D017', '土壤湿度传感器', '传感器', 'SENSOR-007', '2023-01-17', 'R002', 'U001', 3),
('D018', '摄像头', '监控设备', 'CAM-001', '2023-01-18', 'R002', 'U001', 3),
('D019', '摄像头', '监控设备', 'CAM-002', '2023-01-19', 'R002', 'U001', 3),
('D020', '数据采集器', '采集设备', 'COL-001', '2023-01-20', 'R002', 'U001', 3);

PRINT '设备档案表数据插入完成！';
GO

-- 2.6 插入林草资源表(ForestResource)数据（20条）
PRINT '正在插入林草资源表数据...';
GO

INSERT INTO ForestResource (ResourceID, RegionID, ResourceType, TreeSpecies, Quantity, CoverageArea, GrowthStatus, PlantingTime, UpdateTime, UpdatedBy)
VALUES
('FR001', 'R001', '乔木', '松树', 1000, 100.5, '良好', '2023-01-01', GETDATE(), 'U001'),
('FR002', 'R001', '乔木', '柏树', 800, 80.3, '良好', '2023-02-01', GETDATE(), 'U001'),
('FR003', 'R001', '灌木', '荆棘', 500, 50.2, '良好', '2023-03-01', GETDATE(), 'U001'),
('FR004', 'R001', '草本', '草', 3000, 30.1, '良好', '2023-04-01', GETDATE(), 'U001'),
('FR005', 'R002', '乔木', '落叶松', 1200, 120.7, '良好', '2023-01-01', GETDATE(), 'U001'),
('FR006', 'R002', '乔木', '云杉', 900, 90.4, '良好', '2023-02-01', GETDATE(), 'U001'),
('FR007', 'R002', '灌木', '沙柳', 600, 60.3, '良好', '2023-03-01', GETDATE(), 'U001'),
('FR008', 'R002', '草本', '羊草', 4000, 40.2, '良好', '2023-04-01', GETDATE(), 'U001'),
('FR009', 'R003', '乔木', '樟树', 1100, 110.6, '良好', '2023-01-01', GETDATE(), 'U001'),
('FR010', 'R003', '乔木', '楠木', 950, 95.5, '良好', '2023-02-01', GETDATE(), 'U001'),
('FR011', 'R003', '灌木', '杜鹃', 550, 55.4, '良好', '2023-03-01', GETDATE(), 'U001'),
('FR012', 'R003', '草本', '狗尾草', 3500, 35.3, '良好', '2023-04-01', GETDATE(), 'U001'),
('FR013', 'R004', '乔木', '榕树', 1300, 130.8, '良好', '2023-01-01', GETDATE(), 'U001'),
('FR014', 'R004', '乔木', '桉树', 1000, 100.6, '良好', '2023-02-01', GETDATE(), 'U001'),
('FR015', 'R004', '灌木', '簕杜鹃', 650, 65.5, '良好', '2023-03-01', GETDATE(), 'U001'),
('FR016', 'R004', '草本', '马尼拉草', 4500, 45.4, '良好', '2023-04-01', GETDATE(), 'U001'),
('FR017', 'R005', '乔木', '冷杉', 1400, 140.9, '良好', '2023-01-01', GETDATE(), 'U001'),
('FR018', 'R005', '乔木', '铁杉', 1100, 110.7, '良好', '2023-02-01', GETDATE(), 'U001'),
('FR019', 'R005', '灌木', '高山杜鹃', 700, 70.6, '良好', '2023-03-01', GETDATE(), 'U001'),
('FR020', 'R005', '草本', '高山草甸', 5000, 50.5, '良好', '2023-04-01', GETDATE(), 'U001');

PRINT '林草资源表数据插入完成！';
GO

-- 2.7 插入报表模板表(ReportTemplate)数据（20条）
PRINT '正在插入报表模板表数据...';
GO

INSERT INTO ReportTemplate (TemplateID, ReportName, ReportType, StatisticalIndicators, Description)
VALUES
('TEMP001', '环境监测日报', '环境监测', '{"temperature": true, "humidity": true, "wind_speed": true, "rainfall": true, "smoke": true}', '每日环境监测数据汇总'),
('TEMP002', '环境监测周报', '环境监测', '{"temperature": true, "humidity": true, "wind_speed": true, "rainfall": true, "smoke": true}', '每周环境监测数据汇总'),
('TEMP003', '环境监测月报', '环境监测', '{"temperature": true, "humidity": true, "wind_speed": true, "rainfall": true, "smoke": true}', '每月环境监测数据汇总'),
('TEMP004', '设备状态日报', '设备状态', '{"running_status": true, "battery_level": true, "signal_strength": true}', '每日设备状态汇总'),
('TEMP005', '设备状态周报', '设备状态', '{"running_status": true, "battery_level": true, "signal_strength": true}', '每周设备状态汇总'),
('TEMP006', '设备状态月报', '设备状态', '{"running_status": true, "battery_level": true, "signal_strength": true}', '每月设备状态汇总'),
('TEMP007', '资源统计月报', '资源统计', '{"coverage_area": true, "tree_species": true, "growth_status": true}', '每月资源统计汇总'),
('TEMP008', '资源统计季报', '资源统计', '{"coverage_area": true, "tree_species": true, "growth_status": true}', '每季资源统计汇总'),
('TEMP009', '资源统计年报', '资源统计', '{"coverage_area": true, "tree_species": true, "growth_status": true}', '每年资源统计汇总'),
('TEMP010', '预警记录日报', '预警记录', '{"warning_type": true, "warning_level": true, "status": true}', '每日预警记录汇总'),
('TEMP011', '预警记录周报', '预警记录', '{"warning_type": true, "warning_level": true, "status": true}', '每周预警记录汇总'),
('TEMP012', '预警记录月报', '预警记录', '{"warning_type": true, "warning_level": true, "status": true}', '每月预警记录汇总'),
('TEMP013', '火灾风险评估', '环境监测', '{"temperature": true, "humidity": true, "smoke": true}', '火灾风险评估报告'),
('TEMP014', '旱情风险评估', '环境监测', '{"humidity": true, "rainfall": true}', '旱情风险评估报告'),
('TEMP015', '病虫害风险评估', '环境监测', '{"pest_disease": true}', '病虫害风险评估报告'),
('TEMP016', '设备维护建议', '设备状态', '{"running_status": true, "battery_level": true}', '设备维护建议报告'),
('TEMP017', '资源变化分析', '资源统计', '{"coverage_area": true, "change_type": true}', '资源变化分析报告'),
('TEMP018', '区域环境综合评估', '环境监测', '{"temperature": true, "humidity": true, "wind_speed": true, "rainfall": true, "smoke": true}', '区域环境综合评估报告'),
('TEMP019', '年度环境总结', '环境监测', '{"temperature": true, "humidity": true, "wind_speed": true, "rainfall": true, "smoke": true}', '年度环境总结报告'),
('TEMP020', '年度设备总结', '设备状态', '{"running_status": true, "battery_level": true, "signal_strength": true}', '年度设备总结报告');

PRINT '报表模板表数据插入完成！';
GO

-- 2.8 插入监测数据表(MonitoringData)数据（50条）
PRINT '正在插入监测数据表数据...';
GO

DECLARE @i INT = 1;
WHILE @i <= 50
BEGIN
    INSERT INTO MonitoringData (DataID, SensorID, RegionID, DataTime, Temperature, Humidity, WindSpeed, Rainfall, PestDiseaseValue, SmokeValue, SoilMoisture)
    VALUES
    (
        'MD' + RIGHT('0000' + CAST(@i AS VARCHAR(4)), 4),
        'S' + RIGHT('00' + CAST(((@i - 1) % 25 + 1) AS VARCHAR(2)), 3),
        'R' + RIGHT('00' + CAST(((@i - 1) % 20 + 1) AS VARCHAR(2)), 3),
        DATEADD(MINUTE, -@i * 15, GETDATE()),
        15 + (@i % 20),
        40 + (@i % 30),
        5 + (@i % 10),
        CASE WHEN @i % 5 = 0 THEN @i % 20 ELSE 0 END,
        @i % 100,
        CASE WHEN @i % 3 = 0 THEN @i % 60 ELSE 0 END,
        30 + (@i % 40)
    );
    SET @i = @i + 1;
END

PRINT '监测数据表数据插入完成！';
GO

-- 2.9 插入预警记录表(WarningRecord)数据（30条）
PRINT '正在插入预警记录表数据...';
GO

DECLARE @j INT = 1;
WHILE @j <= 30
BEGIN
    INSERT INTO WarningRecord (WarningID, RuleID, RegionID, TriggerTime, WarningContent, Status, HandlerID, HandleResult)
    VALUES
    (
        'WRC' + RIGHT('0000' + CAST(@j AS VARCHAR(4)), 4),
        'WR' + RIGHT('00' + CAST(((@j - 1) % 20 + 1) AS VARCHAR(2)), 3),
        'R' + RIGHT('00' + CAST(((@j - 1) % 20 + 1) AS VARCHAR(2)), 3),
        DATEADD(HOUR, -@j, GETDATE()),
        CASE WHEN @j % 3 = 0 THEN '火灾预警' WHEN @j % 3 = 1 THEN '旱情预警' ELSE '病虫害预警' END,
        CASE WHEN @j % 4 = 0 THEN '已处理' WHEN @j % 4 = 1 THEN '处理中' ELSE '未处理' END,
        CASE WHEN @j % 4 = 0 THEN 'U' + RIGHT('00' + CAST(((@j - 1) % 25 + 1) AS VARCHAR(2)), 3) ELSE NULL END,
        CASE WHEN @j % 4 = 0 THEN '已采取措施' ELSE NULL END
    );
    SET @j = @j + 1;
END

PRINT '预警记录表数据插入完成！';
GO

-- 2.10 插入设备状态表(DeviceStatus)数据（40条）
PRINT '正在插入设备状态表数据...';
GO

DECLARE @k INT = 1;
WHILE @k <= 40
BEGIN
    INSERT INTO DeviceStatus (StatusID, DeviceID, CollectionTime, RunningStatus, BatteryLevel, SignalStrength)
    VALUES
    (
        'DS' + RIGHT('0000' + CAST(@k AS VARCHAR(4)), 4),
        'D' + RIGHT('00' + CAST(((@k - 1) % 20 + 1) AS VARCHAR(2)), 3),
        DATEADD(MINUTE, -@k * 30, GETDATE()),
        CASE WHEN @k % 10 = 0 THEN '故障' ELSE '正常' END,
        100 - (@k % 90),
        CASE WHEN @k % 15 = 0 THEN 1 WHEN @k % 15 = 1 THEN 2 ELSE 3 END
    );
    SET @k = @k + 1;
END

PRINT '设备状态表数据插入完成！';
GO

-- 2.11 插入资源变动记录表(ResourceChangeRecord)数据（25条）
PRINT '正在插入资源变动记录表数据...';
GO

DECLARE @l INT = 1;
WHILE @l <= 25
BEGIN
    INSERT INTO ResourceChangeRecord (ChangeID, ResourceID, ChangeType, ChangeReason, ChangeTime, OperatorID)
    VALUES
    (
        'RCR' + RIGHT('0000' + CAST(@l AS VARCHAR(4)), 4),
        'FR' + RIGHT('00' + CAST(((@l - 1) % 20 + 1) AS VARCHAR(2)), 3),
        CASE WHEN @l % 3 = 0 THEN '增加' WHEN @l % 3 = 1 THEN '减少' ELSE '变更' END,
        CASE WHEN @l % 3 = 0 THEN '新种植' WHEN @l % 3 = 1 THEN '采伐' ELSE '状态变更' END,
        DATEADD(DAY, -@l, GETDATE()),
        'U' + RIGHT('00' + CAST(((@l - 1) % 25 + 1) AS VARCHAR(2)), 3)
    );
    SET @l = @l + 1;
END

PRINT '资源变动记录表数据插入完成！';
GO

-- 2.12 插入生成的报表表(GeneratedReport)数据（20条）
PRINT '正在插入生成的报表表数据...';
GO

DECLARE @m INT = 1;
WHILE @m <= 20
BEGIN
    INSERT INTO GeneratedReport (ReportID, ReportName, TemplateID, RegionID, StartTime, EndTime, ReportContent, ReportFilePath, GeneratedTime, GeneratedBy)
    VALUES
    (
        'GR' + RIGHT('0000' + CAST(@m AS VARCHAR(4)), 4),
        '报表' + CAST(@m AS VARCHAR(2)),
        'TEMP' + RIGHT('000' + CAST(((@m - 1) % 20 + 1) AS VARCHAR(3)), 3),
        'R' + RIGHT('00' + CAST(((@m - 1) % 20 + 1) AS VARCHAR(2)), 3),
        DATEADD(DAY, -7, GETDATE()),
        GETDATE(),
        '这是第' + CAST(@m AS VARCHAR(2)) + '份测试报表内容。',
        'reports/GR' + RIGHT('0000' + CAST(@m AS VARCHAR(4)), 4) + '.txt',
        DATEADD(HOUR, -@m * 2, GETDATE()),
        'U' + RIGHT('00' + CAST(((@m - 1) % 25 + 1) AS VARCHAR(2)), 3)
    );
    SET @m = @m + 1;
END

PRINT '生成的报表表数据插入完成！';
GO

-- 2.13 插入通知记录表(NotificationRecord)数据（30条）
PRINT '正在插入通知记录表数据...';
GO

DECLARE @n INT = 1;
WHILE @n <= 30
BEGIN
    INSERT INTO NotificationRecord (NotificationID, WarningID, ReceiverID, NotificationMethod, SendTime, ReceiveStatus)
    VALUES
    (
        'NOT' + RIGHT('0000' + CAST(@n AS VARCHAR(4)), 4),
        'WRC' + RIGHT('0000' + CAST(((@n - 1) % 30 + 1) AS VARCHAR(4)), 4),
        'U' + RIGHT('00' + CAST(((@n - 1) % 25 + 1) AS VARCHAR(2)), 3),
        CASE WHEN @n % 3 = 0 THEN '短信' WHEN @n % 3 = 1 THEN '邮件' ELSE '系统消息' END,
        DATEADD(HOUR, -@n * 2, GETDATE()),
        CASE WHEN @n % 4 = 0 THEN '已阅读' WHEN @n % 4 = 1 THEN '已发送' ELSE '未发送' END
    );
    SET @n = @n + 1;
END

PRINT '通知记录表数据插入完成！';
GO

-- 2.14 插入设备巡检记录表(EquipmentInspection)数据（25条）
PRINT '正在插入设备巡检记录表数据...';
GO

DECLARE @o INT = 1;
WHILE @o <= 25
BEGIN
    INSERT INTO EquipmentInspection (InspectionID, DeviceID, InspectionTime, InspectorID, MaintenanceType, InspectionResult, ProblemDescription, MaintenanceContent, MaintenanceResult)
    VALUES
    (
        'EI' + RIGHT('0000' + CAST(@o AS VARCHAR(4)), 4),
        'D' + RIGHT('00' + CAST(((@o - 1) % 20 + 1) AS VARCHAR(2)), 3),
        DATEADD(DAY, -@o, GETDATE()),
        'U' + RIGHT('00' + CAST(((@o - 1) % 25 + 1) AS VARCHAR(2)), 3),
        CASE WHEN @o % 4 = 0 THEN '定期巡检' WHEN @o % 4 = 1 THEN '故障维修' ELSE '日常维护' END,
        CASE WHEN @o % 5 = 0 THEN '异常' ELSE '正常' END,
        CASE WHEN @o % 5 = 0 THEN '设备运行温度偏高' ELSE NULL END,
        CASE WHEN @o % 5 = 0 THEN '清洁设备散热片，检查风扇' ELSE NULL END,
        CASE WHEN @o % 5 = 0 THEN '设备温度恢复正常' ELSE NULL END
    );
    SET @o = @o + 1;
END

PRINT '设备巡检记录表数据插入完成！';
GO

-- 2.15 插入维护记录表(MaintenanceRecord)数据（25条）
PRINT '正在插入维护记录表数据...';
GO

DECLARE @p INT = 1;
WHILE @p <= 25
BEGIN
    INSERT INTO MaintenanceRecord (MaintenanceID, DeviceID, MaintenanceType, MaintenanceTime, MaintainerID, MaintenanceContent, MaintenanceResult)
    VALUES
    (
        'MR' + RIGHT('0000' + CAST(@p AS VARCHAR(4)), 4),
        'D' + RIGHT('00' + CAST(((@p - 1) % 20 + 1) AS VARCHAR(2)), 3),
        CASE WHEN @p % 4 = 0 THEN '定期维护' WHEN @p % 4 = 1 THEN '故障维修' ELSE '升级维护' END,
        DATEADD(DAY, -@p * 2, GETDATE()),
        'U' + RIGHT('00' + CAST(((@p - 1) % 25 + 1) AS VARCHAR(2)), 3),
        CASE WHEN @p % 3 = 0 THEN '更换设备电池' WHEN @p % 3 = 1 THEN '修复设备传感器' ELSE '升级设备固件' END,
        CASE WHEN @p % 5 = 0 THEN '部分成功' ELSE '成功' END
    );
    SET @p = @p + 1;
END

PRINT '维护记录表数据插入完成！';
GO

-- =============================================
-- 3. 显示插入结果
-- =============================================

PRINT '\n';
PRINT '=' * 60;
PRINT '          模拟数据生成完成！';
PRINT '=' * 60;
PRINT '各表插入数据统计：';
PRINT '=' * 60;

SELECT 'User' AS TableName, COUNT(*) AS RecordCount FROM [User];
SELECT 'Region' AS TableName, COUNT(*) AS RecordCount FROM Region;
SELECT 'Sensor' AS TableName, COUNT(*) AS RecordCount FROM Sensor;
SELECT 'WarningRule' AS TableName, COUNT(*) AS RecordCount FROM WarningRule;
SELECT 'WarningRecord' AS TableName, COUNT(*) AS RecordCount FROM WarningRecord;
SELECT 'NotificationRecord' AS TableName, COUNT(*) AS RecordCount FROM NotificationRecord;
SELECT 'ForestResource' AS TableName, COUNT(*) AS RecordCount FROM ForestResource;
SELECT 'ResourceChangeRecord' AS TableName, COUNT(*) AS RecordCount FROM ResourceChangeRecord;
SELECT 'DeviceArchive' AS TableName, COUNT(*) AS RecordCount FROM DeviceArchive;
SELECT 'DeviceStatus' AS TableName, COUNT(*) AS RecordCount FROM DeviceStatus;
SELECT 'EquipmentInspection' AS TableName, COUNT(*) AS RecordCount FROM EquipmentInspection;
SELECT 'MaintenanceRecord' AS TableName, COUNT(*) AS RecordCount FROM MaintenanceRecord;
SELECT 'MonitoringData' AS TableName, COUNT(*) AS RecordCount FROM MonitoringData;
SELECT 'ReportTemplate' AS TableName, COUNT(*) AS RecordCount FROM ReportTemplate;
SELECT 'GeneratedReport' AS TableName, COUNT(*) AS RecordCount FROM GeneratedReport;

PRINT '=' * 60;
PRINT '模拟数据生成脚本执行完毕！';
PRINT '=' * 60;
GO

SET NOCOUNT OFF;
GO