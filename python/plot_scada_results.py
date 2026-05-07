import pyodbc
import pandas as pd
import matplotlib.pyplot as plt

CONN_STR = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=ZEM-RAHAF\\SQLEXPRESS;"
    "Database=SCADA_AirHeater;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

TAGS = [
    "AirHeater.Temperature",
    "AirHeater.FilteredTemperature",
    "AirHeater.Setpoint",
    "AirHeater.ControlSignal"
]


def main():
    conn = pyodbc.connect(CONN_STR)

    placeholders = ",".join(["?"] * len(TAGS))

    query = f"""
        SELECT
            t.TagName,
            m.TimestampUTC,
            CAST(m.Value AS FLOAT) AS Value,
            t.Unit
        FROM dbo.Measurement m
        JOIN dbo.Tag t ON t.TagID = m.TagID
        WHERE t.TagName IN ({placeholders})
          AND m.TimestampUTC >= DATEADD(MINUTE, -20, SYSUTCDATETIME())
        ORDER BY m.TimestampUTC ASC;
    """

    df = pd.read_sql(query, conn, params=TAGS)
    conn.close()

    if df.empty:
        print("No data found. Run the OPC UA server and datalogger first.")
        return

    df["TimestampUTC"] = pd.to_datetime(df["TimestampUTC"])

    pivot = df.pivot_table(
        index="TimestampUTC",
        columns="TagName",
        values="Value",
        aggfunc="mean"
    )

    fig, ax1 = plt.subplots(figsize=(10, 5))

    if "AirHeater.Temperature" in pivot:
        ax1.plot(
            pivot.index,
            pivot["AirHeater.Temperature"],
            label="Temperature [C]"
        )

    if "AirHeater.FilteredTemperature" in pivot:
        ax1.plot(
            pivot.index,
            pivot["AirHeater.FilteredTemperature"],
            label="Filtered temperature [C]"
        )

    if "AirHeater.Setpoint" in pivot:
        ax1.plot(
            pivot.index,
            pivot["AirHeater.Setpoint"],
            label="Setpoint [C]"
        )

    ax1.set_xlabel("Time [UTC]")
    ax1.set_ylabel("Temperature [C]")
    ax1.grid(True)

    ax2 = ax1.twinx()

    if "AirHeater.ControlSignal" in pivot:
        ax2.plot(
            pivot.index,
            pivot["AirHeater.ControlSignal"],
            linestyle="--",
            label="Control signal [%]"
        )

    ax2.set_ylabel("Control Signal [%]")

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="best")

    plt.title("Simulated Air Heater Control Response")
    plt.tight_layout()

    output_file = "figures/final_opcua_control_response_plot.png"
    plt.savefig(output_file, dpi=300)
    plt.show()

    print(f"Plot saved as {output_file}")


if __name__ == "__main__":
    main()
