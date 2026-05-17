import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# ============================================================
# SQL Server connection
# ============================================================
CONN_STR = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=ZEM-RAHAF\\SQLEXPRESS;"
    "Database=SCADA_AirHeater;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

# If your PC uses ODBC Driver 18 instead, replace the first line with:
# "Driver={ODBC Driver 18 for SQL Server};"


# ============================================================
# Plot configuration
# ============================================================
TIME_WINDOW_MINUTES = 20

OUTPUT_FILE = "Figure_Control_Response_OPCUA.png"

TAGS = [
    "AirHeater.Temperature",
    "AirHeater.FilteredTemperature",
    "AirHeater.Setpoint",
    "AirHeater.ControlSignal"
]


def load_data():
    """
    Load latest OPC UA logged SCADA data from SQL Server.
    The data source is the Measurement table, where the OPC UA
    datalogger stores timestamped process values.
    """

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
          AND m.TimestampUTC >= DATEADD(MINUTE, -?, SYSUTCDATETIME())
        ORDER BY m.TimestampUTC ASC;
    """

    with pyodbc.connect(CONN_STR) as conn:
        df = pd.read_sql(
            query,
            conn,
            params=TAGS + [TIME_WINDOW_MINUTES]
        )

    return df


def create_plot(df):
    """
    Create a control-response plot showing temperature, filtered
    temperature, setpoint and control signal.
    """

    df["TimestampUTC"] = pd.to_datetime(df["TimestampUTC"])

    pivot = df.pivot_table(
        index="TimestampUTC",
        columns="TagName",
        values="Value",
        aggfunc="mean"
    )

    fig, ax1 = plt.subplots(figsize=(11, 5.5))

    # ============================================================
    # Left axis: temperature values
    # ============================================================
    if "AirHeater.Temperature" in pivot.columns:
        ax1.plot(
            pivot.index,
            pivot["AirHeater.Temperature"],
            linewidth=1.6,
            label="Temperature [°C]"
        )

    if "AirHeater.FilteredTemperature" in pivot.columns:
        ax1.plot(
            pivot.index,
            pivot["AirHeater.FilteredTemperature"],
            linewidth=1.6,
            label="Filtered temperature [°C]"
        )

    if "AirHeater.Setpoint" in pivot.columns:
        ax1.plot(
            pivot.index,
            pivot["AirHeater.Setpoint"],
            linewidth=1.8,
            label="Setpoint [°C]"
        )

    ax1.set_xlabel("Time [UTC]")
    ax1.set_ylabel("Temperature [°C]")
    ax1.grid(True, alpha=0.4)

    # Format x-axis time labels
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax1.xaxis.set_major_locator(mdates.AutoDateLocator())

    # ============================================================
    # Right axis: control signal
    # ============================================================
    ax2 = ax1.twinx()

    if "AirHeater.ControlSignal" in pivot.columns:
        ax2.plot(
            pivot.index,
            pivot["AirHeater.ControlSignal"],
            linestyle="--",
            linewidth=1.6,
            label="Control signal [%]"
        )

    ax2.set_ylabel("Control signal [%]")

    # ============================================================
    # Combined legend
    # ============================================================
    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()

    ax1.legend(
        lines_1 + lines_2,
        labels_1 + labels_2,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.16),
        ncol=2,
        frameon=True
    )

    plt.title("Simulated Air-Heater Control Response Based on OPC UA Logged Data")

    fig.autofmt_xdate()
    plt.tight_layout(rect=[0, 0.08, 1, 1])

    plt.savefig(OUTPUT_FILE, dpi=300, bbox_inches="tight")
    plt.show()

    print(f"Plot saved as {OUTPUT_FILE}")


def main():
    df = load_data()

    if df.empty:
        print("No data found.")
        print("Run the OPC UA server and OPC UA SQL datalogger first.")
        return

    print("Loaded data from SQL Server:")
    print(df["TagName"].value_counts())

    create_plot(df)


if __name__ == "__main__":
    main()