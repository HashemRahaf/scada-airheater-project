import asyncio
from datetime import datetime, timezone

import pyodbc
from asyncua import Client

# =========================
# SQL Server connection
# =========================
CONN_STR = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=ZEM-RAHAF\\SQLEXPRESS;"
    "Database=SCADA_AirHeater;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

# =========================
# OPC UA settings
# =========================
OPC_ENDPOINT = "opc.tcp://localhost:4840/scada/airheater/"
NAMESPACE_URI = "http://rahaf-scada-airheater"

LOG_INTERVAL = 1.0

TAGS = {
    "AirHeater.Temperature": "Temperature",
    "AirHeater.FilteredTemperature": "FilteredTemperature",
    "AirHeater.Setpoint": "Setpoint",
    "AirHeater.ControlSignal": "ControlSignal",
    "AirHeater.Error": "Error"
}


def insert_measurement(cursor, tag_name, value, quality="Good"):
    cursor.execute(
        "EXEC dbo.InsertMeasurement ?, ?, ?",
        tag_name,
        round(float(value), 4),
        quality
    )


def create_alarm_if_needed(cursor, alarm_definition_id, value):
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM dbo.AlarmEvent
        WHERE AlarmDefinitionID = ?
          AND Status = 'Active'
        """,
        alarm_definition_id
    )

    active_count = cursor.fetchone()[0]

    if active_count == 0:
        cursor.execute(
            """
            INSERT INTO dbo.AlarmEvent
            (AlarmDefinitionID, AlarmValue, Status)
            VALUES (?, ?, 'Active')
            """,
            alarm_definition_id,
            round(float(value), 4)
        )


def clear_alarm_if_active(cursor, alarm_definition_id):
    cursor.execute(
        """
        UPDATE dbo.AlarmEvent
        SET Status = 'Inactive',
            EndTimeUTC = SYSUTCDATETIME()
        WHERE AlarmDefinitionID = ?
          AND Status = 'Active'
        """,
        alarm_definition_id
    )


def check_alarms(cursor, temperature, control_signal):
    if temperature > 40.0:
        create_alarm_if_needed(cursor, 1, temperature)
    else:
        clear_alarm_if_active(cursor, 1)

    if temperature < 10.0:
        create_alarm_if_needed(cursor, 2, temperature)
    else:
        clear_alarm_if_active(cursor, 2)

    if control_signal > 95.0:
        create_alarm_if_needed(cursor, 3, control_signal)
    else:
        clear_alarm_if_active(cursor, 3)


async def main():
    print("Starting OPC UA to SQL Server datalogger")
    print(f"OPC UA endpoint: {OPC_ENDPOINT}")
    print("------------------------------------------------------------")

    conn = pyodbc.connect(CONN_STR, autocommit=True)
    cursor = conn.cursor()

    try:
        async with Client(url=OPC_ENDPOINT) as client:
            namespace_index = await client.get_namespace_index(NAMESPACE_URI)

            airheater = await client.nodes.objects.get_child(
                [f"{namespace_index}:AirHeater"]
            )

            nodes = {}

            for tag_name, opc_name in TAGS.items():
                nodes[tag_name] = await airheater.get_child(
                    [f"{namespace_index}:{opc_name}"]
                )

            print("Connected to OPC UA server")
            print("Reading OPC UA tags and logging to SQL Server")
            print("------------------------------------------------------------")

            while True:
                values = {}

                for tag_name, node in nodes.items():
                    value = await node.read_value()
                    values[tag_name] = value
                    insert_measurement(cursor, tag_name, value)

                temperature = values["AirHeater.Temperature"]
                control_signal = values["AirHeater.ControlSignal"]

                check_alarms(cursor, temperature, control_signal)

                now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

                print(
                    f"{now} | "
                    f"Logged from OPC UA: "
                    f"PV={values['AirHeater.Temperature']:.2f} C | "
                    f"Filtered={values['AirHeater.FilteredTemperature']:.2f} C | "
                    f"SP={values['AirHeater.Setpoint']:.2f} C | "
                    f"MV={values['AirHeater.ControlSignal']:.2f} % | "
                    f"Error={values['AirHeater.Error']:.2f} C"
                )

                await asyncio.sleep(LOG_INTERVAL)

    except KeyboardInterrupt:
        print("Stopping OPC UA datalogger")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    asyncio.run(main())
