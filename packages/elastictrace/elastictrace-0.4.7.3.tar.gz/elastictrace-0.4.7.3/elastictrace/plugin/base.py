import plugin
import os
import glob
import time
import hashlib
import json
import syslog
import socket
import telnetlib
import sys
import random

import lib.linux_metrics as lm


class base(plugin.Plugin):

    def __init__(self, *args, **kwargs):
        super(base, self).__init__()
        self.kwargs         = kwargs
        self.config         = kwargs['config']
        self.conf           = None
        self.metric_type_id = {'base': self.get_metric_type_id('base')}
        self.Agent_self     = kwargs['agent_self']

        self.stdout(self.config)
        self.old = {'ipv4': dict(), 'ipv6': dict()}  # keeps last pass values

        #return self
        

    def observe(self):
        self.log_time = self.logTime()
        
        
            
        
        
        self.transmit_queue({self.metric_type_id['base']: json.dumps(self.payload).encode('zlib').encode('base64'), 'logTime': self.log_time, 'encoding': ['base64', 'gzip', 'json']})
