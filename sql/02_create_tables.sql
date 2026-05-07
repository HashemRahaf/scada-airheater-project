USE SCADA_AirHeater;
GO

IF OBJECT_ID('dbo.Measurement', 'U') IS NOT NULL DROP TABLE dbo.Measurement;
IF OBJECT_ID('dbo.AlarmEvent', 'U') IS NOT NULL DROP TABLE dbo.AlarmEvent;
IF OBJECT_ID('dbo.AlarmDefinition', 'U') IS NOT NULL DROP TABLE dbo.AlarmDefinition;
IF OBJECT_ID('dbo.OPCUATagMap', 'U') IS NOT NULL DROP TABLE dbo.OPCUATagMap;
IF OBJECT_ID('dbo.Tag', 'U') IS NOT NULL DROP TABLE dbo.Tag;
GO

CREATE TABLE dbo.Tag (
    TagID INT IDENTITY(1,1) PRIMARY KEY,
    TagName NVARCHAR(100) NOT NULL UNIQUE,
    Description NVARCHAR(200) NULL,
    Unit NVARCHAR(20) NULL,
    DataType NVARCHAR(20) NOT NULL,
    IsActive BIT NOT NULL DEFAULT 1
);
GO

CREATE TABLE dbo.Measurement (
    MeasurementID BIGINT IDENTITY(1,1) PRIMARY KEY,
    TagID INT NOT NULL,
    TimestampUTC DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    Value FLOAT NOT NULL,
    QualityFlag NVARCHAR(20) NOT NULL DEFAULT 'Good',
    CONSTRAINT FK_Measurement_Tag FOREIGN KEY (TagID) REFERENCES dbo.Tag(TagID)
);
GO

CREATE TABLE dbo.OPCUATagMap (
    OPCUATagMapID INT IDENTITY(1,1) PRIMARY KEY,
    TagID INT NOT NULL UNIQUE,
    NamespaceURI NVARCHAR(255) NOT NULL,
    NodeId NVARCHAR(255) NOT NULL,
    BrowsePath NVARCHAR(255) NOT NULL,
    CONSTRAINT FK_OPCUATagMap_Tag FOREIGN KEY (TagID) REFERENCES dbo.Tag(TagID)
);
GO

CREATE TABLE dbo.AlarmDefinition (
    AlarmDefinitionID INT IDENTITY(1,1) PRIMARY KEY,
    AlarmName NVARCHAR(120) NOT NULL UNIQUE,
    TagID INT NOT NULL,
    Priority NVARCHAR(20) NOT NULL,
    ConditionText NVARCHAR(200) NOT NULL,
    LimitValue FLOAT NULL,
    IsEnabled BIT NOT NULL DEFAULT 1,
    CONSTRAINT FK_AlarmDefinition_Tag FOREIGN KEY (TagID) REFERENCES dbo.Tag(TagID)
);
GO

CREATE TABLE dbo.AlarmEvent (
    AlarmEventID BIGINT IDENTITY(1,1) PRIMARY KEY,
    AlarmDefinitionID INT NOT NULL,
    StartTimeUTC DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    EndTimeUTC DATETIME2 NULL,
    AlarmValue FLOAT NULL,
    Status NVARCHAR(20) NOT NULL DEFAULT 'Active',
    Acknowledged BIT NOT NULL DEFAULT 0,
    AcknowledgedBy NVARCHAR(100) NULL,
    AcknowledgedTimeUTC DATETIME2 NULL,
    CONSTRAINT FK_AlarmEvent_AlarmDefinition FOREIGN KEY (AlarmDefinitionID)
        REFERENCES dbo.AlarmDefinition(AlarmDefinitionID)
);
GO

CREATE INDEX IX_Measurement_TagID_TimestampUTC
    ON dbo.Measurement(TagID, TimestampUTC DESC);
GO
