CREATE PROCEDURE InsertMeasurement
    @TagName NVARCHAR(100),
    @Value FLOAT,
    @QualityFlag NVARCHAR(20)
AS
BEGIN
    DECLARE @TagID INT;
    SELECT @TagID = TagID FROM Tag WHERE TagName = @TagName;

    INSERT INTO Measurement (TagID, TimestampUTC, Value, QualityFlag)
    VALUES (@TagID, SYSUTCDATETIME(), @Value, @QualityFlag);
END;
