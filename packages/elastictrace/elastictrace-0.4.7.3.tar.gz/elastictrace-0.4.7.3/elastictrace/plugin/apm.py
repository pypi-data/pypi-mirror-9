import plugin
import os
import time
import glob

import asyncore
import cStringIO as c
import csv

class apm(plugin.Plugin):
    
    def __init__(self, **kwargs):
        super(apm, self).__init__()
        self.kwargs         = kwargs
        self.config         = kwargs['config']
        apm.old             = {'stats' : list(), 'trace': list()} 
        self.metric_type_id = self.get_metric_type_id('apm')
        plugin.PluginAsyncServ(handler='statsSock',handler_file='apm',socket_type='stream',socket_family='unix',bind='/var/run/elastictrace/apmStats.sock',reuse=True,sock_chmod=666)
        plugin.PluginAsyncServ(handler='traceSock',handler_file='apm',socket_type='stream',socket_family='unix',bind='/var/run/elastictrace/apmTrace.sock',reuse=True,sock_chmod=666)

        
        
        #return self
        
    def observe(self):
        self.log_time = self.logTime()
        
        stats   = apm.old['stats']
        traces  = apm.old['trace']
        apm.old = {'stats' : list(), 'trace': list()} 
        
        if len(stats) > 0:
            self.transmit_queue({'logTime': self.log_time, self.metric_type_id:'\n'.join(stats).encode('zlib').encode('base64'), 'encoding': ['base64', 'gzip', 'line', 'json']})
        
        if len(traces) > 0:
            for trace in traces:
                self.transmit_queue({'logTime': self.log_time, 'abcdef-123456':trace, 'encoding': ['base64', 'gzip', 'line', 'json']})

class statsSock(asyncore.dispatcher_with_send, apm):
    def handle_read(self):
        data = self.recv(8192)
        if data:
            data = csv.reader(c.StringIO(data), delimiter='\n', escapechar='\\').next()
            for d in data:
                apm.old['stats'].append(d)
                
class traceSock(asyncore.dispatcher_with_send, apm):
    def handle_read(self):
        data = self.recv(8192)
        if data:
            data = csv.reader(c.StringIO(data), delimiter='\n', escapechar='\\').next()
            for d in data:
                apm.old['trace'].append(d)
