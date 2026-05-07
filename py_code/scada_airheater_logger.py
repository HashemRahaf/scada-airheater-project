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

SAMPLE_TIME = 1.0  # seconds

# Air heater model parameters
ambient_temp = 22.0       # °C
temperature = 22.0        # °C
filtered_temperature = 22.0

process_gain = 0.45
time_constant = 35.0

# Controller parameters
setpoint = 50.0           # °C
kp = 3.0
ki = 0.08
integral = 0.0

# Low-pass filter
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

def create_alarm_if_needed(cursor, alarm_definition_id, value):
    # Avoid creating duplicate active alarms
    cursor.execute("""
        SELECT COUNT(*) 
        FROM dbo.AlarmEvent
        WHERE AlarmDefinitionID = ?
          AND Status = 'Active'
    """, alarm_definition_id)

    active_count = cursor.fetchone()[0]

    if active_count == 0:
        cursor.execute("""
            INSERT INTO dbo.AlarmEvent 
            (AlarmDefinitionID, AlarmValue, Status)
            VALUES (?, ?, 'Active')
        """, alarm_definition_id, round(value, 4))

def clear_alarm_if_active(cursor, alarm_definition_id):
    cursor.execute("""
        UPDATE dbo.AlarmEvent
        SET Status = 'Inactive',
            EndTimeUTC = SYSUTCDATETIME()
        WHERE AlarmDefinitionID = ?
          AND Status = 'Active'
    """, alarm_definition_id)

def check_alarms(cursor, temp, control_signal):
    # AlarmDefinitionID values depend on insert order:
    # 1 = High Temperature, 2 = Low Temperature, 3 = Controller Saturation

    if temp > 80.0:
        create_alarm_if_needed(cursor, 1, temp)
    else:
        clear_alarm_if_active(cursor, 1)

    if temp < 10.0:
        create_alarm_if_needed(cursor, 2, temp)
    else:
        clear_alarm_if_active(cursor, 2)

    if control_signal > 95.0:
        create_alarm_if_needed(cursor, 3, control_signal)
    else:
        clear_alarm_if_active(cursor, 3)

def main():
    global temperature, filtered_temperature, integral

    print("Starting simulated SCADA air-heater logger...")
    print("Press CTRL+C to stop.")
    print("------------------------------------------------------------")

    conn = pyodbc.connect(CONN_STR, autocommit=True)
    cursor = conn.cursor()

    try:
        while True:
            # Sensor noise
            noise = random.uniform(-0.25, 0.25)
            measured_temperature = temperature + noise

            # Low-pass filter
            filtered_temperature = (
                alpha * measured_temperature 
                + (1 - alpha) * filtered_temperature
            )

            # PI controller
            error = setpoint - filtered_temperature
            integral += error * SAMPLE_TIME

            control_signal = kp * error + ki * integral
            control_signal = clamp(control_signal, 0.0, 100.0)

            # Simple air heater process model
            heating_effect = process_gain * control_signal
            cooling_effect = temperature - ambient_temp

            dTdt = (heating_effect - cooling_effect) / time_constant
            temperature += dTdt * SAMPLE_TIME

            # Log values
            insert_measurement(cursor, "AirHeater.Temperature", measured_temperature)
            insert_measurement(cursor, "AirHeater.FilteredTemperature", filtered_temperature)
            insert_measurement(cursor, "AirHeater.Setpoint", setpoint)
            insert_measurement(cursor, "AirHeater.ControlSignal", control_signal)
            insert_measurement(cursor, "AirHeater.Error", error)

            # Alarm check
            check_alarms(cursor, measured_temperature, control_signal)

            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

            print(
                f"{now} | "
                f"PV={measured_temperature:.2f} °C | "
                f"Filtered={filtered_temperature:.2f} °C | "
                f"SP={setpoint:.2f} °C | "
                f"MV={control_signal:.2f} % | "
                f"Error={error:.2f} °C"
            )

            time.sleep(SAMPLE_TIME)

    except KeyboardInterrupt:
        print("Stopping logger...")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()