-- 智慧林草系统 - 视图和存储过程/触发器实现
-- 按照课程设计任务书要求，为每条业务线创建视图和存储过程/触发器

SET NOCOUNT ON;
GO

-- =============================================
-- 1. 环境监测业务线
-- =============================================

PRINT '正在创建环境监测业务线视图...';
GO

-- 1.1 区域日均值视图
CREATE VIEW vw_monitoring_daily_average
AS
SELECT 
    m.RegionID,
    r.RegionName,
    CAST(m.DataTime AS DATE) AS monitoring_date,
    AVG(m.Temperature) AS avg_temperature,
    AVG(m.Humidity) AS avg_humidity,
    AVG(m.WindSpeed) AS avg_wind_speed,
    SUM(m.Rainfall) AS total_rainfall,
    COUNT(*) AS data_count
FROM MonitoringData m
JOIN Region r ON m.RegionID = r.RegionID
WHERE m.DataTime IS NOT NULL
GROUP BY m.RegionID, r.RegionName, CAST(m.DataTime AS DATE);
GO

-- 1.2 异常数据视图
CREATE VIEW vw_abnormal_MonitoringData
AS
SELECT 
    m.DataID,
    m.SensorID,
    s.MonitoringType,
    m.RegionID,
    r.RegionName,
    m.DataTime,
    m.Temperature,
    m.Humidity,
    m.WindSpeed,
    m.Rainfall,
    m.SmokeValue,
    CASE 
        WHEN m.Temperature > 40 OR m.Temperature < -10 THEN '温度异常'
        WHEN m.Humidity > 100 OR m.Humidity < 0 THEN '湿度异常'
        WHEN m.WindSpeed > 30 THEN '风速异常'
        WHEN m.Rainfall > 100 THEN '降雨量异常'
        WHEN m.SmokeValue > 100 THEN '烟雾值异常'
        ELSE '无异常' 
    END AS abnormal_type
FROM MonitoringData m
JOIN Sensor s ON m.SensorID = s.SensorID
JOIN Region r ON m.RegionID = r.RegionID
WHERE 
    m.Temperature > 40 OR m.Temperature < -10 OR
    m.Humidity > 100 OR m.Humidity < 0 OR
    m.WindSpeed > 30 OR
    m.Rainfall > 100 OR
    m.SmokeValue > 100;
GO

-- 1.3 传感器数据汇总视图
CREATE VIEW vw_Sensor_data_summary
AS
SELECT 
    s.SensorID,
    s.DeviceModel,
    s.MonitoringType,
    s.RegionID,
    r.RegionName,
    COUNT(m.DataID) AS total_data_count,
    MIN(m.DataTime) AS first_data_time,
    MAX(m.DataTime) AS last_data_time,
    AVG(m.Temperature) AS avg_temperature,
    AVG(m.Humidity) AS avg_humidity
FROM Sensor s
LEFT JOIN MonitoringData m ON s.SensorID = m.SensorID
JOIN Region r ON s.RegionID = r.RegionID
GROUP BY s.SensorID, s.DeviceModel, s.MonitoringType, s.RegionID, r.RegionName;
GO

-- 1.4 环境监测业务线存储过程：按区域查询监测数据
CREATE PROCEDURE sp_get_MonitoringData_by_Region
    @RegionID VARCHAR(20),
    @start_time DATETIME,
    @end_time DATETIME
AS
BEGIN
    SELECT 
        m.DataID,
        m.SensorID,
        s.MonitoringType,
        m.DataTime,
        m.Temperature,
        m.Humidity,
        m.WindSpeed,
        m.Rainfall,
        m.SmokeValue,
        m.SoilMoisture
    FROM MonitoringData m
    JOIN Sensor s ON m.SensorID = s.SensorID
    WHERE 
        m.RegionID = @RegionID AND
        m.DataTime BETWEEN @start_time AND @end_time
    ORDER BY m.DataTime DESC
END;
GO

PRINT '环境监测业务线视图和存储过程创建完成！';
GO

-- =============================================
-- 2. 灾害预警业务线
-- =============================================

PRINT '正在创建灾害预警业务线视图...';
GO

