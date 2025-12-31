-- 资源管理业务线 - 林草资源表(ForestResource)
-- SQL Server版本
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ForestResource' AND type = 'U')
BEGIN
    CREATE TABLE ForestResource (
        ResourceID VARCHAR(20) PRIMARY KEY,
        region_id VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES region(region_id),
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
        OperatorID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES [User](UserID)
    )
END
GO
