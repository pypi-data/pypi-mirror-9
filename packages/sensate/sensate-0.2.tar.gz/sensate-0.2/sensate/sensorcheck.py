__doc__='''LabSensor class for abstracting access to lab sensor data via SNMP and nagios.'''
__author__='nthmost'

from datetime import datetime
import json

# TODO: make equipment swappable (when more equipment presents itself)
from equipment.wsg30 import get_sensor_oid
from transports.snmp import SNMPobject
from utils import CustomJsonEncoder, CustomJsonDecoder

class SensorCheck(object):
    '''Represents a single moment of "Sensor Check", sampling data via either SNMP or nagios.

	This class was designed to be used mostly through SensorHub.
	
	Required arguments:
	
	hostname		-- (string) fqdn or LAN-accessible hostname (no prefix like http://)
	idx				-- (int) index of sensor on hostname (0 to MAX_SENSORS_PER_HUB)
	
	Object attributes retrieved by SNMP:

    serial          -- (string) unique serial number of recognized sensor.
    name            -- (string) the human-created name written into the sensor hub.
    measurement     -- (float) current value measured by sensor (generally the most important datum).
    units           -- (string) units for measurement data, e.g. "C" or "F" for temperature.
    alarmhigh       -- (float) value set on sensor hub for high value at which to report alarm.
    alarmlow        -- (float) value set on sensor hub for low value at which to report alarm.
    lastalarm	    -- (datetime) date+time at which sensor last had an alarm condition.
    measurement_type-- (string) Sensaphone set string describing type of measurement (e.g. 'Temp 2.8k C')
    alarm_status    -- (string) Reports as 'OK', 'High', 'Low', 'Low Battery' or 'Trouble' (no response)
    
	Available keyword arguments in addition to all of the above:

    timeout         -- (int or float) time in seconds to wait for SNMP response.
    checktime		-- (datetime) date+time at which measurement data was acquired.
    retries			-- (int) number of times to retry connection (default: 0)
    auto            -- (bool) whether to perform snmp checks immediately (use .check() when ready) 
    ''' 

    @classmethod
    def from_snmp(cls, hostname, idx, auto=True, **kwargs):
        '''constructs a SensorCheck object from SNMP data.
        
        This classmethod is expected to be used mainly from within the SensorHub class,
        but could potentially be used to do an individual sensor check when the idx 
        ("index") of the sensor on the hub is already known.
        
        To get a list of available sensors by index, see SensorHub.sensors_by_idx
        
        :param hostname: (required) hostname of hub to which sensor is attached.
        :param idx: (required) the integer "index" of the sensor on the hub. 
        :param auto: (optional) whether to perform a check immediately (default: True)
        '''
        return cls(hostname=hostname, idx=idx, auto=auto, **kwargs)
        
    @classmethod
    def from_record(cls, record, **kwargs):
        '''constructs a SensorCheck object from a CSV record (exported from equipment).
        
        :param record: (required) csv line containing SensorCheck data.
        '''
        CSVFORMAT = 'idx,measurement,checktime'
        raise NotImplementedError
        # TODO: make this actually work.
        #return cls(cls, auto=False, **kwargs)
        
    @classmethod
    def from_json(cls, jdoc):
        # use CustomJsonDecoder to convert checktime from isoformat back to python datetime
        jdict = json.loads(jdoc, cls=CustomJsonDecoder)
        return cls(**jdict)
    
    def __init__(self, *args, **kwargs):
        '''SensorCheck base constructor.
        
        Initializes all instance variables both supplied and implied (defaults: None).

        See class documentation for all available arguments.
        '''

        self.serial_base = kwargs.get('serial_base', None)

        self.name = kwargs.get('name', None)
        self.measurement = kwargs.get('measurement', None)
        self.units = kwargs.get('units', None)
        self.alarmhigh = kwargs.get('alarmhigh', None)
        self.alarmlow = kwargs.get('alarmlow', None)
        self.lastalarm = kwargs.get('lastalarm', None)
        self.alarm_status = kwargs.get('alarm_status', None)
        self.measurement_type = kwargs.get('measurement_type', None)
        self.serial = kwargs.get('serial', None)

        ## SNMP ##        
        self.hostname = kwargs.get('hostname', None)
        self.idx = kwargs.get('idx', None)
        self.timeout = kwargs.get('timeout', 10)
        self.snmp_method = kwargs.get('method', 'pysnmp')
        self.retries = kwargs.get('retries', 0)
        
        auto = kwargs.get('auto', True)
        
        if self.hostname:
    	    self.snmp_get = SNMPobject(hostname=self.hostname, timeout=self.timeout, 
    				method=self.snmp_method, retries=self.retries).snmp_getter()	    
	    
            if auto and self.idx:
    	        self.check()
    	        return

    def check(self):
        '''Uses object's snmp_get method to populate sensor variables, starting by
           acquiring individual datapoint names via get_sensor_oid function.
        '''
        idx = self.idx
        self.checktime = datetime.utcnow()
        
        self.name = self.snmp_get(get_sensor_oid(idx, 'name'))
        self.units = self.snmp_get(get_sensor_oid(idx, 'units'))
        
        self.measurement = self.snmp_get(get_sensor_oid(idx, 'measurement'))
        try:
            self.measurement = float(self.measurement)
        except ValueError:
            # we have a string, probably an 'N/A'
            pass
            
        self.alarmlow = float(self.snmp_get(get_sensor_oid(idx, 'alarmlow')))
        self.alarmhigh = float(self.snmp_get(get_sensor_oid(idx, 'alarmhigh')))
        self.alarm_status = self.snmp_get(get_sensor_oid(idx, 'alarm_status'))
        self.lastalarm = self.snmp_get(get_sensor_oid(idx, 'lastalarm'))
        self.measurement_type = self.snmp_get(get_sensor_oid(idx, 'measurement_type'))
        
        self.serial = self._get_serial()

    def _get_serial(self):
        if self.serial_base:
            return '%s%i' % (self.serial_base, self.idx)
        else:
            return self.snmp_get(get_sensor_oid(self.idx, 'serial'))

    def to_dict(self):
        return { 'idx': self.idx,
                 'name':  self.name,
                 'measurement':  self.measurement,
                 'units': self.units,
                 'alarmhigh': self.alarmhigh,
                 'alarmlow':  self.alarmlow,
                 'checktime': self.checktime,
                 'alarm_status': self.alarm_status,
                 'lastalarm': self.lastalarm,
                 'hostname':  self.hostname,
                 'measurement_type': self.measurement_type,
                 'serial': self.serial,
                }

    def to_json(self):
        return json.dumps(self.to_dict(), cls=CustomJsonEncoder)

    def __str__(self):
        out = "SensorCheck for Sensor %i at %s\n" % (self.idx, self.hostname)
        out += '%r' % self.to_dict()
        out += '\n'
        return out
        
