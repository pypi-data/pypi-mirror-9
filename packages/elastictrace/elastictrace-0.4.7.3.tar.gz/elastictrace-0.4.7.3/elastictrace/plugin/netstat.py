import plugin
import os
import time
import json
import syslog
import sys
import subprocess
import psutil

import elastictrace.lib.linux_metrics as lm


class netstat(plugin.Plugin):

    def __init__(self, *args, **kwargs):
        super(netstat, self).__init__()
        self.kwargs         = kwargs
        self.config         = kwargs['config']
        self.conf           = None
        self.metric_type_id = {'netstat': self.get_metric_type_id('netstat')}
        self.Agent_self     = kwargs['agent_self']

        self.stdout(self.config)
        self.old = {'ipv4': dict(), 'ipv6': dict()}  # keeps last pass values

        #return self
        
        
    def diffOld(self, proto, new):
        if self.old[proto]:
            self.payload[proto] = dict()
            for dex, dat in new.items():
                if self.old[proto][dex]:
                    self.payload[proto][dex] = dict()
                    self.payload[proto][dex] = dict((key, dat[key] - self.old[proto][dex].get(key, dat[key])) for key in dat.keys())


                
                self.old[proto][dex] = new[dex]
            
            return self.payload[proto]
        else:
            self.old[proto] = new #set the new to old
            return None
            
    def ip_in_scope(self, listen, conn):
        #exact match or wildcard
        if listen in ["::", "0.0.0.0", conn]:
            return True

        #ipv6 local with ipv4 local
        elif conn in ["::1", "127.0.0.1"]:
            return True

        return False

    def observe(self):
        self.payload  = dict()
        self.log_time = self.logTime()
        
        protos = ('TcpExt', 'IpExt', 'UdpLite', 'Udp', 'Ip', 'Icmp', 'Tcp',)
        netstat = subprocess.Popen("nstat -za", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        netstat4 = {'Tcp': dict(), 'Udp':dict(), 'Ip':dict(), 'Icmp':dict(), 'TcpExt': dict(), 'IpExt': dict(), 'UdpLite': dict()}
        netstat6 = {'Tcp': dict(), 'Udp':dict(), 'Ip':dict(), 'Icmp':dict(), 'TcpExt': dict(), 'IpExt': dict(), 'UdpLite': dict()}

        for line in netstat.stdout.read().split("\n"):
            stat = line.split()
            if len(stat) != 3:
                continue
                
            if len(stat[0].split("6", 1)) == 2:
                protoTemp = stat[0].split("6", 1)
                try:
                    netstat6[protoTemp[0]][protoTemp[1]] = int(stat[1])
                except:
                    pass
                continue
                
            for proto in protos:
                if stat[0].startswith(proto, 0) is True:
                    netstat4[proto][stat[0].split(proto, 1)[1]] = int(stat[1])
                    break
        
        result4 = self.diffOld('ipv4', netstat4)
        result6 = self.diffOld('ipv6', netstat6)

        cons      = psutil.net_connections('all')
        opened    = dict()
        connected = list()

        for con in cons:
            con_family = None
            con_type   = None
            
            #switch convert family to string
            con_family = {
                1:  'unix',
                2:  'ipv4',
                10: 'ipv6',
            }.get(con.family, None)
            
            #switch covert type to sting
            con_type = {
                1: 'tcp',
                2: 'udp',
                3: 'raw', 
                4: 'rdm',
                5: 'seq',
            }.get(con[2], None)
            
            #get a list of all the connected clients
            if con.raddr is not None and len(con.raddr) > 0:
                connected.append({
                    'raddr': con.raddr,
                    'laddr': con.laddr,
                    'pid': con.pid,
                    'family': con_family,
                    'type': con_type,
                    'status': con.status,
                })
            
            #get a list of all the listening connections    
            if con.raddr is not None and len(con.raddr) == 0:
                opened_key = '{0}/{1}/{2}'.format(con_type, con.laddr[0], con.laddr[1])
                if opened.get(opened_key) is None:
                    opened[opened_key] = {
                        'addr': con.laddr[0],
                        'port': con.laddr[1],
                        'pid': [con.pid],
                        'family': con_family,
                        'type': con_type,
                        'clients': dict(),
                        'count': 0,
                        'status': dict(),
                    }
                else:
                    opened[opened_key]['pid'].append(con.pid)
                    
        for conn_con in connected:
            for opened_key, open_con in opened.iteritems():
                if open_con['type'] == conn_con['type'] and open_con['port'] == conn_con['laddr'][1] and self.ip_in_scope(open_con['addr'], conn_con['laddr'][0]) is True:
                    open_con['count'] += 1
                    
                    if open_con['status'].get(conn_con['status'].lower()) is not None:
                        open_con['status'][conn_con['status'].lower()] += 1
                    else:
                        open_con['status'][conn_con['status'].lower()] = 1

                    if open_con['clients'].get(conn_con['raddr'][0]) is not None:
                        open_con['clients'][conn_con['raddr'][0]]['count'] += 1 
                        open_con['clients'][conn_con['raddr'][0]]['pid'].append(conn_con['pid'])
                        open_con['clients'][conn_con['raddr'][0]]['port'].append(conn_con['raddr'][1]) 
                    else:
                        open_con['clients'][conn_con['raddr'][0]] = {
                            'count': 1,
                            'pid': [conn_con['pid']],
                            'port': [conn_con['raddr'][1]],
                        }
                    
                    break  # since we got it its all good
        
        self.payload['open_conn'] = opened
        
        #self.stdout(self.payload['open_conn'])
        if len(self.payload) > 0:
            self.transmit_queue({self.metric_type_id['netstat']: json.dumps(self.payload).encode('zlib').encode('base64'), 'logTime': self.log_time, 'encoding': ['base64', 'gzip', 'json']})
