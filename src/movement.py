import pandas as pd
import time
from numpy import diff, sqrt
from collections import deque

class Movement:
    def __init__(self, time_units = 0.001):
        """
        Initialize a new collection of readings after the sensor has detected
        movement
        
        # Parameters
        - time_units: units measured by time stamp (tr) from bluetooth device
        defaults to microseconds (1/1000)
        """
        if time_units <= 0:
            raise ValueError("time_units must be a positive value")
        self.time_units = time_units
        self.prev_max = [0] # Set of previous max acceleration readings
        self.current = None # se readings of most recent set

    def set_current(self, readings):
        """
        Creates a dataframe for each set of sensor
        readings. This will then update the current field. 
        
        # Parameters
        - readings: dictionary with accelerometer data, gyroscope data, and 
        time stamps.
        """
        self.current = pd.DataFrame(data = readings)
        # subtract previous reading from next to get time delta
        self.current["td"] = diff(self.current.tr, prepend = self.current.tr[0])
        # convert millisecond readings to seconds for units in g's
        self.current["td"] = self.current.td * self.time_units
        # Total Acceleration
        self.current["Total Acceleration"] = self.current.apply(lambda x: 
            sqrt(x["ax"]**2 + x["ay"]**2 + x["az"]**2),
            axis = 1
            )
        # Remove gravity from the reading
        self.current["Total Acceleration"] = self.current["Total Acceleration"] - 1
        
        self.prev_max.append((self.current["Total Acceleration"].max()))