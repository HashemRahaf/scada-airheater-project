USE SCADA_AirHeater;
GO

CREATE OR ALTER PROCEDURE dbo.InsertMeasurement
    @TagName NVARCHAR(100),
    @Value FLOAT,
    @QualityFlag NVARCHAR(20) = 'Good'
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @TagID INT;
    SELECT @TagID = TagID FROM dbo.Tag WHERE TagName = @TagName;

    IF @TagID IS NULL
    BEGIN
        THROW 50001, 'Tag not found in dbo.Tag.', 1;
    END

    INSERT INTO dbo.Measurement (TagID, TimestampUTC, Value, QualityFlag)
    VALUES (@TagID, SYSUTCDATETIME(), @Value, @QualityFlag);
END;
GO

CREATE OR ALTER PROCEDURE dbo.GetLatestValues
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        t.TagName,
        t.Description,
        t.Unit,
        m.TimestampUTC,
        m.Value,
        m.QualityFlag
    FROM dbo.Tag t
    OUTER APPLY (
        SELECT TOP (1)
            mm.TimestampUTC,
            mm.Value,
            mm.QualityFlag
        FROM dbo.Measurement mm
        WHERE mm.TagID = t.TagID
        ORDER BY mm.TimestampUTC DESC
    ) m
    WHERE t.IsActive = 1
    ORDER BY t.TagName;
END;
GO

CREATE OR ALTER PROCEDURE dbo.AcknowledgeAlarm
    @AlarmEventID BIGINT,
    @AcknowledgedBy NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;

    UPDATE dbo.AlarmEvent
    SET
        Acknowledged = 1,
        AcknowledgedBy = @AcknowledgedBy,
        AcknowledgedTimeUTC = SYSUTCDATETIME()
    WHERE AlarmEventID = @AlarmEventID
      AND Status = 'Active';
END;
GO
