-- 环境监测业务线 - 传感器表(Sensor)
-- SQL Server版本
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Sensor' AND type = 'U')
BEGIN
    CREATE TABLE Sensor (
        SensorID VARCHAR(20) PRIMARY KEY,
        RegionID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES Region(RegionID),
        DeviceModel VARCHAR(50) NOT NULL,
        MonitoringType VARCHAR(20) NOT NULL,
        InstallTime DATETIME NOT NULL,
        CommunicationProtocol VARCHAR(20) NOT NULL
    )
END
GO

-- 环境监测业务线 - 监测数据表(MonitoringData)
-- SQL Server版本
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'MonitoringData' AND type = 'U')
BEGIN
    CREATE TABLE MonitoringData (
        DataID VARCHAR(20) PRIMARY KEY,
        SensorID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES Sensor(SensorID),
        RegionID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES Region(RegionID),
        DataTime DATETIME NOT NULL,
        Temperature DECIMAL(5,2),
        Humidity DECIMAL(5,2),
        WindSpeed DECIMAL(5,2),
        Rainfall DECIMAL(5,2),
        PestDiseaseValue INT,
        SmokeValue INT,
        SoilMoisture DECIMAL(5,2),
        ImagePath VARCHAR(255),
        DataStatus VARCHAR(20) NOT NULL DEFAULT '有效'
    )
END
GO
