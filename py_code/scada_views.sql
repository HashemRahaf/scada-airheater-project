CREATE VIEW vw_LatestValues AS
SELECT
    t.TagName,
    t.Unit,
    m.TimestampUTC,
    m.Value,
    m.QualityFlag
FROM Measurement m
JOIN Tag t ON t.TagID = m.TagID
WHERE m.TimestampUTC = (
    SELECT MAX(TimestampUTC)
    FROM Measurement m2
    WHERE m2.TagID = m.TagID
);