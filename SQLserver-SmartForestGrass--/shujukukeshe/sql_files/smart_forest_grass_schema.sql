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
        UserID VARCHAR(20) PRIMARY KEY,
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
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Region' AND type = 'U')
BEGIN
    CREATE TABLE Region (
        RegionID VARCHAR(20) PRIMARY KEY,
        RegionName NVARCHAR(100) NOT NULL,
        RegionType NVARCHAR(20) NOT NULL,
        Longitude DECIMAL(10,6) NOT NULL,
        Latitude DECIMAL(10,6) NOT NULL,
        ManagerID VARCHAR(20) FOREIGN KEY REFERENCES [User](UserID),
        CreateTime DATETIME NOT NULL DEFAULT GETDATE()
    );
END;
GO

-- 创建预警规则表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'WarningRule' AND type = 'U')
BEGIN
    CREATE TABLE WarningRule (
        RuleID VARCHAR(20) PRIMARY KEY,
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
        WarningID VARCHAR(20) PRIMARY KEY,
        RuleID VARCHAR(20) NOT NULL,
        RegionID VARCHAR(20) NOT NULL,
        TriggerTime DATETIME NOT NULL,
        WarningContent TEXT NOT NULL,
        Status VARCHAR(20) NOT NULL DEFAULT '未处理',
        HandlerID VARCHAR(20),
        HandleResult TEXT,
        CONSTRAINT FK_WarningRecord_WarningRule FOREIGN KEY (RuleID) REFERENCES WarningRule(RuleID),
        CONSTRAINT FK_WarningRecord_Region FOREIGN KEY (RegionID) REFERENCES Region(RegionID),
        CONSTRAINT FK_WarningRecord_Handler FOREIGN KEY (HandlerID) REFERENCES [User](UserID)
    );
END;
GO

-- 创建通知记录表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'NotificationRecord' AND type = 'U')
BEGIN
    CREATE TABLE NotificationRecord (
        NotificationID VARCHAR(20) PRIMARY KEY,
        WarningID VARCHAR(20) NOT NULL,
        ReceiverID VARCHAR(20) NOT NULL,
        NotificationMethod VARCHAR(20) NOT NULL,
        SendTime DATETIME NOT NULL,
        ReceiveStatus VARCHAR(20) NOT NULL DEFAULT '已发送',
        CONSTRAINT FK_NotificationRecord_WarningRecord FOREIGN KEY (WarningID) REFERENCES WarningRecord(WarningID),
        CONSTRAINT FK_NotificationRecord_Receiver FOREIGN KEY (ReceiverID) REFERENCES [User](UserID)
    );
END;
GO

-- 创建索引以提高查询性能（SQL Server不支持IF NOT EXISTS语法，直接创建索引）
CREATE INDEX IX_User_Username ON [User](Username);
CREATE INDEX IX_User_Role ON [User](Role);
CREATE INDEX IX_User_Status ON [User](Status);
CREATE INDEX IX_Region_ManagerID ON Region(ManagerID);
CREATE INDEX IX_Region_RegionType ON Region(RegionType);
CREATE INDEX IX_WarningRule_WarningType ON WarningRule(WarningType);
CREATE INDEX IX_WarningRecord_RuleID ON WarningRecord(RuleID);
CREATE INDEX IX_WarningRecord_RegionID ON WarningRecord(RegionID);
CREATE INDEX IX_WarningRecord_Status ON WarningRecord(Status);
CREATE INDEX IX_WarningRecord_HandlerID ON WarningRecord(HandlerID);
CREATE INDEX IX_NotificationRecord_WarningID ON NotificationRecord(WarningID);
CREATE INDEX IX_NotificationRecord_ReceiveStatus ON NotificationRecord(ReceiveStatus);
CREATE INDEX IX_NotificationRecord_ReceiverID ON NotificationRecord(ReceiverID);
GO

-- 示例数据已移至 sample_data.sql 文件中
-- 请运行 sample_data.sql 文件以插入示例数据


-- 常用查询语句示例
-- 1. 查询所有生效的预警规则
SELECT * FROM WarningRule WHERE IsActive = 1;

-- 2. 查询所有未处理的预警记录
SELECT * FROM WarningRecord WHERE Status = '未处理' ORDER BY TriggerTime DESC;

-- 3. 查询特定区域的预警记录
SELECT * FROM WarningRecord WHERE RegionID = 'R001' ORDER BY TriggerTime DESC;

-- 4. 查询特定预警的通知记录
SELECT * FROM NotificationRecord WHERE WarningID = 'WRC0001';

-- 5. 查询已阅读的通知记录
SELECT * FROM NotificationRecord WHERE ReceiveStatus = '已阅读';

-- 6. 统计不同类型的预警数量
SELECT WarningType, COUNT(*) AS WarningCount FROM WarningRule GROUP BY WarningType;

-- 7. 统计不同状态的预警记录数量
SELECT Status, COUNT(*) AS RecordCount FROM WarningRecord GROUP BY Status;
