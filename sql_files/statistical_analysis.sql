-- 统计分析业务线 - 报表模板表(ReportTemplate)
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ReportTemplate' AND type = 'U')
BEGIN
    CREATE TABLE ReportTemplate (
        TemplateID VARCHAR(20) PRIMARY KEY,
        ReportName VARCHAR(100) NOT NULL,
        ReportType VARCHAR(50) NOT NULL,
        StatisticalIndicators TEXT NOT NULL,
        Description TEXT,
        CreateTime DATETIME NOT NULL DEFAULT GETDATE(),
        -- 新增字段
        StatisticalDimension VARCHAR(100) NOT NULL, -- 统计维度（区域/时间/类型）
        GenerationCycle VARCHAR(20) NOT NULL, -- 生成周期（日/周/月）
        IsActive BIT NOT NULL DEFAULT 1, -- 是否启用
        AuditStatus VARCHAR(20) NOT NULL DEFAULT '待审核', -- 审核状态（待审核/已通过/已拒绝）
        AuditBy VARCHAR(20) NULL, -- 审核人
        AuditTime DATETIME NULL, -- 审核时间
        AuditComments TEXT NULL -- 审核意见
    )
END
ELSE
BEGIN
    -- 如果表已存在，添加缺少的字段
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('ReportTemplate') AND name = 'StatisticalDimension')
    BEGIN
        ALTER TABLE ReportTemplate ADD StatisticalDimension VARCHAR(100) NOT NULL DEFAULT '区域/时间/类型';
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('ReportTemplate') AND name = 'GenerationCycle')
    BEGIN
        ALTER TABLE ReportTemplate ADD GenerationCycle VARCHAR(20) NOT NULL DEFAULT '月';
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('ReportTemplate') AND name = 'IsActive')
    BEGIN
        ALTER TABLE ReportTemplate ADD IsActive BIT NOT NULL DEFAULT 1;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('ReportTemplate') AND name = 'AuditStatus')
    BEGIN
        ALTER TABLE ReportTemplate ADD AuditStatus VARCHAR(20) NOT NULL DEFAULT '待审核';
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('ReportTemplate') AND name = 'AuditBy')
    BEGIN
        ALTER TABLE ReportTemplate ADD AuditBy VARCHAR(20) NULL;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('ReportTemplate') AND name = 'AuditTime')
    BEGIN
        ALTER TABLE ReportTemplate ADD AuditTime DATETIME NULL;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('ReportTemplate') AND name = 'AuditComments')
    BEGIN
        ALTER TABLE ReportTemplate ADD AuditComments TEXT NULL;
    END
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
        GeneratedBy VARCHAR(20) NOT NULL FOREIGN KEY REFERENCES [User](UserID),
        IsPublished BIT NOT NULL DEFAULT 0,
        PublishTime DATETIME NULL,
        -- 新增字段
        StatisticalCycle VARCHAR(20) NOT NULL, -- 统计周期（如2024-10）
        DataSourceDescription TEXT NOT NULL -- 数据来源说明
    )
END
ELSE
BEGIN
    -- 如果表已存在，添加缺少的字段
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('GeneratedReport') AND name = 'IsPublished')
    BEGIN
        ALTER TABLE GeneratedReport ADD IsPublished BIT NOT NULL DEFAULT 0;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('GeneratedReport') AND name = 'PublishTime')
    BEGIN
        ALTER TABLE GeneratedReport ADD PublishTime DATETIME NULL;
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('GeneratedReport') AND name = 'StatisticalCycle')
    BEGIN
        ALTER TABLE GeneratedReport ADD StatisticalCycle VARCHAR(20) NOT NULL DEFAULT '';
    END
    
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('GeneratedReport') AND name = 'DataSourceDescription')
    BEGIN
        ALTER TABLE GeneratedReport ADD DataSourceDescription TEXT NOT NULL DEFAULT '';
    END
END
GO
