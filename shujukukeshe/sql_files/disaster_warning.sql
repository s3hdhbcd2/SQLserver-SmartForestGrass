-- 灾害预警业务线 - 预警规则表(WarningRule)
-- SQL Server版本
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'WarningRule' AND type = 'U')
BEGIN
    CREATE TABLE WarningRule (
        RuleID VARCHAR(20) PRIMARY KEY,
        WarningType VARCHAR(50) NOT NULL,
        TriggerCondition TEXT NOT NULL,
        WarningLevel VARCHAR(20) NOT NULL,
        IsActive BIT NOT NULL DEFAULT 1
    )
END
GO

-- 灾害预警业务线 - 预警记录表(WarningRecord)
-- SQL Server版本
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'WarningRecord' AND type = 'U')
BEGIN
    CREATE TABLE WarningRecord (
        WarningID VARCHAR(20) PRIMARY KEY,
        RuleID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES WarningRule(RuleID),
        RegionID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES Region(RegionID),
        TriggerTime DATETIME NOT NULL,
        WarningContent TEXT NOT NULL,
        Status VARCHAR(20) NOT NULL DEFAULT '未处理',
        HandlerID VARCHAR(20) FOREIGN KEY REFERENCES [User](UserID),
        HandleResult TEXT
    )
END
GO

-- 灾害预警业务线 - 通知记录表(NotificationRecord)
-- SQL Server版本
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'NotificationRecord' AND type = 'U')
BEGIN
    CREATE TABLE NotificationRecord (
        NotificationID VARCHAR(20) PRIMARY KEY,
        WarningID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES WarningRecord(WarningID),
        ReceiverID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES [User](UserID),
        NotificationMethod VARCHAR(20) NOT NULL,
        SendTime DATETIME NOT NULL,
        ReceiveStatus VARCHAR(20) NOT NULL DEFAULT '已发送'
    )
END
GO
