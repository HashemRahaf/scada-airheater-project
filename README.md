# SCADA Air-Heater Project

This repository contains a modular SCADA prototype for a simulated air-heater process.
The final architecture is OPC UA based:

`OPC UA server -> OPC UA SQL datalogger -> SQL Server -> C# WinForms HMI`

## Project overview

- Python OPC UA server simulates the process dynamics, PI control, and low-pass filtering.
- Python OPC UA SQL datalogger reads OPC UA tags and persists time-series data to SQL Server.
- SQL Server stores measurements, tag metadata, alarm definitions/events, and query objects.
- C# WinForms HMI reads SQL Server for live values and active alarms, and supports acknowledgement.
- Python plotting script generates the final control-response figure used in the report.

## Folder structure

- `sql/`: numbered SQL deployment scripts (database, schema, seed data, procedures, views).
- `python/`: final runtime Python modules.
- `csharp/`: C# WinForms project files.
- `figures/`: final report figures and screenshots only.
- `legacy/`: non-final validation code kept only for traceability.
- `report/`: formal report PDF and optional editable report sources.

## Prerequisites

- Python 3.10+ with packages from `python/requirements.txt`
- SQL Server (Express or full)
- ODBC Driver 17/18 for SQL Server
- .NET 8 SDK + Windows desktop runtime
- Visual Studio 2022 or compatible tooling for WinForms

## Setup instructions

1. Create and initialize the database by running scripts in `sql/` in order:
   - `01_create_database.sql`
   - `02_create_tables.sql`
   - `03_insert_initial_data.sql`
   - `04_create_procedures.sql`
   - `05_create_views.sql`
2. Install Python dependencies:
   - `pip install -r python/requirements.txt`
3. Update connection strings in Python and C# files if your SQL instance name differs.

## Runtime order (final workflow)

1. Start `python/opcua_airheater_server.py`
2. Start `python/opcua_sql_datalogger.py`
3. Run the WinForms HMI from `csharp/ScadaHMI/`
4. Generate the control-response figure with `python/plot_scada_results.py`

## Legacy note

`legacy/direct_sql_logger_early_validation.py` is preserved only as an early validation artifact.
It is **not** part of the final runtime workflow and should not be used in formal testing results.

## Report delivery

The formal delivery document is the PDF report in `report/`.
The report should emphasize architecture, design reasoning, verification, results, and cybersecurity.
Complete implementation code remains in this GitHub repository.
