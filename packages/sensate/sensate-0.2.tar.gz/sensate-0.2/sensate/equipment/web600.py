__author__ = 'nthmost/connorh'

__doc__='''editing a copy of wsg30.py to accommodate the web600 in sensate'''

### SNMP helpers used by hub.py and sensor.py

# Magic SNMP number for Sensaphone WSG30, used in constructing Object IDs for sensor value lookups.
SENSAPHONE_OIDBASE = '.1.3.6.1.4.1.8338.1.1.4.1.1.1'

# MAC address: 1.3.6.1.4.1.8338.1.1.4.1.6.28.0

MAX_SENSORS_PER_HUB = 8     # Power and Battery are 1 and 2. 6 sensors remain.


SENSOR_DATA_MAP = { 'name': 15,
                    'units': 19,
                    'alarmlow': 12,
                    'alarmhigh': 14,
                    'measurement': 48,
                    'alarm_status': 91,         # STRING: "OK", "Low", "High", "Low Battery" or "Trouble"
                    'measurement_type': 92,     # STRING: 'Temp 2.8k C' or other type.
                    'lastalarm': 98,            # STRING: "3/3/2014 1:31:14am"
                  }


STATUS_OK = 'OK'
STATUS_TROUBLE = 'Trouble'
BATTERY_LOW = 'Low Battery'         # there is no Low Battery state. this is a satisfice move to make SensorHub code neater.
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
        return '%s.%i.%i' % (SENSAPHONE_OIDBASE, idx, SENSOR_DATA_MAP[datum])
    else:
        return '%s.%i' % (SENSAPHONE_OIDBASE, idx)

'''
enterprises.8338.1.1.4.1.6.1.0 = IpAddress: 172.20.1.66
enterprises.8338.1.1.4.1.6.11.0 = IpAddress: 172.25.4.1
enterprises.8338.1.1.4.1.6.12.0 = IpAddress: 172.25.4.50
enterprises.8338.1.1.4.1.6.13.0 = IpAddress: 255.255.255.0
enterprises.8338.1.1.4.1.6.14.0 = ""
enterprises.8338.1.1.4.1.6.15.0 = ""
enterprises.8338.1.1.4.1.6.16.0 = INTEGER: 1
enterprises.8338.1.1.4.1.6.17.0 = ""
enterprises.8338.1.1.4.1.6.18.0 = ""
enterprises.8338.1.1.4.1.6.19.0 = INTEGER: 2
enterprises.8338.1.1.4.1.6.20.0 = INTEGER: 2
enterprises.8338.1.1.4.1.6.22.0 = INTEGER: 25
enterprises.8338.1.1.4.1.6.23.0 = INTEGER: 80
enterprises.8338.1.1.4.1.6.24.0 = STRING: "public"
enterprises.8338.1.1.4.1.6.25.0 = ""
enterprises.8338.1.1.4.1.6.26.0 = ""
enterprises.8338.1.1.4.1.6.27.0 = STRING: "time.sensaphone.com"
enterprises.8338.1.1.4.1.6.28.0 = STRING: "00-07-F9-00-6D-B4"
enterprises.8338.1.1.4.1.6.33.0 = INTEGER: 1
enterprises.8338.1.1.4.1.7.2.0 = STRING: "Testy Temperature"
enterprises.8338.1.1.4.1.7.3.0 = ""
enterprises.8338.1.1.4.1.7.4.0 = ""
enterprises.8338.1.1.4.1.7.5.0 = INTEGER: 483284768
enterprises.8338.1.1.4.1.7.8.0 = STRING: "0"
enterprises.8338.1.1.4.1.7.12.0 = INTEGER: 60
enterprises.8338.1.1.4.1.7.13.0 = INTEGER: 2
enterprises.8338.1.1.4.1.7.14.0 = INTEGER: 1
enterprises.8338.1.1.4.1.7.15.0 = STRING: "1/14/2015 1:46:08pm"
enterprises.8338.1.1.4.1.7.17.0 = INTEGER: 1
enterprises.8338.1.1.4.1.7.18.0 = INTEGER: 1
enterprises.8338.1.1.4.1.7.19.0 = INTEGER: 502
enterprises.8338.1.1.4.1.7.28.0 = INTEGER: 0
enterprises.8338.1.1.4.1.7.29.0 = INTEGER: 0
enterprises.8338.1.1.4.1.7.30.0 = INTEGER: 480263391
enterprises.8338.1.1.4.1.7.31.0 = STRING: "v.1.5.9.H"
enterprises.8338.1.1.4.1.7.32.0 = INTEGER: 5756
enterprises.8338.1.1.4.1.7.33.0 = INTEGER: 0
enterprises.8338.1.1.4.1.7.34.0 = INTEGER: 0
enterprises.8338.1.1.4.1.7.35.0 = INTEGER: 0
enterprises.8338.1.1.4.1.7.36.0 = STRING: "Sensaphone"
enterprises.8338.1.1.4.1.7.37.0 = STRING: "Web600"
enterprises.8338.1.1.4.1.7.38.0 = INTEGER: 0
enterprises.8338.1.1.4.1.7.39.0 = INTEGER: 1
enterprises.8338.1.1.4.1.7.40.0 = STRING: "Sensaphone"
enterprises.8338.1.1.4.1.7.41.0 = STRING: "<i>Web600</i>"
enterprises.8338.1.1.4.1.7.43.0 = INTEGER: 1520762882
enterprises.8338.1.1.4.1.7.50.0 = INTEGER: 8
enterprises.8338.1.1.4.1.7.51.0 = INTEGER: 46
enterprises.8338.1.1.4.1.7.52.0 = INTEGER: 13
enterprises.8338.1.1.4.1.7.53.0 = INTEGER: 14
enterprises.8338.1.1.4.1.7.54.0 = INTEGER: 6
enterprises.8338.1.1.4.1.7.55.0 = INTEGER: 1
enterprises.8338.1.1.4.1.7.56.0 = INTEGER: 2015
enterprises.8338.1.1.4.1.9.1.0 = INTEGER: 0
enterprises.8338.1.1.4.1.9.2.0 = INTEGER: 536903680
enterprises.8338.1.1.4.1.9.3.0 = INTEGER: 0
enterprises.8338.1.1.4.1.9.4.0 = Hex-STRING: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 
00 00 00 00 00 00 00 00 00 00 
enterprises.8338.1.1.4.1.9.5.0 = INTEGER: 0
enterprises.8338.1.1.4.1.9.6.0 = INTEGER: 0
enterprises.8338.1.1.4.1.9.1.0 = INTEGER: 0
'''
