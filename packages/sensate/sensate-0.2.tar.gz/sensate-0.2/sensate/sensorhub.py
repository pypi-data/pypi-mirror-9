from datetime import datetime
import json

from sensorcheck import SensorCheck
from utils import CustomJsonEncoder, CustomJsonDecoder

from transports.snmp import SNMPobject
from equipment import web600, wsg30

HUB_OIDS = { 'MAC': '1.3.6.1.4.1.8338.1.1.4.1.6.28.0', 
             'ntp': '.1.3.6.1.4.1.8338.1.1.4.1.6.27.0',
             'model': '.1.3.6.1.4.1.8338.1.1.4.1.7.37.0' }     # wsg30 string: "Wireless Sensor Gateway" }

class SensorHub(object):
    '''The central communications hub that sensors report back to. 

    Uses SNMP to poll the hub directly over the network. 
    
    Required argument:  
    
    hostname                -- (string) fqdn or LAN-routable hostname (no protocol prefix)
    
    Optional keyword arguments:
    
    match           -- (string) restrict results to only those sensors with `match` in their name
    auto            -- (bool) whether to perform SNMP connections immediately (default: True)
    port            -- (int) port used to connect via snmp (default: 161)
    timeout         -- (int or float) time in seconds to wait for SNMP response.
    retries			-- (int) number of times to retry connection (default: 0)
    snmp_method     -- (string) if pysnmp isn't working for you, try 'cli' (default: 'pysnmp')
    
    Currently decoration-only attributes that can be set by keyword arguments:
    
    model           -- (string) defines model of Sensaphone equipment (default: WSG30)
    ''' 
    
    def __init__(self, hostname, **kwargs):
        '''
        Constructor for SensorHub.

        Uses SNMP to poll the hub directly over the network.
           
        Supply "match" to restrict results to only those sensors
        with "match" in their name.

        :param hostname: (required) fqdn or reachable local hostname.
        :param match: (optional) only load sensors where match (string) can be found in name.
        '''
    
        self.hostname = hostname   
        self.mac_address = ''
        self.serial_base = None
        self.match = kwargs.get('match', '')
        
        # whether to complete SNMP checks immediately
        auto = kwargs.get('auto', True)

        self.snmp_method = kwargs.get('snmp_method', 'pysnmp')
        self.retries = kwargs.get('retries', 0)
        # generic timeout length in seconds for any type of connection.
        self.timeout = kwargs.get('timeout', 10)  
        
        # Updated every time snmp_check_sensors used.
        self.lastchecktime = None

        # Assign self.snmp_get to a generated snmp get function.  
        self.snmp_get = SNMPobject(hostname=self.hostname, timeout=self.timeout,
            			retries=self.retries, method=self.snmp_method).snmp_getter()
        # MODEL DETECTION. If kwarg model supplied, skip model detection.
        self.model = str(kwargs.get('model', 'autodetect')).upper()
        if self.model == 'AUTODETECT':
            self.model = self._autodetect_model()
        
        ## SNMP ##
        if self.model == 'WSG30':            
            self.get_sensor_oid = wsg30.get_sensor_oid
            self.STATUS_TROUBLE = wsg30.STATUS_TROUBLE 
            self.ALARM_HIGH = wsg30.ALARM_HIGH 
            self.ALARM_LOW = wsg30.ALARM_LOW
            self.STATUS_OK = wsg30.STATUS_OK
            self.BATTERY_LOW = wsg30.BATTERY_LOW 
            self.MAX_SENSORS_PER_HUB = wsg30.MAX_SENSORS_PER_HUB
            
        if self.model == 'WEB600':
            self.get_sensor_oid = web600.get_sensor_oid
            self.STATUS_TROUBLE = web600.STATUS_TROUBLE 
            self.ALARM_HIGH = web600.ALARM_HIGH 
            self.ALARM_LOW = web600.ALARM_LOW
            self.STATUS_OK = web600.STATUS_OK
            self.BATTERY_LOW = web600.BATTERY_LOW
            self.MAX_SENSORS_PER_HUB = web600.MAX_SENSORS_PER_HUB
 

        self.sensors_by_idx = {}   # idx: name mapping. Filled during discover()
        self.checks_by_idx = {}    # idx: SensorCheck mapping. Filled during check()
        self.checks_by_serial = {} # serial: SensorCheck mapping. Filled during check()
        self.checks = []
        self.alarms = { 'high': [], 'low': [], 'low_battery': [], 'trouble': [] }

        if auto:
            self._get_MAC()
            self.reload()

    def _autodetect_model(self):
        result = self.snmp_get(HUB_OIDS['model'])
        if result=='Wireless Sensor Gateway':
            return 'WSG30'
        elif result=='Web600':
            return 'WEB600'

    def _get_MAC(self):
        self.mac_address = self.snmp_get(HUB_OIDS['MAC'])
        if self.model == 'WEB600':
            self.serial_base = ''.join(self.mac_address.split('-')[3:6])

    def _process_alarms(self, check):
        if check.alarm_status == self.BATTERY_LOW:
            self.alarms['low_battery'].append(check)
        elif check.alarm_status == self.STATUS_TROUBLE:
            self.alarms['trouble'].append(check)
        elif check.alarm_status == self.ALARM_HIGH:
            self.alarms['high'].append(check)
        elif check.alarm_status == self.ALARM_LOW:
            self.alarms['low'].append(check)

    def check(self):
        '''Populates and returns self.checks by retrieving SensorCheck objects via SNMP (destructive update)
        
        Also sets up self.checks_by_idx (idx to SensorCheck mapping) and self.checks_by_serial
        (they have both been useful in different contexts, so let's have both.)
        ''' 
        self.checks = []
        self.checks_by_idx = {}
        self.checks_by_serial = {}
        
        for idx in self.sensors_by_idx.keys():
            checktime = datetime.utcnow()
            check = SensorCheck.from_snmp(self.hostname, idx, name=self.sensors_by_idx[idx], checktime=checktime, serial_base=self.serial_base)
            self.checks.append(check)
            self.checks_by_idx[idx] = check
            # ignore Power and Battery for checks_by_serial mapping.
            if check.serial != '0':
                self.checks_by_serial[check.serial] = check
            self._process_alarms(check)

    def discover(self):
        '''Populates and returns self.sensors_by_idx (destructive update)
        
        :rtype: dictionary mapping of sensor index (int) to name (str) 
        '''
        self.sensors_by_idx = {} 
        self.lastchecktime = datetime.utcnow()
        
        for idx in range(self.MAX_SENSORS_PER_HUB+1):
            name = self.snmp_get(self.get_sensor_oid(idx, 'name'))
            # we sometimes get garbage characters in the sensor name :(
            try:
                name.decode()
            except UnicodeDecodeError, e:
                #TODO: CONVERT name (don't just give up on it)
                continue
            except AttributeError, e:
                # name was returned as None
                continue

            if self.match:
                if self.match in name:
                    self.sensors_by_idx[idx] = name
            else:
                if name and name != 'Unconfigured':
                    self.sensors_by_idx[idx] = name
        return self.sensors_by_idx

    def reload(self):
        '''Convenience interface to self.discover() and self.check()'''
        self.discover()
        self.check()
    
    def __str__(self):
        out = 'Sensaphone Hub at %s\n\n' % self.hostname
        for idx in sorted(self.sensors_by_idx.keys()):
            out += '%d: %s\n' % (idx, self.sensors_by_idx[idx])
        return out
    
    def to_dict(self, by_idx=False):
        '''returns dictionary representing hub and all checked sensors.
        
        if self.check() has successfully run, the 'sensors' key will have 
        self.checks_by_serial as its value, or self.checks_by_idx if by_idx=True.
        
        if only self.discover() has run, the 'sensors' key = self.sensors_by_idx
        '''
        
        if self.checks_by_idx:
            if by_idx:
                sensord = dict([(k,v.to_dict()) for k,v in self.checks_by_idx.items()])
            else:
                sensord = dict([(k,v.to_dict()) for k,v in self.checks_by_serial.items()])
        else:
            sensord = self.sensors_by_idx

        return { 'hostname': self.hostname,
                 'lastchecktime': self.lastchecktime,
                 'match': self.match,
                 'model': self.model,
                 'sensors': sensord,
                 'alarms': self.alarms
               }

    def to_json(self, by_idx=False):
        return json.dumps(self.to_dict(by_idx), cls=CustomJsonEncoder)
        
