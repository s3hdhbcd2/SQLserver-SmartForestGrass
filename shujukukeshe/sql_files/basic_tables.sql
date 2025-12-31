-- 基础表 - 用户表(User)
-- SQL Server版本
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
    )
END
GO

-- 基础表 - 区域表(region)
-- SQL Server版本
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'region' AND type = 'U')
BEGIN
    CREATE TABLE region (
        region_id VARCHAR(20) PRIMARY KEY,
        region_name NVARCHAR(100) NOT NULL,
        region_type NVARCHAR(20) NOT NULL,
        longitude DECIMAL(10,6) NOT NULL,
        latitude DECIMAL(10,6) NOT NULL,
        manager_id VARCHAR(20) FOREIGN KEY REFERENCES [User](UserID),
        create_time DATETIME NOT NULL DEFAULT GETDATE()
    )
END
GO
