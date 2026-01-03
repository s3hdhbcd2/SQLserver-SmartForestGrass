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

-- 示例数据
INSERT INTO Feedback (FeedbackID, FeedbackType, RegionID, Description, Contact, Status)
VALUES 
('FB0001', '火灾', 'R001', '发现华北林区有烟雾，可能发生火灾', '13800138000', '待处理'),
('FB0002', '病虫害', 'R002', '东北林区发现大量虫害', '13900139000', '已处理'),
('FB0003', '旱情', 'R006', '西北林区持续干旱，需要浇水', '13700137000', '待处理');
GO