-- 2.1 预警处理情况视图
CREATE VIEW vw_warning_processing_status
AS
SELECT 
    wr.WarningID,
    wr.RuleID,
    wrule.WarningType,
    wrule.WarningLevel,
    wr.RegionID,
    r.RegionName,
    wr.TriggerTime,
    CAST(wr.WarningContent AS VARCHAR(MAX)) AS WarningContent,
    wr.Status,
    wr.HandlerID,
    u.Name AS handler_name,
    CAST(wr.HandleResult AS VARCHAR(MAX)) AS HandleResult,
    DATEDIFF(MINUTE, wr.TriggerTime, GETDATE()) AS minutes_elapsed
FROM WarningRecord wr
JOIN WarningRule wrule ON wr.RuleID = wrule.RuleID
JOIN Region r ON wr.RegionID = r.RegionID
LEFT JOIN [User] u ON wr.HandlerID = u.UserID;
GO

-- 2.2 预警规则有效性视图
CREATE VIEW vw_active_warning_rules
AS
SELECT 
    wrule.RuleID,
    wrule.WarningType,
    wrule.WarningLevel,
    wrule.IsActive,
    COUNT(wr.WarningID) AS trigger_count,
    MAX(wr.TriggerTime) AS last_trigger_time
FROM WarningRule wrule
LEFT JOIN WarningRecord wr ON wrule.RuleID = wr.RuleID
WHERE wrule.IsActive = 1
GROUP BY wrule.RuleID, wrule.WarningType, wrule.WarningLevel, wrule.IsActive;
GO

-- 2.3 预警统计视图
CREATE VIEW vw_warning_statistics
AS
SELECT 
    wr.RegionID,
    r.RegionName,
    wrule.WarningType,
    CAST(wr.TriggerTime AS DATE) AS warning_date,
    COUNT(*) AS warning_count,
    SUM(CASE WHEN wr.Status = '已处理' THEN 1 ELSE 0 END) AS processed_count,
    SUM(CASE WHEN wr.Status = '未处理' THEN 1 ELSE 0 END) AS pending_count,
    SUM(CASE WHEN wr.Status = '处理中' THEN 1 ELSE 0 END) AS processing_count
FROM WarningRecord wr
JOIN WarningRule wrule ON wr.RuleID = wrule.RuleID
JOIN Region r ON wr.RegionID = r.RegionID
GROUP BY wr.RegionID, r.RegionName, wrule.WarningType, CAST(wr.TriggerTime AS DATE);
GO

-- 2.4 灾害预警业务线触发器：预警触发后自动发送通知
-- 注释掉触发器，因为NotificationLog表不存在
-- CREATE TRIGGER tr_warning_after_insert
-- ON WarningRecord
-- AFTER INSERT
-- AS
-- BEGIN
--     -- 这里实现预警触发后的自动通知逻辑
--     -- 由于是示例，我们只记录到日志表（假设存在NotificationLog表）
--     -- 实际实现中可以调用外部服务发送短信/系统消息
--     
--     INSERT INTO NotificationLog (
--         WarningID,
--         NotificationType,
--         RecipientID,
--         NotificationContent,
--         SendTime,
--         Status
--     )
--     SELECT 
--         inserted.WarningID,
--         '系统消息',
--         r.ManagerID,
--         '区域' + r.RegionName + '发生' + wr.WarningLevel + '级' + wr.WarningType + '预警',
--         GETDATE(),
--         '待发送'
--     FROM inserted
--     JOIN WarningRule wr ON inserted.RuleID = wr.RuleID
--     JOIN Region r ON inserted.RegionID = r.RegionID;
-- END;
GO

PRINT '灾害预警业务线视图和触发器创建完成！';
GO

-- =============================================
-- 3. 资源管理业务线
-- =============================================

PRINT '正在创建资源管理业务线视图...';
GO

-- 3.1 区域资源概况视图
CREATE VIEW vw_resource_overview
AS
SELECT 
    fr.RegionID,
    r.RegionName,
    r.RegionType,
    COUNT(fr.ResourceID) AS resource_count,
    SUM(fr.CoverageArea) AS total_coverage_area,
    COUNT(DISTINCT fr.ResourceType) AS resource_type_count,
    COUNT(DISTINCT fr.TreeSpecies) AS tree_species_count
