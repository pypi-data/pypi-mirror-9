import plugin
import os
import asyncore
import lib.tail
import cStringIO as c
import csv
import time

class helloworld(plugin.Plugin):
    
    def __init__(self, **kwargs):
        super(helloworld, self).__init__()
        kwargs['name'] = 'helloworld'
        self.kwargs = kwargs
        self.config = kwargs['config']
        self.kwargs['name'] = 'helloworld2'
        helloworld.old = list() #keeps last pass values
        #plugin.PluginAsyncServ(handler='hellosock',handler_file='helloworld',socket_type='stream',socket_family='unix',bind='/tmp/unix.sock',reuse=True,sock_chmod=666)
        #return self
        
        #t = lib.tail.Tail()
        #t.tail('/tmp/tail1.txt', self.print2)
        #t.follow(1)
        
    def observe(self):
        print helloworld.old
        #print len(helloworld.old)
        helloworld.old = list()
        self.stdout("Hello World")
        self.transmit_queue({'loadavg' : os.getloadavg()})
        
    def print2(self, dump):
        print dump
        helloworld.old.append(dump)

class hellosock(asyncore.dispatcher_with_send, helloworld):
    def handle_read(self):
        data = self.recv(8192)
        #print data
        time.sleep(5)
        if data:
            data = csv.reader(c.StringIO(data), delimiter='\n', escapechar='\\').next()
            
            print len(data)
            print type(data)
            for d in data:
                helloworld.old.append(d)
    
