import os
import re
import telnetlib

import plugin

class memcached(plugin.Plugin):
    def __init__(self, **kwargs):
        super(memcached, self).__init__()
        self.kwargs = kwargs
        self.config = kwargs['config']
        
        self.old = dict() #keeps last pass values
        self.regex = re.compile(ur"STAT (.*) (.*)\r")
        self.diff_keys = ('bytes_read', 'bytes_written', 'cas_badval', 'cas_hits', 'cas_misses', 'cmd_flush', 'cmd_get', 'cmd_set', 'decr_hits', 'decr_misses', 'delete_hits', 'delete_misses', 'evictions', 'get_hits', 'get_misses', 'incr_hits', 'incr_misses', 'reclaimed', 'rusage_system', 'rusage_user') #we need to diff prev from current on these values
        #return self
        
    def observe(self):
        self.stdout("memcached start")
        start, payload = time.time(), dict()
        try:
            start, last_min = time.time(), self.get_last_min() #get current log_time
            payload = dict()
            try:
                client.write("stats\n") #write to telnet
                memcacheStats_curr = dict(self.regex.findall(client.read_until('END'))) #get memcache stats
            except:
                client = telnetlib.Telnet(self.agentConfig['memcache']['host'], self.agentConfig['memcache']['port']) #open connection if it is closed
                client.write("stats\n") #write to telnet
                memcacheStats_curr = dict(self.regex.findall(client.read_until('END'))) #get memcache stats

            payload = memcacheStats_curr.copy() #set to the current value so we dont loose keys we dont do math on
            if len(self.old) > 1: #more than one memcache stats
                for dex in self.diff_keys:
                    payload[dex] = float(memcacheStats_curr[dex]) - float(self.old[dex]) #diff the values and save them correctly

            else: #set to 0 so the first load does not look crazy high
                for dex in self.diff_keys:
                    payload[dex] = 0 #diff the values and save them correctly
            self.old = memcacheStats_curr.copy() #flip the values over a little
            payload = memcacheStats_curr.copy()
            client.write("version")
            payload['version'] = client.read_until("\n").split(' ')[1]
            self.transmit_queue(payload)
        finally:
                stdout('memcacheStats : '+str(time.time() - start)) #write to output so we can see whats going on