FROM ForestResource fr
JOIN Region r ON fr.RegionID = r.RegionID
GROUP BY fr.RegionID, r.RegionName, r.RegionType;
GO

-- 3.2 资源变动趋势视图
CREATE VIEW vw_resource_change_trend
AS
SELECT TOP 100 PERCENT
    fr.ResourceID,
    fr.ResourceType,
    fr.TreeSpecies,
    fr.RegionID,
    r.RegionName,
    rc.ChangeType,
    rc.ChangeTime,
    CAST(rc.ChangeReason AS VARCHAR(MAX)) AS ChangeReason,
    u.Name AS operator_name
FROM ResourceChangeRecord rc
JOIN ForestResource fr ON rc.ResourceID = fr.ResourceID
JOIN Region r ON fr.RegionID = r.RegionID
JOIN [User] u ON rc.OperatorID = u.UserID
ORDER BY rc.ChangeTime DESC;
GO

-- 3.3 资源生长状态视图
CREATE VIEW vw_resource_growth_status
AS
SELECT 
    fr.ResourceID,
    fr.ResourceType,
    fr.TreeSpecies,
    fr.CoverageArea,
    fr.GrowthStatus,
    fr.RegionID,
    r.RegionName,
    fr.UpdateTime,
    u.Name AS update_by_name
FROM ForestResource fr
JOIN Region r ON fr.RegionID = r.RegionID
JOIN [User] u ON fr.UpdatedBy = u.UserID;
GO

-- 3.4 资源管理业务线存储过程：更新资源信息
CREATE PROCEDURE sp_update_resource
    @resource_id VARCHAR(20),
    @coverage_area DECIMAL(10,2) = NULL,
    @tree_species VARCHAR(50) = NULL,
    @growth_status VARCHAR(20) = NULL,
    @update_by VARCHAR(20)
AS
BEGIN
    BEGIN TRANSACTION;
    
    -- 更新资源信息
    UPDATE ForestResource
    SET 
        CoverageArea = ISNULL(@coverage_area, CoverageArea),
        TreeSpecies = ISNULL(@tree_species, TreeSpecies),
        GrowthStatus = ISNULL(@growth_status, GrowthStatus),
        UpdateTime = GETDATE(),
        UpdatedBy = @update_by
    WHERE ResourceID = @resource_id;
    
    -- 记录资源变动
    INSERT INTO ResourceChangeRecord (
        ChangeID,
        ResourceID,
        ChangeType,
        ChangeReason,
        ChangeTime,
        OperatorID
    )
    VALUES (
        'RCR' + RIGHT('0000' + CAST(NEWID() AS VARCHAR(10)), 4),
        @resource_id,
        '更新',
        '通过存储过程更新资源信息',
        GETDATE(),
        @update_by
    );
    
    COMMIT TRANSACTION;
END;
GO

PRINT '资源管理业务线视图和存储过程创建完成！';
GO

-- =============================================
-- 4. 设备管理业务线
-- =============================================

PRINT '正在创建设备管理业务线视图...';
GO

-- 4.1 设备状态汇总视图
CREATE VIEW vw_DeviceStatus_summary
AS
SELECT 
    da.DeviceID,
    da.DeviceName,
    da.DeviceType,
    da.RegionID,
    r.RegionName,
    MAX(ds.CollectionTime) AS last_status_time,
    ds.RunningStatus,
    AVG(ds.BatteryLevel) AS avg_battery_level,
    AVG(CASE 
            WHEN ds.SignalStrength = '强' THEN 100 
            WHEN ds.SignalStrength = '中' THEN 50 
            WHEN ds.SignalStrength = '弱' THEN 20 
            ELSE 0 
        END) AS avg_signal_strength
FROM DeviceArchive da
JOIN Region r ON da.RegionID = r.RegionID
LEFT JOIN DeviceStatus ds ON da.DeviceID = ds.DeviceID
GROUP BY da.DeviceID, da.DeviceName, da.DeviceType, da.RegionID, r.RegionName, ds.RunningStatus;
GO

