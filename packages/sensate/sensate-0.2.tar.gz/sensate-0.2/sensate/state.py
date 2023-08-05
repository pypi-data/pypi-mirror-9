import os
from json import loads, dumps

try:
    STATE_DIR = os.environ['SENSATE_STATE_DIR']
except:
    STATE_DIR = os.path.join(os.path.expanduser('~'), '.sensate')

## WARNING: NON-TESTED CODE PORTED FROM ANOTHER THING ##

def _require_dir(loc):
    '''Make sure that loc is a directory. If it does not exist, create it.'''
    if os.path.exists(loc):
        if not os.path.isdir(loc):
            raise ValueError('%s must be a directory' % loc)
    else:
        os.makedirs(loc, 0755)

def save_state(state_dict, filename=None, state_path=STATE_DIR):
    _require_dir(state_path)
    
    # an idea for another day.
    #state_dict = experiment.to_dict()
    
    if filename==None:
        filename = experiment.name
    
    buf = dumps(state_dict, indent=2, separators=(',', ': '))
    statefile = os.path.join(state_path, filename)
    open(statefile, 'w').write(buf)
    return True

def restore_state(subnet, state_path='/tmp/labsensors'):
    _require_dir(state_path)
    statefile = statefile_path(subnet, state_path)
    buf=open(statefile).read()
    return loads(buf)
