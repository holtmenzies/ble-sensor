import asyncio
import struct
from bleak import BleakClient, BleakScanner

import streamlit as st
from altair import Chart, Y, X

from movement import Movement
from reading import Reading

st.set_page_config(
    page_title="Sensor Acceleration",
    layout="wide"
)


# Name given to Arduino
DEVICE_NAME = "AccelerationMonitor"
# Accelerometer Sensor Data
DATA_CHAR = "00001143-0000-1000-8000-00805f9b34fb"
# Gyroscope Sensor Data
GYRO_CHAR = "00001142-0000-1000-8000-00805f9b34fb"
# Max / Min Value to use for display of acceleration data
ACCEL_MAX = 4
# Delay - time between printing sensor readings to the console
PRINT_DELAY = 0.5

mv = Movement()
re = Reading()
def data_note_handler(sender, data):
    """
    Takes data passed from the BLE connection as an array of bytes and converts 
    it to three floats for the x,y,z axes

    # Parameters
    - sender: UUID of sender of data
    - data: notification data to process
    """
    ax, ay, az, ar, gx, gy, gz, gr = struct.unpack('fffIfffI', data)
    re.listen(ax, ay, az, ar, gx, gy, gz)
    re.add_data(ax, ay, az, ar, gx, gy, gz)


async def run_ble_client(frame):
    """
    Establishes the BLE connection updates current sensor readings, and updates
    dashboard with most recent datazd
    
    # Parameters
    - frame: streamlit empty frame used to display sensor data
    """
    print("Scanning...")
    device = None
    # scan for devices
    devices = await BleakScanner.discover()

    for d in devices:
        if d.name == DEVICE_NAME:
            device = d
            break
    
    # device cannot be found
    if not device:
        print(f"Cannot find {DEVICE_NAME}")
        return
    
    print(f"Connecting to {DEVICE_NAME}")
    async with BleakClient(device) as client:
        try:
            print("reading notifications")
            await client.start_notify(
                DATA_CHAR,
                data_note_handler
            )

            print("Receiving Data (Press Ctrl-C to stop)")
            while True:
                di = re.get_data()
                if di: 
                    mv.set_current(di)
                    with frame.container(): # fill out streamlit container
                        st.markdown("# Incoming Sensor Data")
                        col = st.columns((3, 3), gap = 'medium')
                        with col[0]:
                            st.metric(
                                label = "Max Acceleration",
                                value = f"{round(mv.prev_max[-1], 2)} Gs",
                                delta = round(mv.prev_max[-1] - mv.prev_max[-2], 1)
                            )
                                            
                            chart = Chart(mv.current).mark_line().encode(
                                x = X("td", title = "Time (s)"),
                                y = Y("Total Acceleration", title = "Acceleration (Gs)").scale(domain = (-1, ACCEL_MAX))
                            )
                            st.altair_chart(chart, use_container_width=True)

                        with col[1]:
                            st.markdown("### Accelerometer and Gyroscope Data")
                            st.dataframe(mv.current)

                await asyncio.sleep(PRINT_DELAY)
        except asyncio.CancelledError:
            print("\nStopping Notifications...")
            await client.stop_notify(DATA_CHAR)
    
def main():
    frame = st.empty()

    try:
        asyncio.run(run_ble_client(frame))
    except KeyboardInterrupt:
        print("DONE!")


if __name__ == "__main__":
    main()