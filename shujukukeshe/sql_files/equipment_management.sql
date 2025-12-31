-- 设备管理业务线 - 设备档案表(DeviceArchive)
-- SQL Server版本
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DeviceArchive' AND type = 'U')
BEGIN
    CREATE TABLE DeviceArchive (
        DeviceID VARCHAR(20) PRIMARY KEY,
        DeviceName VARCHAR(100) NOT NULL,
        DeviceType VARCHAR(20) NOT NULL,
        ModelSpecification VARCHAR(100) NOT NULL,
        PurchaseTime DATETIME NOT NULL,
        region_id VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES region(region_id),
        InstallerID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES [User](UserID),
        WarrantyPeriod VARCHAR(20) NOT NULL
    )
END
GO

-- 设备管理业务线 - 设备状态表(DeviceStatus)
-- SQL Server版本
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DeviceStatus' AND type = 'U')
BEGIN
    CREATE TABLE DeviceStatus (
        StatusID VARCHAR(20) PRIMARY KEY,
        DeviceID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES DeviceArchive(DeviceID),
        CollectionTime DATETIME NOT NULL,
        RunningStatus VARCHAR(20) NOT NULL,
        BatteryLevel DECIMAL(5,2),
        SignalStrength INT
    )
END
GO

-- 设备管理业务线 - 设备巡检记录表(EquipmentInspection)
-- SQL Server版本
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'EquipmentInspection' AND type = 'U')
BEGIN
    CREATE TABLE EquipmentInspection (
        InspectionID VARCHAR(20) PRIMARY KEY,
        DeviceID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES DeviceArchive(DeviceID),
        InspectionTime DATETIME NOT NULL,
        InspectorID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES [User](UserID),
        MaintenanceType VARCHAR(20) NOT NULL,
        InspectionResult VARCHAR(20) NOT NULL,
        ProblemDescription TEXT,
        MaintenanceContent TEXT,
        MaintenanceResult TEXT
    )
END
GO

-- 设备管理业务线 - 维护记录表(MaintenanceRecord)
-- SQL Server版本
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'MaintenanceRecord' AND type = 'U')
BEGIN
    CREATE TABLE MaintenanceRecord (
        MaintenanceID VARCHAR(20) PRIMARY KEY,
        DeviceID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES DeviceArchive(DeviceID),
        MaintenanceType VARCHAR(20) NOT NULL,
        MaintenanceTime DATETIME NOT NULL,
        MaintainerID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES [User](UserID),
        MaintenanceContent TEXT,
        MaintenanceResult TEXT
    )
END
GO
