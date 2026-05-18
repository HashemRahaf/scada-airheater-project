SELECT
    TagName,
    Description,
    Unit,
    OPCNodeName,
    OPCNamespace,
    OPCServerEndpoint
FROM dbo.Tag
WHERE TagName LIKE 'AirHeater.%'
ORDER BY TagName;