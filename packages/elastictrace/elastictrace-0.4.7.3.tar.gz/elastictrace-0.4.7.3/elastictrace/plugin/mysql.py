import plugin
import os
import time

class mysql(plugin.Plugin):
    def __init__(self, **kwargs):
        super(mysql, self).__init__()
        self.kwargs = kwargs
        self.config = kwargs['config']
        self.metric_type_id = self.get_metric_type_id('mysql')
        self.old = {'bytes_received' : None, 'bytes_sent' : None, 'slow_queries' : None, 'queries' : None, 'qcache_lowmem_prunes' : None, 'qcache_not_cached' : None, 'qcache_queries_in_cache' : None, 'qcache_inserts' : None, 'qcache_hits' : None, 'connections' : None, 'aborted_clients' : None, 'delete' : None, 'update' : None, 'replace' : None, 'replace_select' : None, 'select' : None, 'insert' : None, 'insert_select' : None, 'delete_multi' : None, 'update_multi' : None, 'commit' : None, 'rollback' : None}
        
        #base settings
        if self.config.has_key('host'):
            host = self.config['host']
        else:
            host = '127.0.0.1'

        if self.config.has_key('port'):
            port = str(self.config['port'])
        else:
            self.port = '3306'

        if self.config.has_key('user'):
            port += " --user="+self.config['user']

        if self.config.has_key('passwd'):
            port += " --password="+self.config['passwd']
        
        self.mysql_line = "mysql --host="+host+" --port="+port
        #return self
        
    def observe(self):
        self.stdout("mysql start")
        start, payload = time.time(), dict()
        try:
            info = {'version' : None}
            last_min, start = self.logTime(), time.time()
            stats = dict()
            
            for line in os.popen("echo 'SHOW GLOBAL STATUS' | "+self.mysql_line).read().lower().replace('com_', '').split("\n")[1:-1]:
                line = line.split("\t")

                if self.old.has_key(line[0]) == True: #make sure the stat is the one we want
                    try:
                        stats[line[0]] = int(line[1])-self.old[line[0]]
                    except:
                        pass
                    self.old[line[0]] = int(line[1]) #save the new value
            
            for line in os.popen("echo 'SHOW GLOBAL VARIABLES' | "+self.mysql_line).read().lower().split("\n")[1:-1]:
                line = line.split("\t")

                if info.has_key(line[0]) == True:
                    #print line[0]
                    stats[line[0]] = line[1]

            #print stats
            self.transmit_queue({'logTime': last_min, self.metric_type_id: stats, 'encoding': [None]})
            self.transmit_queue(stats)
        finally:
            self.stdout('mysql   : '+str(time.time()-start)) #set timer out going
