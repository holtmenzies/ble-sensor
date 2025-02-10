#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>

// Device name
const char *nameOfPeripheral = "AccelerationMonitor";
const char *BLE_UUID_SERVICE = "00001101-0000-1000-8000-00805f9b34fb";
const char *BLE_UUID_DATA = "00001143-0000-1000-8000-00805f9b34fb";

typedef struct {
    float x;
    float y;
    float z;
    unsigned long time;
} Reading;

// Size of packet from IMU in Bytes 4 floats + 1 unsigned long (for time)
// Arduino treats unsigned long as a 4 byte integer
const int READING_SIZE = 2 * sizeof(Reading);

// BLE Service
BLEService IMUservice(BLE_UUID_SERVICE);

// Sends one instance of the Reading Struct
BLECharacteristic dataChar(BLE_UUID_DATA, BLERead | BLENotify | BLEBroadcast, READING_SIZE, true);

// Interval for each sensor
const unsigned long DATA_INTERVAL = 1; // 1ms
// Variables to hold previous read time
unsigned long dataPrev;
unsigned long gyroPrev;


/*
 *  MAIN
 */
void setup()
{

    // Start serial.
    Serial.begin(9600);

    // Ensure serial port is ready. -- Uncomment if using Serial Monitor in 
    // Arduino IDE
    // while (!Serial);

    // Start accelerometer
    startAccel();

    // Start BLE.
    startBLE();

    // Create BLE service and characteristics.
    BLE.setLocalName(nameOfPeripheral);
    BLE.setAdvertisedService(IMUservice);
    IMUservice.addCharacteristic(dataChar);
    BLE.addService(IMUservice);

    // Bluetooth LE connection handlers.
    BLE.setEventHandler(BLEConnected, onBLEConnected);
    BLE.setEventHandler(BLEDisconnected, onBLEDisconnected);

    // Advertise Service
    BLE.advertise();

    // Print out full UUID and MAC address.
    Serial.println("Peripheral advertising info: ");
    Serial.print("Name: ");
    Serial.println(nameOfPeripheral);
    Serial.print("MAC: ");
    Serial.println(BLE.address());
    Serial.print("Service UUID: ");
    Serial.println(IMUservice.uuid());
    Serial.print("txCharacteristics UUID: ");
    Serial.println(BLE_UUID_DATA);

    Serial.println("Bluetooth device active, waiting for connections...");
}

void loop()
{
    BLEDevice central = BLE.central();

    if (central)
    {
        dataPrev = millis();
        // Only send data if we are connected to a central device.
        while (central.connected())
        {
            connectedLight();

            if (IMU.accelerationAvailable())
            {
                onDataRead(&dataPrev);
            }
        }
    }
}

/*
 *  BLUETOOTH
 */
void startBLE()
{
    if (!BLE.begin())
    {
        Serial.println("starting BLE failed!");
        while (1)
            ;
    }
}

void onBLEConnected(BLEDevice central)
{
    Serial.print("Connected event, central: ");
    Serial.println(central.address());
}

void onBLEDisconnected(BLEDevice central)
{
    Serial.print("Disconnected event, central: ");
    Serial.println(central.address());
}


/**
 * Accelerometer startup
 */
void startAccel()
{
    if (!IMU.begin())
    {
        Serial.println("Faild to Start Accelerometer");
        while (1)
            ;
    }
}

/**
 * Send reading from accelerometer
 * 
 * @param prevTime previous time of accelerometer reading
 */
void onDataRead(unsigned long *prevTime)
{   
    Reading accel;
    Reading gyro;

    unsigned long current = millis();
    if (current - *prevTime >=  DATA_INTERVAL) {

        IMU.readAcceleration(accel.x, accel.y, accel.z);
        accel.time = current;
        IMU.readGyroscope(gyro.x, gyro.y, gyro.z);
        gyro.time = current;
        // Only update if new reading
        *prevTime = current;

        Reading data[2 * READING_SIZE];
        memcpy(&data[0], &accel, READING_SIZE);
        memcpy(&data[READING_SIZE], &gyro, READING_SIZE);
        dataChar.writeValue(data, sizeof(data));
    }
    
}