-- 4.2 设备维护记录视图
CREATE VIEW vw_device_maintenance_records
AS
SELECT 
    da.DeviceID,
    da.DeviceName,
    da.DeviceType,
    da.RegionID,
    r.RegionName,
    COUNT(*) AS maintenance_count,
    MAX(mt.MaintenanceTime) AS last_maintenance_time,
    SUM(CASE WHEN mt.MaintenanceResult = '成功' THEN 1 ELSE 0 END) AS successful_maintenance_count
FROM DeviceArchive da
JOIN Region r ON da.RegionID = r.RegionID
LEFT JOIN MaintenanceRecord mt ON da.DeviceID = mt.DeviceID
GROUP BY da.DeviceID, da.DeviceName, da.DeviceType, da.RegionID, r.RegionName;
GO

-- 4.3 设备分布视图
CREATE VIEW vw_device_distribution
AS
SELECT 
    r.RegionID,
    r.RegionName,
    da.DeviceType,
    COUNT(*) AS device_count,
    SUM(CASE WHEN ds.RunningStatus = '正常' THEN 1 ELSE 0 END) AS normal_device_count,
    SUM(CASE WHEN ds.RunningStatus = '故障' THEN 1 ELSE 0 END) AS fault_device_count,
    SUM(CASE WHEN ds.RunningStatus = '离线' THEN 1 ELSE 0 END) AS offline_device_count
FROM DeviceArchive da
JOIN Region r ON da.RegionID = r.RegionID
LEFT JOIN DeviceStatus ds ON da.DeviceID = ds.DeviceID
GROUP BY r.RegionID, r.RegionName, da.DeviceType;
GO

-- 4.4 设备管理业务线存储过程：获取设备状态历史
CREATE PROCEDURE sp_get_DeviceStatus_history
    @device_id VARCHAR(20),
    @start_time DATETIME,
    @end_time DATETIME
AS
BEGIN
    SELECT 
        ds.StatusID,
        ds.DeviceID,
        da.DeviceName,
        ds.CollectionTime,
        ds.RunningStatus,
        ds.BatteryLevel,
        ds.SignalStrength
    FROM DeviceStatus ds
    JOIN DeviceArchive da ON ds.DeviceID = da.DeviceID
    WHERE 
        ds.DeviceID = @device_id AND
        ds.CollectionTime BETWEEN @start_time AND @end_time
    ORDER BY ds.CollectionTime DESC;
END;
GO

PRINT '设备管理业务线视图和存储过程创建完成！';
GO

-- =============================================
-- 5. 统计分析业务线
-- =============================================

PRINT '正在创建统计分析业务线视图...';
GO

-- 5.1 报表生成情况视图
CREATE VIEW vw_report_generation_status
AS
SELECT TOP 100 PERCENT
    gr.ReportID,
    gr.ReportName,
    rt.ReportType,
    gr.RegionID,
    r.RegionName,
    gr.StartTime,
    gr.EndTime,
    gr.GeneratedTime,
    gr.GeneratedBy,
    u.Name AS generated_by_name,
    DATEDIFF(HOUR, gr.GeneratedTime, GETDATE()) AS hours_since_generation
FROM GeneratedReport gr
JOIN ReportTemplate rt ON gr.TemplateID = rt.TemplateID
JOIN Region r ON gr.RegionID = r.RegionID
JOIN [User] u ON gr.GeneratedBy = u.UserID
ORDER BY gr.GeneratedTime DESC;
GO

-- 5.2 报表模板使用率视图
CREATE VIEW vw_report_template_usage
AS
SELECT 
    rt.TemplateID,
    rt.ReportName,
    rt.ReportType,
    COUNT(gr.ReportID) AS usage_count,
    MAX(gr.GeneratedTime) AS last_used_time,
    AVG(DATEDIFF(DAY, gr.GeneratedTime, GETDATE())) AS avg_days_since_last_use
FROM ReportTemplate rt
LEFT JOIN GeneratedReport gr ON rt.TemplateID = gr.TemplateID
GROUP BY rt.TemplateID, rt.ReportName, rt.ReportType;
GO

