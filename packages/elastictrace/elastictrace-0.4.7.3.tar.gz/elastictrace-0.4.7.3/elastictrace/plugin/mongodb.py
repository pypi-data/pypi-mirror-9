import plugin
import os
"""
class mongodb(plugin.Plugin):
    def __init__(self, **kwargs):
        super(mongodb, self).__init__()
        self.kwargs = kwargs
        self.config = kwargs['config']
        
        self.old    = {'network' : {'bytesIn' : None, 'bytesOut' : None, 'numRequests' : ""}, 'opcounters' : {'insert' : None, 'query' : None, 'update' : None, 'delete' : None, 'getmore' : None, 'command' : None}} #, locks, queue, cursor should get added later
        
        if self.agentConfig['mongodb'].has_key('host'):
            mongoHost = self.agentConfig['mongodb']['host']
        else:
            mongoHost = "127.0.0.1"

        if self.agentConfig['mongodb'].has_key('port'):
            mongoPort = str(self.agentConfig['mongodb']['port'])
        else:
            mongoPort = "27017"
        self.mongoConnect = 'mongo --host '+mongoHost+' --quiet --eval "printjson(%s)" %s'
        
    def observe(self):
        self.stdout("mongodb start")
        start, payload = time.time(), dict()
        try:
                mongoStats_temp = dict()
                last_min, start = self.get_last_min(), time.time()
                mongoStats = {'stats' : {'locks' : dict()}}
                mongodbsCmd = os.popen(mongoConnect % ("db.adminCommand('listDatabases')","", )).read()
                mongodbsCmd = json.loads(mongodbsCmd, object_hook=_decode_dict)
                serverStats = json.loads(stripMongo(os.popen(mongoConnect % ("db.serverStatus()","", )).read()), object_hook=_decode_dict)
                version = serverStats['version']
                dbs = dict()
                for sub in mongodbsCmd['databases']:
                    if sub['empty'] == False:
                        db = dict()
                        db['sizeOnDisk'] = sub['sizeOnDisk']
                        db['stats'] = json.loads(os.popen(mongoConnect % ("db.stats()",sub['name'], )).read(), object_hook=_decode_dict)

                        #get collection data
                        db['collection'] = dict()
                        collectionStats = os.popen(mongoConnect % ('db.printCollectionStats()',sub['name'], )).read().split('---')[:-1]
                        for colStats in collectionStats:
                            colStats = colStats.split("\n")
                            #print colStats
                            for s in range(len(colStats)):
                                if colStats[s] != "":
                                    break
                            try:
                                db['collection'][colStats[s]] = json.loads(''.join(colStats[(s+1):]).replace("\t", ''), object_hook=_decode_dict)
                            except Exception, e:
                                db['collection'][colStats[s]] = str(e)
                        #print db['collection']
                        dbs[sub['name']] = db
                #print serverStats
                #merge some easy stats
                for key,value in self.old.iteritems():
                    mongoStats['stats'][key] = dict()
                    for dex,dat in value.iteritems():
                        try:
                            mongoStats['stats'][key][dex] = serverStats[key][dex] - dat
                            self.old[key][dex] = serverStats[key][dex]
                        except:
                            #mongoStats['stats'][key][dex] = 0
                            self.old[key][dex] = serverStats[key][dex]

                #extra stats
                mongoStats['stats']['connections'] = serverStats['connections']
                if serverStats['process'] == 'mongod':
                    mongoStats['stats']['cursors']= serverStats['cursors']['totalOpen'] #cursors
                    mongoStats['stats']['queue'] = {'total' : serverStats['globalLock']['currentQueue']['total'], 'reads' : serverStats['globalLock']['currentQueue']['readers'], 'writes' : serverStats['globalLock']['currentQueue']['writers']} #queues

                    try: #try page faults
                        mongoStats['stats']['pageFaults'] = serverStats['extra_info']['page_faults'] - mongoStats_temp['page_faults']
                    except:
                        pass
                    mongoStats_temp['page_faults'] = serverStats['extra_info']['page_faults']

                    try: #locks well global for now
                        mongoStats['stats']['locks']['global'] = (float(serverStats['globalLock']['lockTime']) - mongoStats_temp['globalLock']['lockTime'])/(float(serverStats['globalLock']['totalTime']) - mongoStats_temp['globalLock']['totalTime'])
                    except:
                        mongoStats_temp['globalLock'] = dict()
                    mongoStats_temp['globalLock']['totalTime'] = float(serverStats['globalLock']['totalTime'])
                    mongoStats_temp['globalLock']['lockTime'] = float(serverStats['globalLock']['lockTime'])

                mongoStats['info'] = {'host': serverStats['host'] , 'version' : serverStats['version'], 'process' : serverStats['process'], 'pid' : serverStats['pid'], 'uptime' : serverStats['uptime']}
                mongoStats['database'] = dbs
                mongoStats['version'] = version
                self.dataSet[last_min]['mongoStats'] = mongoStats
                self.transmit_queue(mongoStats)
                #print mongoStats
"""
