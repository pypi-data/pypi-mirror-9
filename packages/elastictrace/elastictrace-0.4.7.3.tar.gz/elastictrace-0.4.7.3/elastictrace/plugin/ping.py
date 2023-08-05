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

import elastictrace.lib.linux_metrics as lm


class ping(plugin.Plugin):

    def __init__(self, *args, **kwargs):
        super(ping, self).__init__()
        self.kwargs         = kwargs
        self.config         = kwargs['config']
        self.conf           = None
        self.metric_type_id = {'ping': self.get_metric_type_id('ping')}
        self.Agent_self     = kwargs['agent_self']

        self.stdout(self.config)
        self.old = {}  # keeps last pass values

        #return self
        
    def is_ip(self, ip):
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False
            
    def get_ip(self, hostname):
        if self.is_ip is False:
            try:
                return socket.gethostbyname(hostname)
            except:
                return None
        return hostname

    def observe(self):
        self.log_time = self.logTime()
        
        if self.conf is None or random.randint(1, 10) == 1:
            
            try:
                
                conf = self.get_metric_config([ self.metric_type_id['ping'] ]).get('metric_config', {}).get(self.metric_type_id['ping'])
            except:
                conf = False
        
            if conf is not None and conf is not False:
                self.conf = conf
            else:
                self.conf = None
                self.stderr("Failed to get metric_config")
        
        if self.conf is not None:
            self.payload  = {'latency' : dict()}
            

            for line in self.conf['latancy']:
                host = line['host']
                port = random.choice(line['port'])
                try:
                    ai_list = socket.getaddrinfo(host, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
                    self.payload['latency'][host] = 0  #set default
                    counter = 0;
                
                except socket.gaierror:
                    self.stderr(host+" - getaddrinfo() error: {0}".format(sys.exc_info()[1]))
                    continue
                
                for (family, socktype, proto, canon, sockaddr) in ai_list:
                    curr_socket = socket.socket(family, socktype)
                    
                    try:
                        start_time = time.time()
                        curr_socket.connect(sockaddr)
                        self.payload['latency'][host] += (float(time.time()-start_time))
                        counter += 1
                        curr_socket.close()
                    
                    except socket.timeout:
                        try:
                            self.payload['latency'][host] += (float(time.time()-start_time))
                            counter += 1
                            curr_socket.close()
                        except:
                            pass
                        
                    except:
                        curr_socket.close()
                        pass
                
                try:
                    self.payload['latency'][host] = self.payload['latency'][host]/float(counter)
                except:
                    self.payload['latency'][host] = None
                    
            self.transmit_queue({self.metric_type_id['ping']: json.dumps(self.payload).encode('zlib').encode('base64'), 'logTime': self.log_time, 'encoding': ['base64', 'gzip', 'json']})
