-- 资源管理业务线 - 林草资源表(ForestResource)
-- SQL Server版本
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ForestResource' AND type = 'U')
BEGIN
    CREATE TABLE ForestResource (
        ResourceID VARCHAR(20) PRIMARY KEY,
        RegionID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES Region(RegionID),
        ResourceType VARCHAR(50) NOT NULL,
        TreeSpecies VARCHAR(100),
        Quantity INT,
        CoverageArea DECIMAL(10,2),
        GrowthStatus VARCHAR(50) NOT NULL,
        PlantingTime DATETIME NOT NULL,
        UpdateTime DATETIME NOT NULL,
        UpdatedBy VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES [User](UserID)
    )
END
GO

-- 资源管理业务线 - 资源变动记录表(ResourceChangeRecord)
-- SQL Server版本
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ResourceChangeRecord' AND type = 'U')
BEGIN
    CREATE TABLE ResourceChangeRecord (
        ChangeID VARCHAR(20) PRIMARY KEY,
        ResourceID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES ForestResource(ResourceID),
        ChangeType VARCHAR(20) NOT NULL,
        ChangeReason TEXT NOT NULL,
        ChangeTime DATETIME NOT NULL,
        OperatorID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES [User](UserID),
        AuditStatus VARCHAR(20) NOT NULL DEFAULT '待审核',
        AuditorID VARCHAR(20) FOREIGN KEY REFERENCES [User](UserID),
        AuditTime DATETIME,
        AuditComments TEXT
    )
END
ELSE
BEGIN
    -- 添加审核相关字段
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE name = 'AuditStatus' AND object_id = OBJECT_ID('ResourceChangeRecord'))
    BEGIN
        ALTER TABLE ResourceChangeRecord ADD AuditStatus VARCHAR(20) NOT NULL DEFAULT '待审核'
    END
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE name = 'AuditorID' AND object_id = OBJECT_ID('ResourceChangeRecord'))
    BEGIN
        ALTER TABLE ResourceChangeRecord ADD AuditorID VARCHAR(20) FOREIGN KEY REFERENCES [User](UserID)
    END
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE name = 'AuditTime' AND object_id = OBJECT_ID('ResourceChangeRecord'))
    BEGIN
        ALTER TABLE ResourceChangeRecord ADD AuditTime DATETIME
    END
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE name = 'AuditComments' AND object_id = OBJECT_ID('ResourceChangeRecord'))
    BEGIN
        ALTER TABLE ResourceChangeRecord ADD AuditComments TEXT
    END
END
GO
