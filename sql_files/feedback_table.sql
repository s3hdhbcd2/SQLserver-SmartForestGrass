-- 创建反馈表
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Feedback' AND type = 'U')
BEGIN
    CREATE TABLE Feedback (
        FeedbackID VARCHAR(20) PRIMARY KEY,
        FeedbackType VARCHAR(50) NOT NULL,
        RegionID VARCHAR(20) NOT NULL,
        Description TEXT NOT NULL,
        Contact VARCHAR(50) NOT NULL,
        SubmitTime DATETIME NOT NULL DEFAULT GETDATE(),
        Status VARCHAR(20) NOT NULL DEFAULT '待处理',
        HandlerID VARCHAR(20) NULL,
        HandleTime DATETIME NULL,
        HandleResult TEXT NULL,
        CONSTRAINT FK_Feedback_Region FOREIGN KEY (RegionID) REFERENCES Region(RegionID),
        CONSTRAINT FK_Feedback_Handler FOREIGN KEY (HandlerID) REFERENCES [User](UserID)
    );
    
    -- 创建索引
    CREATE INDEX IX_Feedback_Status ON Feedback(Status);
    CREATE INDEX IX_Feedback_RegionID ON Feedback(RegionID);
    CREATE INDEX IX_Feedback_SubmitTime ON Feedback(SubmitTime);
    CREATE INDEX IX_Feedback_HandlerID ON Feedback(HandlerID);
    
    PRINT '反馈表创建成功！';
END;
GO
