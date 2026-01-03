-- 统计分析业务线 - 报表模板表(ReportTemplate)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ReportTemplate' AND type = 'U')
BEGIN
    CREATE TABLE ReportTemplate (
        TemplateID VARCHAR(20) PRIMARY KEY,
        ReportName VARCHAR(100) NOT NULL,
        ReportType VARCHAR(50) NOT NULL,
        StatisticalIndicators TEXT NOT NULL,
        Description TEXT,
        CreateTime DATETIME NOT NULL DEFAULT GETDATE()
    )
END
GO

-- 统计分析业务线 - 生成报表表(GeneratedReport)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'GeneratedReport' AND type = 'U')
BEGIN
    CREATE TABLE GeneratedReport (
        ReportID VARCHAR(20) PRIMARY KEY,
        ReportName VARCHAR(100) NOT NULL,
        TemplateID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES ReportTemplate(TemplateID),
        RegionID VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES Region(RegionID),
        StartTime DATETIME NOT NULL,
        EndTime DATETIME NOT NULL,
        ReportContent TEXT NOT NULL,
        ReportFilePath VARCHAR(255) NOT NULL,
        GeneratedTime DATETIME NOT NULL DEFAULT GETDATE(),
        GeneratedBy VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES [User](UserID)
    )
END
GO
