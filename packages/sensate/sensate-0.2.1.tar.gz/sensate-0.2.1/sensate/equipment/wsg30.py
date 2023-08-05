__doc__='''The SensaphoneRecord object encapsulates the historical records 
currently stored on the Sensaphone device.

This object assists in populating historical records of sensor values.

The input data structure is a comma-separated CSV containing records for either a single 
selected sensor or for all sensors.  (see below copied from the Sensaphone WSG30 manual)

From there, we construct SensorCheck objects which can be converted to 

    # dict of SensorCheck objects (similar to SensorHub.sensor_check attribute)

The challenge here is that the sensaphone stores data based on the POSITION ("idx")
of the sensors on the device in its internal reckoning. Therefore the records don't 
provide a contiguous record of monitoring in real-world terms -- we have to piece
that back together ourselves.
'''

### SNMP helpers used by hub.py and sensor.py

# Magic SNMP number for Sensaphone WSG30, used in constructing Object IDs for sensor value lookups.
SENSAPHONE_OIDBASE = '.1.3.6.1.4.1.8338.1.1.4.1.1'

# MAX_SENSORS_PER_HUB restricts SNMP guesswork to a reasonable level.
# (theoretical max # of sensors per WSG30 hub = 30 wireless + 1 Power + 1 Battery.)
MAX_SENSORS_PER_HUB = 32

SENSOR_DATA_MAP = { 'name': 15, 
                    'units': 19,
                    'alarmlow': 11,
                    'alarmhigh': 12,
                    'measurement': 48,
                    'warnlow': 74,              # STRING: "3.7C"   ?? warn at low value ?? 
                    'warnhigh': 75,             # STRING: "7.6C"   ?? warn at high value ?? 
                    'alarm_status': 91,         # STRING: "OK", "Low", "High", "Low Battery" or "Trouble"
                    'measurement_type': 92,     # STRING: 'Temp 2.8k C' or other type.  
                    'battery_level': 93,        # STRING: "4.5"     ?? battery level ??
                    'lastalarm': 98,            # STRING: "3/3/2014 1:31:14am"
                    'serial': 35,               # STRING: "13500" 
                  }

STATUS_OK = 'OK'
STATUS_TROUBLE = 'Trouble'
BATTERY_LOW = 'Low Battery'
ALARM_HIGH = 'High'
ALARM_LOW = 'Low'

def get_sensor_oid(idx, datum=''):
    '''Returns OID for individual sensor (or, if `datum` supplied, the named data point for 
    sensor) at index `idx`.  Uses global SENSAPHONE_OIDBASE to construct and return full OID.
    
    Named data points:
    
    %r

    :param idx: (required) the "index" (1-32) of the sensor on the hub.
    :param datum: (optional) 
    :return oid (string) allowing retrieval of named data point.
    ''' % SENSOR_DATA_MAP

    if datum:
        return '%s.1.%i.%i' % (SENSAPHONE_OIDBASE, idx, SENSOR_DATA_MAP[datum])
    else:
        return '%s.1.%i' % (SENSAPHONE_OIDBASE, idx)



