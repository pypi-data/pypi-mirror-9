import time
import sys
import os
import math
import asyncore
import json
import socket
import syslog


class Plugin(object):

    def __init__(self, *args, **kwargs):
        self.kwargs = dict()
        self.Agent = sys.modules['elastictrace.agent'].Agent
        #self.Agent_self = kwargs['agent_self']

    def __enter__(self):
        return self

    def loop(self, wait=True):
        while True:
            self.last_min = self.logTime()
            self.start    = time.time()
            self.observe()

            if 'name' not in self.kwargs:
                self.kwargs['name'] = "N/A"

            self.stdout(self.kwargs['name'] + ": " + str(time.time() - self.start))

            if(wait is True):  # sometimes plugins need to have werid timing
                self.wait()

    def observe(self):  # yes i come up with conrny naming
        raise NotImplementedError("Write a observe method check the docs")
    

    def transmit_now(self, payload):
        """
        For some unknown reasom someone is in a rush and wants there data sent now
        """
        self.Agent.transmit_now(payload)

    def transmit_queue(self, payload):
        """
        We are going to transmit the info but when we have a chance
        """
        payload['logTime'] = self.logTime()
        self.Agent.transmitQueue.push(json.dumps(payload))

    def get_metric_type_id(self, metric_name=None):
        if metric_name is not None:
            for dex, dat in self.kwargs['metrics_meta'].iteritems():
                if dat['metric_type'] == metric_name:
                    return dex
        else:
            return self.kwargs['metrics_meta']
            
    def get_metric_config(self, metric_type_ids=None):
        """
        For getting metric configs from the plugin
        """
        return self.Agent_self.get_metric_config(metric_type_ids)

    def logTime(self, rounded=False):
        if rounded is False:
            return math.floor(time.time() / 60)
        else:
            return math.round(math.floor(time.time() / 60), 0)

    def stdout(self, logLine):
        logLine = str(logLine)

        if self.Agent.options['debug'] is True:
            if self.Agent.options['syslog'] is True:
                syslog.syslog(str("elasticTrace > " + self.kwargs['name'] + " > " + logLine))

            else:
                print str(self.kwargs['name'] + ": " + logLine)

    def stderr(self, logLine):
        if 'name' not in self.kwargs:
            self.kwargs['name'] = 'N/A'

        if self.Agent.options['syslog'] is True:
            syslog.syslog(syslog.LOG_ERR, str("elasticTrace > " + self.kwargs['name'] + " > " + logLine))
        else:
            sys.stderr.write(self.kwargs['name'] + ": " + logLine + "\n")

    def wait(self, till=60, plus=0):
        if 'tname' in self.kwargs:
            self.Agent.nite_nite(name=self.kwargs['tname'])
        else:
            #print "bypass"
            time.sleep(till - (int(time.time()) % till) + plus)


class PluginAsyncServ(asyncore.dispatcher):

    def __init__(self, **kwargs):
        asyncore.dispatcher.__init__(self)
        self.kwargs = kwargs

        if kwargs['socket_family'] == 'unix':
            socket_family = socket.AF_UNIX

            if os.path.exists(kwargs['bind']) is False:
                open(kwargs['bind'], 'w')

        elif kwargs['socket_family'] == 'ipv4':
            socket_family = socket.AF_INET

        elif kwargs['socket_family'] == 'ipv6':
            socket_family = socket.AF_INET6

        if kwargs['socket_type'] == 'stream':
            socket_type = socket.SOCK_STREAM

        elif kwargs['socket_type'] == 'dgram':
            socket_type = socket.SOCK_DGRAM

        self.create_socket(socket_family, socket_type)
        if 'reuse' in kwargs and kwargs['reuse'] is True:
            if kwargs['socket_family'] == 'unix':
                try:
                    os.unlink(kwargs['bind'])

                except OSError:
                    if os.path.exists(kwargs['bind']):
                        raise
            else:
                self.set_reuse_addr()

        if 'listen' not in kwargs:
            kwargs['listen'] = 5

        self.bind(kwargs['bind'])
        self.listen(kwargs['listen'])

        if 'sock_chmod' in kwargs:
            os.chmod(kwargs['bind'], kwargs['sock_chmod'])

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            handler = getattr(getattr(__import__('plugin.' + self.kwargs['handler_file']), self.kwargs['handler_file']), self.kwargs['handler'])(sock)
        return False
