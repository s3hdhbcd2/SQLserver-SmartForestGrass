-- 智慧林草系统-灾害预警业务线数据库设计
-- SQL Server版本

-- 创建数据库（如果不存在）
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'SmartForestGrass')
BEGIN
    CREATE DATABASE SmartForestGrass;
END;
GO

-- 使用创建的数据库
USE SmartForestGrass;
GO

-- 创建用户表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'User' AND type = 'U')
BEGIN
    CREATE TABLE [User] (
        UserID BIGINT NOT NULL PRIMARY KEY,
        Username VARCHAR(50) NOT NULL UNIQUE,
        Password VARCHAR(100) NOT NULL,
        Name VARCHAR(50) NOT NULL,
        Contact VARCHAR(50) NOT NULL,
        Role VARCHAR(20) NOT NULL,
        Status VARCHAR(20) NOT NULL DEFAULT '启用'
    );
END;
GO

-- 创建区域表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'region' AND type = 'U')
BEGIN
    CREATE TABLE region (
        region_id BIGINT NOT NULL PRIMARY KEY,
        region_name NVARCHAR(100) NOT NULL,
        region_type NVARCHAR(20) NOT NULL,
        longitude DECIMAL(10,6) NOT NULL,
        latitude DECIMAL(10,6) NOT NULL,
        manager_id BIGINT NOT NULL,
        create_time DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT FK_region_Manager FOREIGN KEY (manager_id) REFERENCES [User](UserID)
    );
END;
GO

-- 创建预警规则表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'WarningRule' AND type = 'U')
BEGIN
    CREATE TABLE WarningRule (
        RuleID VARCHAR(30) PRIMARY KEY,
        WarningType VARCHAR(50) NOT NULL,
        TriggerCondition TEXT NOT NULL,
        WarningLevel VARCHAR(20) NOT NULL,
        IsActive BIT NOT NULL DEFAULT 1
    );
END;
GO

-- 创建预警记录表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'WarningRecord' AND type = 'U')
BEGIN
    CREATE TABLE WarningRecord (
        WarningID VARCHAR(30) PRIMARY KEY,
        RuleID VARCHAR(30) NOT NULL,
        region_id BIGINT NOT NULL,
        TriggerTime DATETIME NOT NULL,
        WarningContent TEXT NOT NULL,
        Status VARCHAR(20) NOT NULL DEFAULT '未处理',
        HandlerID VARCHAR(20),
        HandleResult TEXT,
        CONSTRAINT FK_WarningRecord_WarningRule FOREIGN KEY (RuleID) REFERENCES WarningRule(RuleID),
        CONSTRAINT FK_WarningRecord_region FOREIGN KEY (region_id) REFERENCES region(region_id),
        CONSTRAINT FK_WarningRecord_Handler FOREIGN KEY (HandlerID) REFERENCES [User](UserID)
    );
END;
GO

-- 创建通知记录表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'NotificationRecord' AND type = 'U')
BEGIN
    CREATE TABLE NotificationRecord (
        NotificationID VARCHAR(30) PRIMARY KEY,
        WarningID VARCHAR(30) NOT NULL,
        ReceiverID VARCHAR(20) NOT NULL,
        NotificationMethod VARCHAR(20) NOT NULL,
        SendTime DATETIME NOT NULL,
        ReceiveStatus VARCHAR(20) NOT NULL DEFAULT '已发送',
        CONSTRAINT FK_NotificationRecord_WarningRecord FOREIGN KEY (WarningID) REFERENCES WarningRecord(WarningID),
        CONSTRAINT FK_NotificationRecord_Receiver FOREIGN KEY (ReceiverID) REFERENCES [User](UserID)
    );
END;
GO

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS IX_User_Username ON [User](Username);
CREATE INDEX IF NOT EXISTS IX_User_Role ON [User](Role);
CREATE INDEX IF NOT EXISTS IX_User_Status ON [User](Status);
CREATE INDEX IF NOT EXISTS IX_region_ManagerID ON region(manager_id);
CREATE INDEX IF NOT EXISTS IX_region_regionType ON region(region_type);
CREATE INDEX IF NOT EXISTS IX_WarningRule_WarningType ON WarningRule(WarningType);
CREATE INDEX IF NOT EXISTS IX_WarningRecord_RuleID ON WarningRecord(RuleID);
CREATE INDEX IF NOT EXISTS IX_WarningRecord_regionID ON WarningRecord(region_id);
CREATE INDEX IF NOT EXISTS IX_WarningRecord_Status ON WarningRecord(Status);
CREATE INDEX IF NOT EXISTS IX_WarningRecord_HandlerID ON WarningRecord(HandlerID);
CREATE INDEX IF NOT EXISTS IX_NotificationRecord_WarningID ON NotificationRecord(WarningID);
CREATE INDEX IF NOT EXISTS IX_NotificationRecord_ReceiveStatus ON NotificationRecord(ReceiveStatus);
CREATE INDEX IF NOT EXISTS IX_NotificationRecord_ReceiverID ON NotificationRecord(ReceiverID);
GO

-- 示例数据已移至 sample_data.sql 文件中
-- 请运行 sample_data.sql 文件以插入示例数据


-- 常用查询语句示例
-- 1. 查询所有生效的预警规则
SELECT * FROM WarningRule WHERE IsActive = 1;

-- 2. 查询所有未处理的预警记录
SELECT * FROM WarningRecord WHERE Status = '未处理' ORDER BY TriggerTime DESC;

-- 3. 查询特定区域的预警记录
SELECT * FROM WarningRecord WHERE region_id = 20251230120000 ORDER BY TriggerTime DESC;

-- 4. 查询特定预警的通知记录
SELECT * FROM NotificationRecord WHERE WarningID = 'WARN20251230000001';

-- 5. 查询已阅读的通知记录
SELECT * FROM NotificationRecord WHERE ReceiveStatus = '已阅读';

-- 6. 统计不同类型的预警数量
SELECT WarningType, COUNT(*) AS WarningCount FROM WarningRule GROUP BY WarningType;

-- 7. 统计不同状态的预警记录数量
SELECT Status, COUNT(*) AS RecordCount FROM WarningRecord GROUP BY Status;
