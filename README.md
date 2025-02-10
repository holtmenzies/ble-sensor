# ble-sensor
A straightforward interface to read sensor data from a bluetooth LE enabled device and display the results in a dashboard.

## imu_sensor.ino

This implements the ble service for an Arduino Nano 33 BLE Sense. Currently only the accelerometer and gyroscope are read from and transmitted. This can easily be updated to include other sensor data as well by updating the `onDataRead()` function for example. If more data needs to be included either another characteristic (similar to `dataChar`) needs to be defined and added to the ble service or the size of `dataChar` needs to be increased.

