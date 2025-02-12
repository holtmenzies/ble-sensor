import time
from collections import deque
from numpy import sqrt

# Threshold for starting a new reading for max velocity (in Gs)
G_THRESHOLD = 1.2
# max time to wait to end a rep in nano seconds
MOVEMENT_DELAY = 1e9 
# Number of readings to save before a movement is detected
BUFFER_SIZE = 20

class Reading:
    def __init__(self):
        """
        Initialize a new set of readings. This represents on set of sensor
        readings from start to finish. Data is stored as a dictionary with a 
        key for each axis from each sensor and a key for timestamp
        """
        self.record = False # boolean should record incoming data
        self.last_movment = None # boolean movement detected
        self.update = False # boolean ok to return results or not
        self.buffer = dict(
            ax = deque(maxlen = BUFFER_SIZE),
            ay = deque(maxlen = BUFFER_SIZE),
            az = deque(maxlen = BUFFER_SIZE),
            gx = deque(maxlen = BUFFER_SIZE),
            gy = deque(maxlen = BUFFER_SIZE),
            gz = deque(maxlen = BUFFER_SIZE),
            tr = deque(maxlen = BUFFER_SIZE)
        )
        # will be turned into a dataframe for calculations
        self.readings = dict(
            ax = [],
            ay = [],
            az = [],
            gx = [],
            gy = [],
            gz = [],
            tr = []
        )

    def _add_to_buffer(self,  ax, ay, az, ar, gx, gy, gz):
        """
        Adds a new buffer reading from the sensor and time stamp.

        # Params
        - ax: x axis accelerometer reading
        - ay: y axis accelerometer reading
        - az: z axis accelerometer reading
        - ar: accelerometer timestamp
        - gx: x axis gyroscope reading
        - gy: y axis gyroscope reading
        - gz: z axis gyroscope reading
        - gr: gyroscope time stamp
        """        
        self.buffer["ax"].append(ax)
        self.buffer["ay"].append(ay)
        self.buffer["az"].append(az)
        self.buffer["gx"].append(gx)
        self.buffer["gy"].append(gy)
        self.buffer["gz"].append(gz)
        self.buffer["tr"].append(ar)
        

    def add_data(self, ax, ay, az, ar, gx, gy, gz):
        """
        Adds a new reading from the sensor and time stamp.

        # Params
        - ax: x axis accelerometer reading
        - ay: y axis accelerometer reading
        - az: z axis accelerometer reading
        - ar: accelerometer timestamp
        - gx: x axis gyroscope reading
        - gy: y axis gyroscope reading
        - gz: z axis gyroscope reading
        - gr: gyroscope time stamp
        """
        if self.record:
            self.readings["ax"].append(ax)
            self.readings["ay"].append(ay)
            self.readings["az"].append(az)
            self.readings["gx"].append(gx)
            self.readings["gy"].append(gy)
            self.readings["gz"].append(gz)
            self.readings["tr"].append(ar)

    def listen(self, ax, ay, az, ar, gx, gy, gz):
        """
        Monitor incoming sensor data, if a movement has been detected or if 
        the max delay has not been exceeded continue recording
        
        # Parameters
        - ax: x axis of accelerometer
        - ay: y axis of accelerometer
        - az: z axis of accelerometer
        """
        curr = time.time_ns()
        # check the total acceleration -- waiting for a sudden movement
        has_movment = sqrt(ax**2 + ay**2 + az**2) > G_THRESHOLD
        if has_movment:
            self.last_movment = curr
        # check that last_movment has been initialized
        if self.last_movment != None and curr - self.last_movment < MOVEMENT_DELAY:
            if len(self.buffer["ax"]) > 0: # empty the buffer before writing new sensor data
                for k in self.buffer.keys():
                    self.readings[k] = [x for x in self.buffer[k]]
                    self.buffer[k].clear()
            self.record = True
        else:
            if self.last_movment != None:
                # Set has been started and finished display results
                self.update = True
            self.record = False
            # Movement not detected, Update buffer
            self._add_to_buffer(ax, ay, az, ar, gx, gy, gz)


    def get_data(self):
        """
        Returns all of the readings from the last working set, then resets the 
        state for a new set, If the data is not ready yet None is returned
        
        # Returns
        - a dictionary containing new data or None if data is still being
        recorded or there are no readings
        """
        if self.update:
            last_set = self.readings
            self.reset_data()
            return last_set


    def reset_data(self):
        """
        Resets the contents of a working set after it has ended
        """
        self.readings = dict(
            ax = [],
            ay = [],
            az = [],
            gx = [],
            gy = [],
            gz = [],
            tr = []
        )
        self.buffer = dict(
            ax = deque(maxlen = BUFFER_SIZE),
            ay = deque(maxlen = BUFFER_SIZE),
            az = deque(maxlen = BUFFER_SIZE),
            gx = deque(maxlen = BUFFER_SIZE),
            gy = deque(maxlen = BUFFER_SIZE),
            gz = deque(maxlen = BUFFER_SIZE),
            tr = deque(maxlen = BUFFER_SIZE)
        )
        self.update = False
        self.last_movment = None
