USE SCADA_AirHeater;
GO

INSERT INTO dbo.Tag (TagName, Description, Unit, DataType, IsActive)
VALUES
('AirHeater.Temperature', 'Measured process temperature', 'C', 'FLOAT', 1),
('AirHeater.FilteredTemperature', 'Low-pass filtered temperature', 'C', 'FLOAT', 1),
('AirHeater.Setpoint', 'Temperature setpoint', 'C', 'FLOAT', 1),
('AirHeater.ControlSignal', 'PI controller output', '%', 'FLOAT', 1),
('AirHeater.Error', 'Setpoint minus filtered temperature', 'C', 'FLOAT', 1);
GO

INSERT INTO dbo.OPCUATagMap (TagID, NamespaceURI, NodeId, BrowsePath)
SELECT TagID, 'http://rahaf-scada-airheater',
       CASE TagName
           WHEN 'AirHeater.Temperature' THEN 'ns=2;s=AirHeater.Temperature'
           WHEN 'AirHeater.FilteredTemperature' THEN 'ns=2;s=AirHeater.FilteredTemperature'
           WHEN 'AirHeater.Setpoint' THEN 'ns=2;s=AirHeater.Setpoint'
           WHEN 'AirHeater.ControlSignal' THEN 'ns=2;s=AirHeater.ControlSignal'
           WHEN 'AirHeater.Error' THEN 'ns=2;s=AirHeater.Error'
       END,
       CASE TagName
           WHEN 'AirHeater.Temperature' THEN '/Objects/AirHeater/Temperature'
           WHEN 'AirHeater.FilteredTemperature' THEN '/Objects/AirHeater/FilteredTemperature'
           WHEN 'AirHeater.Setpoint' THEN '/Objects/AirHeater/Setpoint'
           WHEN 'AirHeater.ControlSignal' THEN '/Objects/AirHeater/ControlSignal'
           WHEN 'AirHeater.Error' THEN '/Objects/AirHeater/Error'
       END
FROM dbo.Tag;
GO

INSERT INTO dbo.AlarmDefinition (AlarmName, TagID, Priority, ConditionText, LimitValue, IsEnabled)
SELECT 'High Temperature', TagID, 'High', 'Temperature > 40 C', 40.0, 1
FROM dbo.Tag WHERE TagName = 'AirHeater.Temperature';

INSERT INTO dbo.AlarmDefinition (AlarmName, TagID, Priority, ConditionText, LimitValue, IsEnabled)
SELECT 'Low Temperature', TagID, 'Medium', 'Temperature < 10 C', 10.0, 1
FROM dbo.Tag WHERE TagName = 'AirHeater.Temperature';

INSERT INTO dbo.AlarmDefinition (AlarmName, TagID, Priority, ConditionText, LimitValue, IsEnabled)
SELECT 'Controller Saturation', TagID, 'Medium', 'ControlSignal > 95 %', 95.0, 1
FROM dbo.Tag WHERE TagName = 'AirHeater.ControlSignal';
GO