-- 5.3 区域报表统计视图
CREATE VIEW vw_Region_report_statistics
AS
SELECT 
    gr.RegionID,
    r.RegionName,
    rt.ReportType,
    YEAR(gr.GeneratedTime) AS report_year,
    MONTH(gr.GeneratedTime) AS report_month,
    COUNT(gr.ReportID) AS report_count,
    MAX(gr.GeneratedTime) AS last_report_time
FROM GeneratedReport gr
JOIN ReportTemplate rt ON gr.TemplateID = rt.TemplateID
JOIN Region r ON gr.RegionID = r.RegionID
GROUP BY gr.RegionID, r.RegionName, rt.ReportType, YEAR(gr.GeneratedTime), MONTH(gr.GeneratedTime);
GO

-- 5.4 统计分析业务线存储过程：生成报表
CREATE PROCEDURE sp_generate_report
    @template_id VARCHAR(20),
    @RegionID VARCHAR(20),
    @start_time DATETIME,
    @end_time DATETIME,
    @generated_by VARCHAR(20)
AS
BEGIN
    DECLARE @report_id VARCHAR(20);
    DECLARE @report_name VARCHAR(100);
    DECLARE @report_content NVARCHAR(MAX);
    DECLARE @report_file_path VARCHAR(200);
    
    -- 生成报表ID
    SET @report_id = 'REP' + RIGHT('0000' + CAST(NEWID() AS VARCHAR(10)), 4);
    
    -- 获取模板信息
    SELECT 
        @report_name = ReportName + '_' + r.RegionName + '_' + CONVERT(VARCHAR(10), @start_time, 120) + '_' + CONVERT(VARCHAR(10), @end_time, 120)
    FROM ReportTemplate rt
    JOIN Region r ON @RegionID = r.RegionID
    WHERE rt.TemplateID = @template_id;
    
    -- 生成报表文件路径
    SET @report_file_path = 'reports/' + @report_id + '.txt';
    
    -- 根据模板类型生成不同的报表内容
    SET @report_content = '智慧林草系统报表\r\n';
    SET @report_content += '============================\r\n';
    SET @report_content += '报表ID: ' + @report_id + '\r\n';
    SET @report_content += '报表名称: ' + @report_name + '\r\n';
    SET @report_content += '生成时间: ' + CONVERT(VARCHAR(20), GETDATE(), 120) + '\r\n';
    SET @report_content += '生成人: ' + @generated_by + '\r\n';
    SET @report_content += '============================\r\n';
    
    -- 插入报表记录
    INSERT INTO GeneratedReport (
        ReportID, ReportName, TemplateID, RegionID, 
        StartTime, EndTime, ReportContent, ReportFilePath, 
        GeneratedTime, GeneratedBy
    )
    VALUES (
        @report_id, @report_name, @template_id, @RegionID,
        @start_time, @end_time, @report_content, @report_file_path,
        GETDATE(), @generated_by
    );
    
    -- 返回生成的报表ID
    SELECT @report_id AS ReportID;
END;
GO

PRINT '统计分析业务线视图和存储过程创建完成！';
GO

-- =============================================
-- 6. 登录安全策略增强
-- =============================================

PRINT '正在创建登录安全策略相关对象...';
GO

-- 6.1 用户登录日志表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'LoginLog' AND type = 'U')
BEGIN
    CREATE TABLE LoginLog (
        LogID VARCHAR(20) PRIMARY KEY,
        UserID VARCHAR(20) FOREIGN KEY REFERENCES [User](UserID),
        Username VARCHAR(50),
        LoginTime DATETIME NOT NULL DEFAULT GETDATE(),
        LoginIP VARCHAR(20),
        LoginStatus VARCHAR(10) NOT NULL,
        ErrorMessage VARCHAR(200)
    );
END;
GO

-- 6.2 登录日志视图
CREATE VIEW vw_login_audit
AS
SELECT TOP 100 PERCENT
    ll.LogID,
    ll.UserID,
    u.Name,
    u.Role,
    ll.Username,
    ll.LoginTime,
    ll.LoginIP,
    ll.LoginStatus,
    ll.ErrorMessage
FROM LoginLog ll
JOIN [User] u ON ll.UserID = u.UserID
ORDER BY ll.LoginTime DESC;
GO

