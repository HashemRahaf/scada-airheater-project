"""
Legacy module: direct SQL logger from the control simulation.

This script was used during early validation only.
It is not part of the final runtime architecture.

Final runtime path:
OPC UA server -> OPC UA SQL datalogger -> SQL Server -> C# HMI
"""

import time
import random
import pyodbc
from datetime import datetime, timezone

CONN_STR = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=ZEM-RAHAF\\SQLEXPRESS;"
    "Database=SCADA_AirHeater;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

SAMPLE_TIME = 1.0
ambient_temp = 22.0
temperature = 22.0
filtered_temperature = 22.0
process_gain = 0.45
time_constant = 35.0
setpoint = 50.0
kp = 3.0
ki = 0.08
integral = 0.0
alpha = 0.25


def clamp(value, low, high):
    return max(low, min(high, value))


def insert_measurement(cursor, tag_name, value, quality="Good"):
    cursor.execute(
        "EXEC dbo.InsertMeasurement ?, ?, ?",
        tag_name,
        round(value, 4),
        quality
    )


def main():
    global temperature, filtered_temperature, integral

    conn = pyodbc.connect(CONN_STR, autocommit=True)
    cursor = conn.cursor()
    try:
        while True:
            noise = random.uniform(-0.25, 0.25)
            measured_temperature = temperature + noise
            filtered_temperature = alpha * measured_temperature + (1 - alpha) * filtered_temperature
            error = setpoint - filtered_temperature
            integral += error * SAMPLE_TIME
            control_signal = clamp(kp * error + ki * integral, 0.0, 100.0)
            dTdt = (process_gain * control_signal - (temperature - ambient_temp)) / time_constant
            temperature += dTdt * SAMPLE_TIME

            insert_measurement(cursor, "AirHeater.Temperature", measured_temperature)
            insert_measurement(cursor, "AirHeater.FilteredTemperature", filtered_temperature)
            insert_measurement(cursor, "AirHeater.Setpoint", setpoint)
            insert_measurement(cursor, "AirHeater.ControlSignal", control_signal)
            insert_measurement(cursor, "AirHeater.Error", error)

            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            print(f"{now} | Legacy direct SQL logger running")
            time.sleep(SAMPLE_TIME)
    except KeyboardInterrupt:
        pass
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
