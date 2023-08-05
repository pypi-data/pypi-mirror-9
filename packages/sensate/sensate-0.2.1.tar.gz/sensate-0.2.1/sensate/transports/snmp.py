__doc__='''SNMPobject class and helper functions.
 
Relies either on pysnmp (default) or snmpget on the command line (see snmp_get method).

pysnmp is used to avoid having to install snmp command line tools (also because pysnmp is
a pure-python implementation of the SNMP protocol).  The pysnmp commands are modeled on the
following magic SNMP incantations:

# Retrieve a single value:
#
# snmpget -v 2c -c public -OvQ sensaphone1.458.locusdev.net:161 .1.3.6.1.4.1.8338.1.1.4.1.1.2.15
# or
# snmpget -v2c -c public -ObentU sensaphone1.458.locusdev.net 1.3.6.1.4.1.8338.1.1.4.1.1.1.2.15
#
# Walk the whole sensaphone:
#
# snmpwalk -v 2c -m ALL -Os -c public sensaphone1.458.locusdev.net:161 1.3.6.1.4.1.8338.1.1.4
'''
__author__='nthmost'

from subprocess import Popen, PIPE
from socket import gethostbyname, gaierror
from pysnmp.entity.rfc3413.oneliner import cmdgen

SNMP_DEFAULT_PORT = 161
SNMP_DEFAULT_PROTOCOL = '2c'
SNMP_DEFAULT_COMMUNITY = 'public'
SNMP_DEFAULT_TIMEOUT = 3
SNMP_DEFAULT_RETRIES = 0
SNMP_DEFAULT_HOSTNAME = None
SNMP_DEFAULT_METHOD = 'pysnmp'       # 'pysnmp' or 'cli'

class SNMPobject(object):
    def __init__(self, *args, **kwargs):
        self.hostname = kwargs.get('hostname', SNMP_DEFAULT_HOSTNAME) 
        self.port = kwargs.get('port', SNMP_DEFAULT_PORT)
        self.protocol = str(kwargs.get('protocol', SNMP_DEFAULT_PROTOCOL))
        self.community = kwargs.get('community', SNMP_DEFAULT_COMMUNITY)
        self.timeout = kwargs.get('timeout', SNMP_DEFAULT_TIMEOUT)
        self.retries = kwargs.get('retries', SNMP_DEFAULT_RETRIES)
        self.method = kwargs.get('method', SNMP_DEFAULT_METHOD)
        
        self._results = {}      # keep a store of previously acquired results
        
        if self.protocol not in ['1', '2c', '3']:
            raise Exception('Invalid protocol "%s" supplied to SNMPobject' % self.protocol)

        # set up a pysnmp CommandGenerator to use repeatedly.
        if self.method=='pysnmp':
            self._cmdGen = cmdgen.CommandGenerator()
        else:
            self._cmdGen = None
        
        # set snmp_get to desired method, using function creator method snmp_getter
        self.snmp_get = self.snmp_getter(method=self.method)
        
    def snmp_getter(self, method='pysnmp'):
        '''Returns snmp_get function.  Supply method='cli' to switch to CLI snmpget tool.'''
        
        if method=='pysnmp':
            return self._pysnmp_get(self.hostname, self.port, self.protocol, self.community, 
                                    self.retries, self.timeout)
        else:
            return self._cli_get(self.hostname, self.port, self.protocol, self.community, 
                                    self.retries, self.timeout)

    def _cli_get(self, hostname, port, protocol, community, retries, timeout):
        '''constructs a pysnmp-based snmp_get function with baked-in parameters.
        
        :return: function snmp_get(oid) 
        '''
        def snmp_get(oid):
            snmpproc = Popen(['snmpget',
                          '-v', protocol,
                          '-c', community,
                          '-r', retries,
                          '-t', timeout,
                          '-OvQ',
                          '%s:%s' % (hostname, port),
                          oid],
                         stdout=PIPE)    
            value = snmpproc.communicate()[0].strip()
            return value.strip('"')
        return snmp_get

    def _pysnmp_get(self, hostname, port, protocol, community, retries, timeout):   
        '''returns a pysnmp-based snmp_get function with baked-in parameters.
        
        :return: function snmp_get(oid) 
        '''
        _cmdGen = cmdgen.CommandGenerator()

        def snmp_get(oid):
            (errorIndication, errorStatus, 
                errorIndex, varBinds) = _cmdGen.getCmd(
                                        cmdgen.CommunityData(community),
                                        cmdgen.UdpTransportTarget((hostname, port), 
                                        timeout=timeout, retries=retries), 
                                        oid)
            if errorIndication:
                raise Exception(errorIndication)

            if errorStatus:
                raise Exception('%s at %s\n' % 
                           (errorStatus.prettyPrint(),
                            errorIndex and varBinds[int(errorIndex)-1] or '?'))                       
            return '%s' % varBinds[0][1]
        return snmp_get
        
        

# BEHOLD THE MAGIC SNMP INCANTATIONS
#
# Retrieve a single value:
#
# snmpget -v 2c -c public -OvQ sensaphone1.458.locusdev.net:161 .1.3.6.1.4.1.8338.1.1.4.1.1.2.15
# or
# snmpget -v2c -c public -ObentU sensaphone1.458.locusdev.net 1.3.6.1.4.1.8338.1.1.4.1.1.1.2.15
#
# Walk the whole sensaphone:
#
# snmpwalk -v 2c -m ALL -Os -c public sensaphone1.458.locusdev.net:161 1.3.6.1.4.1.8338.1.1.4