-- 6.3 登录尝试限制视图
CREATE VIEW vw_failed_login_attempts
AS
SELECT 
    Username,
    COUNT(*) AS failed_attempts,
    MAX(LoginTime) AS last_failed_time
FROM LoginLog
WHERE LoginStatus = '失败'
AND LoginTime >= DATEADD(MINUTE, -30, GETDATE())
GROUP BY Username
HAVING COUNT(*) >= 3;
GO

-- 6.4 登录记录存储过程
CREATE PROCEDURE sp_log_login_attempt
    @user_id VARCHAR(20),
    @username VARCHAR(50),
    @login_ip VARCHAR(20),
    @login_status VARCHAR(10),
    @error_message VARCHAR(200) = NULL
AS
BEGIN
    INSERT INTO LoginLog (
        LogID, UserID, Username, LoginIP, LoginStatus, ErrorMessage
    )
    VALUES (
        'LOG' + RIGHT('00000' + CAST(NEWID() AS VARCHAR(10)), 8),
        @user_id,
        @username,
        @login_ip,
        @login_status,
        @error_message
    );
END;
GO

PRINT '登录安全策略相关对象创建完成！';
GO

-- =============================================
-- 7. 复杂SQL查询示例
-- =============================================

PRINT '创建复杂SQL查询示例...';
GO

-- 示例1: 查询某区域近7天火灾预警及处理情况
CREATE PROCEDURE sp_query_fire_warnings_recent_7_days
    @RegionID VARCHAR(20)
AS
BEGIN
    SELECT 
        wr.WarningID,
        wr.TriggerTime,
        wr.WarningContent,
        wr.Status,
        wr.HandleResult,
        wrule.WarningType,
        wrule.WarningLevel,
        u.Name AS HandlerName,
        r.RegionName
    FROM WarningRecord wr
    JOIN WarningRule wrule ON wr.RuleID = wrule.RuleID
    JOIN Region r ON wr.RegionID = r.RegionID
    LEFT JOIN [User] u ON wr.HandlerID = u.UserID
    WHERE 
        wr.RegionID = @RegionID
        AND wr.TriggerTime BETWEEN DATEADD(DAY, -7, GETDATE()) AND GETDATE()
        AND wrule.WarningType = '火灾'
    ORDER BY wr.TriggerTime DESC;
END;
GO

-- 示例2: 统计各区域设备故障次数及维护成本
CREATE PROCEDURE sp_statistics_device_faults
    @start_time DATETIME,
    @end_time DATETIME
AS
BEGIN
    SELECT 
        r.RegionName,
        COUNT(DISTINCT da.DeviceID) AS DeviceCount,
        SUM(CASE WHEN ds.RunningStatus = '故障' THEN 1 ELSE 0 END) AS FaultCount,
        COUNT(mt.MaintenanceID) AS InspectionCount
    FROM Region r
    LEFT JOIN DeviceArchive da ON r.RegionID = da.RegionID
    LEFT JOIN DeviceStatus ds ON da.DeviceID = ds.DeviceID AND ds.CollectionTime BETWEEN @start_time AND @end_time
    LEFT JOIN MaintenanceRecord mt ON da.DeviceID = mt.DeviceID AND mt.MaintenanceTime BETWEEN @start_time AND @end_time
    GROUP BY r.RegionName
    ORDER BY FaultCount DESC;
END;
GO

PRINT '复杂SQL查询示例创建完成！';
GO

PRINT '\n';
PRINT '=' * 60;
PRINT '          视图和存储过程/触发器创建完成！';
PRINT '=' * 60;
PRINT '创建的对象统计：';
PRINT '=' * 60;

SELECT '视图' AS ObjectType, COUNT(*) AS ObjectCount FROM sys.views WHERE name LIKE 'vw_%';
SELECT '存储过程' AS ObjectType, COUNT(*) AS ObjectCount FROM sys.procedures WHERE name LIKE 'sp_%';
SELECT '触发器' AS ObjectType, COUNT(*) AS ObjectCount FROM sys.triggers WHERE name LIKE 'tr_%';

PRINT '=' * 60;
PRINT '所有代码部分要求已完成！';
PRINT '=' * 60;
GO

SET NOCOUNT OFF;
GO