import asyncio
import random
from datetime import datetime, timezone
from asyncua import Server

# =========================
# Simulation settings
# =========================
SAMPLE_TIME = 1.0  # seconds

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


async def main():
    global temperature
    global filtered_temperature
    global integral

    server = Server()
    await server.init()

    server.set_endpoint("opc.tcp://0.0.0.0:4840/scada/airheater/")
    server.set_server_name("SCADA Air Heater OPC UA Server")

    namespace_uri = "http://rahaf-scada-airheater"
    idx = await server.register_namespace(namespace_uri)

    objects = server.nodes.objects
    airheater = await objects.add_object(idx, "AirHeater")

    node_temperature = await airheater.add_variable(idx, "Temperature", temperature)
    node_filtered = await airheater.add_variable(idx, "FilteredTemperature", filtered_temperature)
    node_setpoint = await airheater.add_variable(idx, "Setpoint", setpoint)
    node_control = await airheater.add_variable(idx, "ControlSignal", 0.0)
    node_error = await airheater.add_variable(idx, "Error", 0.0)
    node_status = await airheater.add_variable(idx, "Status", "Running")

    await node_setpoint.set_writable()

    print("OPC UA Server started")
    print("Endpoint: opc.tcp://localhost:4840/scada/airheater/")
    print("------------------------------------------------------------")

    async with server:
        while True:
            current_setpoint = await node_setpoint.read_value()

            noise = random.uniform(-0.25, 0.25)
            measured_temperature = temperature + noise

            filtered_temperature = (
                alpha * measured_temperature
                + (1.0 - alpha) * filtered_temperature
            )

            error = current_setpoint - filtered_temperature
            integral += error * SAMPLE_TIME

            control_signal = kp * error + ki * integral
            control_signal = clamp(control_signal, 0.0, 100.0)

            heating_effect = process_gain * control_signal
            cooling_effect = temperature - ambient_temp

            dTdt = (heating_effect - cooling_effect) / time_constant
            temperature += dTdt * SAMPLE_TIME

            await node_temperature.write_value(round(measured_temperature, 4))
            await node_filtered.write_value(round(filtered_temperature, 4))
            await node_setpoint.write_value(round(current_setpoint, 4))
            await node_control.write_value(round(control_signal, 4))
            await node_error.write_value(round(error, 4))
            await node_status.write_value("Running")

            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

            print(
                f"{now} | "
                f"PV={measured_temperature:.2f} °C | "
                f"Filtered={filtered_temperature:.2f} °C | "
                f"SP={current_setpoint:.2f} °C | "
                f"MV={control_signal:.2f} % | "
                f"Error={error:.2f} °C"
            )

            await asyncio.sleep(SAMPLE_TIME)


if __name__ == "__main__":
    asyncio.run(main())