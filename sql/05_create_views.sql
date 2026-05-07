USE SCADA_AirHeater;
GO

CREATE OR ALTER VIEW dbo.vw_LatestValues
AS
SELECT
    t.TagName,
    t.Unit,
    m.TimestampUTC,
    m.Value,
    m.QualityFlag
FROM dbo.Measurement m
JOIN dbo.Tag t ON t.TagID = m.TagID
WHERE m.TimestampUTC = (
    SELECT MAX(m2.TimestampUTC)
    FROM dbo.Measurement m2
    WHERE m2.TagID = m.TagID
);
GO

CREATE OR ALTER VIEW dbo.vw_ActiveAlarms
AS
SELECT
    ae.AlarmEventID,
    ad.AlarmName,
    ad.Priority,
    ae.StartTimeUTC,
    ae.AlarmValue,
    t.Unit,
    ae.Status,
    ae.Acknowledged,
    ae.AcknowledgedBy,
    ae.AcknowledgedTimeUTC
FROM dbo.AlarmEvent ae
JOIN dbo.AlarmDefinition ad ON ad.AlarmDefinitionID = ae.AlarmDefinitionID
JOIN dbo.Tag t ON t.TagID = ad.TagID
WHERE ae.Status = 'Active'
ORDER BY ae.StartTimeUTC DESC;
GO