"""
iso.3.6.1.4.1.8338.1.1.4.1.6.1.0 = IpAddress: 172.20.1.66
iso.3.6.1.4.1.8338.1.1.4.1.6.11.0 = IpAddress: 172.25.2.1
iso.3.6.1.4.1.8338.1.1.4.1.6.12.0 = IpAddress: 172.25.2.254
iso.3.6.1.4.1.8338.1.1.4.1.6.13.0 = IpAddress: 255.255.255.0
iso.3.6.1.4.1.8338.1.1.4.1.6.14.0 = ""
iso.3.6.1.4.1.8338.1.1.4.1.6.15.0 = ""
iso.3.6.1.4.1.8338.1.1.4.1.6.16.0 = INTEGER: 1
iso.3.6.1.4.1.8338.1.1.4.1.6.17.0 = ""
iso.3.6.1.4.1.8338.1.1.4.1.6.18.0 = ""
iso.3.6.1.4.1.8338.1.1.4.1.6.19.0 = INTEGER: 2
iso.3.6.1.4.1.8338.1.1.4.1.6.20.0 = INTEGER: 2
iso.3.6.1.4.1.8338.1.1.4.1.6.22.0 = INTEGER: 25
iso.3.6.1.4.1.8338.1.1.4.1.6.23.0 = INTEGER: 80
iso.3.6.1.4.1.8338.1.1.4.1.6.24.0 = STRING: "public"
iso.3.6.1.4.1.8338.1.1.4.1.6.25.0 = ""
iso.3.6.1.4.1.8338.1.1.4.1.6.26.0 = ""
iso.3.6.1.4.1.8338.1.1.4.1.6.27.0 = STRING: "time.sensaphone.com"
iso.3.6.1.4.1.8338.1.1.4.1.6.28.0 = STRING: "00-07-F9-00-5E-1E"
iso.3.6.1.4.1.8338.1.1.4.1.6.29.0 = INTEGER: 0
iso.3.6.1.4.1.8338.1.1.4.1.6.33.0 = INTEGER: 1
iso.3.6.1.4.1.8338.1.1.4.1.7.2.0 = STRING: "475 Suite 230 WSG"
iso.3.6.1.4.1.8338.1.1.4.1.7.3.0 = STRING: "Wireless Sensor Gateway"
iso.3.6.1.4.1.8338.1.1.4.1.7.4.0 = STRING: "475 Brannan Suite 230"
iso.3.6.1.4.1.8338.1.1.4.1.7.5.0 = INTEGER: 483281323
iso.3.6.1.4.1.8338.1.1.4.1.7.8.0 = STRING: "0"
iso.3.6.1.4.1.8338.1.1.4.1.7.12.0 = INTEGER: 60
iso.3.6.1.4.1.8338.1.1.4.1.7.13.0 = INTEGER: 2
iso.3.6.1.4.1.8338.1.1.4.1.7.14.0 = INTEGER: 0
iso.3.6.1.4.1.8338.1.1.4.1.7.15.0 = STRING: "1/14/2015 12:48:43pm"
iso.3.6.1.4.1.8338.1.1.4.1.7.17.0 = INTEGER: 1
iso.3.6.1.4.1.8338.1.1.4.1.7.18.0 = INTEGER: 1
iso.3.6.1.4.1.8338.1.1.4.1.7.19.0 = INTEGER: 502
iso.3.6.1.4.1.8338.1.1.4.1.7.28.0 = INTEGER: 0
iso.3.6.1.4.1.8338.1.1.4.1.7.29.0 = INTEGER: 0
iso.3.6.1.4.1.8338.1.1.4.1.7.30.0 = INTEGER: 483265053
iso.3.6.1.4.1.8338.1.1.4.1.7.31.0 = STRING: "v.1.5.6.C"
iso.3.6.1.4.1.8338.1.1.4.1.7.32.0 = INTEGER: 4680
iso.3.6.1.4.1.8338.1.1.4.1.7.33.0 = INTEGER: 0
iso.3.6.1.4.1.8338.1.1.4.1.7.34.0 = INTEGER: 0
iso.3.6.1.4.1.8338.1.1.4.1.7.35.0 = INTEGER: 0
iso.3.6.1.4.1.8338.1.1.4.1.7.36.0 = STRING: "Sensaphone WSG30"
iso.3.6.1.4.1.8338.1.1.4.1.7.37.0 = STRING: "Wireless Sensor Gateway"
iso.3.6.1.4.1.8338.1.1.4.1.7.38.0 = INTEGER: 0
iso.3.6.1.4.1.8338.1.1.4.1.7.39.0 = INTEGER: 1
iso.3.6.1.4.1.8338.1.1.4.1.7.40.0 = STRING: "Sensaphone WSG30"
iso.3.6.1.4.1.8338.1.1.4.1.7.41.0 = STRING: "<i>Wireless Sensor Gateway</i>"
iso.3.6.1.4.1.8338.1.1.4.1.7.43.0 = INTEGER: 1520762885
"""

