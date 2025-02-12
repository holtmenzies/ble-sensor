# ble-sensor
A straightforward interface to read sensor data from a bluetooth LE enabled device and display the results in a dashboard. This serves as an easy template for anyone who wants a near real-time dashboard for incoming sensor data over bluetooth. Incoming data is simply an array of bytes so changing this to read from another bluetooth enabled device should not prove difficult.

## imu_sensor.ino

This implements the ble service for an Arduino Nano 33 BLE Sense. Currently only the accelerometer and gyroscope are read from and transmitted. This can easily be updated to include other sensor data as well by updating the onDataRead() function. If more data needs to be included either another characteristic (similar to dataChar) needs to be defined and added to the ble service or the size of dataChar needs to be increased.

## reading.py

This handles listening for movement from the remote sensor. Currently this means any detection of total acceleration greater than 1.2 G's. This parameter can be tuned by adjusting G_THRESHOLD constant.

Data will continue to be recorded until no motion has been detected for an amount of time greater than MOVEMENT_DELAY has passed. This amount of time is denoted in nanoseconds.

While data is not being recorded a buffer is filled with a number of readings set by the BUFFER_SIZE constant.

## movement.py

This file stores the most recent set of sensor readings. It also maintains an array of all previous maximum acceleration readings.

The dict passed to set_current() is turned into a pandas dataframe.

## ble_client.py

This is the entry point for the program. run_ble_client() handles establishing the bluetooth connection, reading notifications from the peripheral device, and displaying those results in a dashboard.

The BleakClient calls data_note_handler() which uses a Reading instance to listen for movement and record sensor data when appropriate.