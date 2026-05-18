SELECT TOP 50
    t.TagName,
    m.TimestampUTC,
    CAST(m.Value AS DECIMAL(18,2)) AS Value,
    t.Unit,
    m.QualityFlag
FROM dbo.Measurement m
JOIN dbo.Tag t ON t.TagID = m.TagID
ORDER BY m.TimestampUTC DESC;