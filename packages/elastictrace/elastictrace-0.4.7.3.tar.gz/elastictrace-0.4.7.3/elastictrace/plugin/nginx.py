import plugin
import os
import httplib
import urllib2
import urllib
import time
import traceback

class nginx(plugin.Plugin):
    
    def __init__(self, name, **kwargs):
        super(nginx, self).__init__()
        kwargs['name'] = 'nginx'
        self.kwargs = kwargs
        self.config = kwargs['config']
        self.metric_type_id = self.get_metric_type_id('nginx')
        
        self.old = list() #keeps last pass values
        #return self
        
    def observe(self):
        self.stdout("nginx start")
        start, payload = time.time(), dict()
        self.log_time = self.logTime()
        try:
            req = urllib2.urlopen(urllib2.Request(self.config['endpoint']))
            nginx, stale, value = list(), dict(), list()
            for dex,dat in enumerate(req.read().split("\n")):
                if dex != 1: #cuss we dont need that line
                    data = dat.split(" ")
                    if dex == 0:
                        stale['active'] = data[2]
                    elif dex == 2:
                        nginx.append(data[1])
                        nginx.append(data[2])
                        nginx.append(data[3])
                    elif dex == 3:
                        stale['reading'], stale['writing'], stale['waiting'] = data[1], data[3], data[5]
            try:
                for dex, dat in enumerate(nginx):
                    value.append(int(dat)-int(self.old[dex]))
            except: #except Exception, e:
                value = (0, 0, 0)
            self.old = list(nginx) #old is now what was current

            #set values
            payload['httpdStats'] = True
            payload['nginx'] =  dict(zip(('accept', 'handled', 'requests'),value))
            payload['nginx']['active'] = int(stale['active'])
            payload['nginx']['reading'] = int(stale['reading'])
            payload['nginx']['writing'] = int(stale['writing'])
            payload['nginx']['waiting'] = int(stale['waiting'])
            payload['nginx']['version'] = os.popen('nginx -v 2>&1').readline().split('/')[1][:-1]
            #print payload
        
        except Exception, e:
            self.stderr('Nginx Stats: '+str(e))
            #traceback.print_exc()
        
        #stdout(payload['nginx'])
        self.transmit_queue({self.metric_type_id: payload['nginx'], 'logTime': self.log_time, 'encoding': [None]})
        self.stdout('nginx_stats   : '+str(time.time()-start)) #set timer out going
