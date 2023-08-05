from json import loads,dumps

from sensorcheck import SensorCheck
from sensorhub import SensorHub
from transports.snmp import SNMPobject

DEFAULT_SAMPLERATE = 500.0      # 500 seconds.

class Experiment(object):

    """basic Experiment object.

        keyword argument set attributes:

        name            -- (string)   human-friendly string describing experiment (default: '')
        start           -- (datetime) time at which to kick off experiment (default: None)
        end             -- (datetime) time at which to end experiment (default: None)
        savegame        -- (bool) whether to allow state save / reload (default: True)
        samplerate      -- (float) interval in seconds (default: %f)
        
        attributes set during operation:
        
        savegame_file   -- (string) path to state file 
        
    """ % DEFAULT_SAMPLERATE

    def __init__(self, *args, **kwargs):
    
        self.name = kwargs.get('name', '')
        self.start = kwargs.get('start', datetime.now())
        self.end = kwargs.get('end', None)
        self.savegame = kwargs.get('savegame', True)
        self.samplerate = float(kwargs.get('samplerate', DEFAULT_SAMPLERATE))
        
        self.savegame_file = ''

    @classmethod
    def from_savegame(cls, statefile, **kwargs):
        state = loads(statefile)
        
        meta = state['meta']
        print meta
    
        return cls(savegame=True, **meta)

    def run():
        "Like main() in a command line script -- makes experiment go."
        if self.start == None:
            self.start = datetime.now()
        print "Running!"

    def save():
        "Save state, enabling us to shut down experiment and start later where we left off."
        raise NotImplementedError
        
    def load():
        "Load state, picking up experiment where we left off."
        raise NotImplementedError


class SensorBatteryExperiment(Experiment):

    """SensorBatteryExperiment object (inherits from Experiment)."""

    def __init__(self, idx, hostname, *args, **kwargs):
        self.idx = idx
        self.hostname = hostname

        self.snmp_get = SNMPobject(hostname).snmp_getter()

        self.state_oids = { 'battery_status': get_sensor_oid('intPower'),
                            'measurement': get_sensor_oid('measurement'),
                            'units': get_sensor_oid('units'),
                            'measurement_type': get_sensor_oid('measurement_type'),
                          }
        self.timeseries_data = { }

    def get_status(self):
        for codename in list(timeseries_data.keys()):
            self.timeseries_data[codename] = self.snmp_get(self.state_oids[codename])
        if self.savegame:
            self.save()

    def poll(self):
        "use SNMP to check availability and alarm status of sensor."
        self.statuses.append(  self.get_status() ) 

    def run(self):
        while datetime.now() < self.end:
            poll()
            time.sleep(self.interval)

    def to_dataframe(self):
        from pandas import DataFrame
        return DataFrame(self.timeseries_data)
