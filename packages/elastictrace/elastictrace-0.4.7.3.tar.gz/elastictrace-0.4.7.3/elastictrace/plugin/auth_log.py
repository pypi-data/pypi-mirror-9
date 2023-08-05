import plugin
import os
import sys
import time
import json
import syslog
import random

import lib.linux_metrics as lm


class auth_log(plugin.Plugin):

    def __init__(self, *args, **kwargs):
        super(base, self).__init__()
        self.kwargs         = kwargs
        self.config         = kwargs['config']
        self.conf           = None
        self.metric_type_id = {'auth_log': self.get_metric_type_id('auth_log')}
        self.Agent_self     = kwargs['agent_self']

        self.stdout(self.config)
        self.old = {'active': list()}  # keeps last pass values

        #return self
        
    def getAuthList(self):
        events = list()

        for x in os.popen('last -wFi').read().split('\n'):
            login = x.split()
            
            if len(login) < 5 or login[1] == "begins":
                continue
            
            if login[8] == 'still':
                end = None
            else:
                end = time.mktime(time.strptime(("{0}, {1} {2} {3} {4} GMT").format(login[9], login[10], login[11], login[12], login[13]), "%a, %B %d %X %Y %Z"))
            
            start = time.mktime(time.strptime(("{0}, {1} {2} {3} {4} GMT").format(login[3], login[4], login[5], login[6], login[7], login[8]), "%a, %B %d %X %Y %Z"))
            events.append({'user': login[0], 'login_time': start, 'logout_time': end, 'ip': login[2], 'terminal ':login[1]})
        
        return events

    def observe(self):
        self.log_time = self.logTime()
        sessions = self.getAuthList()
        self.payload = {'closed': list(), 'opened': list()}
        
        for session in sessions: #list all the sessions we got not to long ago
            # find sessions that we once opened and now closed
            not_seen = True
            """
            for active in self.old['active']:
                if session['logout_time'] is not None and 
                        session['login_time'] == active['login_time'] and 
                        session['ip'] == active['ip'] and 
                        session['terminal'] == active['terminal'] and 
                        session['user'] == active['user']:
                    
                    self.payload['closed'].append(session)
                    not_seen = False #it has been seen
                    
            if not_seen is True: #find new sessions
                self.payload['new'].append(session) #reagdless we need to send this data upstream
                
                if session['logout_time'] is None: #is this session still active
                    self.old['active'].append(session)
                else:
                    self.payload['closed'].append(session)
            """
        
        self.transmit_queue({self.metric_type_id['auth_log']: json.dumps(self.payload).encode('zlib').encode('base64'), 'logTime': self.log_time, 'encoding': ['base64', 'gzip', 'json']})
