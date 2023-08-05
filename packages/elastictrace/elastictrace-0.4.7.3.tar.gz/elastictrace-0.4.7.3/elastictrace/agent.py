#!/usr/bin/python
import math
import random
import time
import sys
import os
import platform
import urllib2
import urllib
import socket
import asyncore
import collections
import signal
import threading
import ConfigParser
import json
import glob
import syslog
import select
import shutil
import subprocess
from datetime import datetime

import requests
#import queuelib
# import inspect

# add libs
import elastictrace.lib.linux_metrics as lm
import elastictrace.lib.queuelib.queue as queuelib

#plugins
import elastictrace.plugin.system
import elastictrace.plugin.ping
import elastictrace.plugin.netstat
import elastictrace.plugin.rethinkdb

# add plugins
# import plugin


class Agent:
    options = dict()

    def __init__(self, args, version, **kwargs):
        # base vars
        self.history        = {'filename' : '', 'last_min' : 0}
        self.logs           = dict()
        self.dataSet        = dict()
        self.regex          = dict()
        Agent.threadCheckin = dict()
        self.thread_meta    = dict()
        self.plugins        = dict()
        Agent.session        = {'metrics': {'system' : dict()}}
        self.threads        = {'tailLogs' : "", 'transmit' : dict()}
        self.api            = 'api.'
        self.edge           = 'edge.'
        self.http_proto     = 'https'
        self.http_hostname  = 'elastictrace.com'
        self.pidFile        = '/var/run/elastictrace.pid'
        self.runDir         = '/var/run/elastictrace/'
        self.dataDir        = '/var/lib/elastictrace'
        self.agentVersion   = version
        self.agentFD        = None
        self.config         = dict()
        Agent.transmit_failure = 0
        Agent.options       = args
        Agent.transmitQueue = queuelib.FifoMemoryQueue()
        Agent.transmitDiskQueue = queuelib.FifoDiskQueue("{0}/agentTransmitQueue".format(self.dataDir), syncAll=True)
        
        Agent.var = {
            'transmit_failure': {
                'backoff_time': 60,
                'backoff_count': 20,
            }
        }

        if args is not None:
            self.cmdArgs = args

        # functions
        if self.lockFile_action(True) is True:
            self.readAgentConfig()
            self.agentLogin()
            if self.cmdArgs['fork'] is True:  # if we are ment to fork fork

                self.lockFile_action(False)  # remove the lock file with this pid
                fork = os.fork()
                if fork != 0:  # kill the parent
                    exit()

                else:
                    sys.stderr.write("Forking as: " + str(os.getpid()) + "\n")
                    if self.lockFile_action(True) is False:   # remake the lock file for this pid
                        sys.stderr.write("Could not get lock file " + self.pidFile + "\n")
                        sys.exit()

            self.run()
        else:  # cant get the lock file
            sys.stderr.write("Could not get lock file " + self.pidFile  + "\n")

    def lockFile_action(self, action):
        if action is True:  # lets make the lock file
            if os.path.exists(self.pidFile) is False:
                if not os.path.exists(self.runDir):
                    os.makedirs(self.runDir)

                self.lockFile = open(self.pidFile, "w+")
                self.lockFile.write(str(os.getpid()))
                self.lockFile.flush()  # flush it
                return True
            else:
                self.lockFile = open(self.pidFile, "r+")
                pid = self.lockFile.read()
                try:
                    if os.kill(int(pid), 0) is True:
                        return False
                except:
                    os.unlink(self.pidFile)
                    return self.lockFile_action(action)

        else:  # lets kill the lock file
            return os.unlink(self.pidFile)

    def readAgentConfig(self):

        try:
            self.agentConfig = ConfigParser.RawConfigParser()
            self.agentConfig.read(self.cmdArgs['config_file'])

        except IOError as e:
            stderr(str(e))
            stderr("This may be okay if the file has not been made yet")
            # self.agentConfig = {}

        except Exception, e:
            stderr(str(e))
            exit()

        if self.agentConfig.has_section('agent') is False:  # handle the case if we dont have the default section
            self.agentConfig.add_section('agent')

        # time to override args from whats in the file
        if self.cmdArgs['api_key'] is not None:
            self.agentConfig.set('agent', 'api_key', self.cmdArgs['api_key'])

        if self.cmdArgs['api_secret'] is not None:
            self.agentConfig.set('agent', 'api_secret', self.cmdArgs['api_secret'])

        if self.cmdArgs['platform_id'] is not None:
            self.agentConfig.set('agent', 'platform_id', self.cmdArgs['platform_id'])

        if self.cmdArgs['nodeId'] is not None:
            self.agentConfig.set('agent', 'node_id', self.cmdArgs['nodeId'])

        # throw some errors if we still dont have some of the things we need to run
        if 'platform_id' not in self.agentConfig._sections['agent']:
            stderr("Misisng an platform_id")
            exit()

        if 'api_key' not in self.agentConfig._sections['agent']:
            stderr("Misisng an API key")
            exit()

        if 'api_secret' not in self.agentConfig._sections['agent']:
            stderr("Misisng an API secret")
            exit()

        self.agentConfig.set('agent', 'hostname'  , socket.gethostname())
        self.agentConfig.set('agent', 'interfaces', lm.net_stat.get_interfaces())
        self.agentConfig.set('agent', 'disks'     , lm.disk_stat.list_disks())
        self.agentConfig.set('agent', 'disk_parts', list(lm.disk_stat.list_parts()))
        # need to add a checks to make sure the values work and connect to the things they say they should

    def writeAgentConfig(self):
        try:
            self.agentFD.seek(0)
        except:
            if not os.path.exists("/etc/elastictrace"): #check for a folder
                os.makedirs("/etc/elastictrace")  # create the missing folder
            
            if os.path.isfile(self.cmdArgs['config_file']) is False:
                self.agentFD = open(self.cmdArgs['config_file'], "w+") #open the file for reading and writing
            else:
                self.agentFD = open(self.cmdArgs['config_file'], "r+") #open the file for reading and writing
        
        self.agentConfig.write(self.agentFD) #write to the file discriptor
        self.agentFD.flush()
        os.fsync(self.agentFD.fileno())
        self.agentFD.close()

    def get_last_min(self, rounded=False):
        if rounded is False:
            return math.floor(time.time() / 60)
        else:
            return math.round(math.floor(time.time() / 60), 0)
    
    def niteNite(self, till=60, plus=0, name=None):
        if name is not None:
            Agent.threadCheckin[name] = time.time()
            
        if till == 0:
            till = 60

        time.sleep(till - (int(time.time()) % till) + plus)
        
    @staticmethod
    def nite_nite(till=60, plus=0, name=None):
        if name is not None:
            Agent.threadCheckin[name] = time.time()

        if till == 0:
            till = 60
        
        time.sleep(till - (int(time.time()) % till) + plus)

    def makeThread(self, name, method, args=None, daemon=True, restart=False):
        
        if name in self.threads and self.threads[name].is_alive() == True: #check if thread is still runing
            self.threads[name]._Thread__stop() #stop the running thread
        
        if args is None:
            self.threads[name] = threading.Thread(target=method)  # start the
        else:
            self.threads[name] = threading.Thread(target=method, args=args)  # start the

        if daemon is True:
            self.threads[name].daemon = True  # set daemon mode
            
        if restart is True:
            Agent.threadCheckin[name] = time.time()
            
        
        self.thread_meta[name]    = {'name': name, 'method': method, 'args': args, 'restart': restart}
        self.threads[name].start()  # start threads
        return True

    def run(self):
        self.config = config2dict(self.agentConfig)
        #Agent.transmitQueue = queuelib.FifoDiskQueue("{0}/agentTransmitQueue".format(self.dataDir), syncAll=True)

        self.config['plugin.system']    = { "name" : "system", 'disks': self.config['agent']['disks'], 'disk_parts': self.config['agent']['disk_parts'], 'interfaces': self.config['agent']['interfaces'], "agent_self": self }
        
        for dex,dat in Agent.session['metrics'].iteritems():
            if dex != 'system' and dat[dat.keys()[0]]['metric_type_status'] == 'A':
                self.config['plugin.'+dex] = {"name": dex}
                
        self.plugins = dict()

        # if self.config.has_key('plugins') is True: # we are going to load the plugins
        for dex in self.config.keys():
            if dex.startswith('plugin.') is False:
                continue

            dex = dex.replace('plugin.', '')
            import_str = 'elastictrace.plugin.'+dex
            self.plugins[dex] = sys.modules[import_str]
            self.plugins[dex] = getattr(self.plugins[dex], dex)(agent_self=self, name=dex, tname=("plugin_"+dex), config=self.config['plugin.' + dex], metrics_meta=Agent.session['metrics'][dex])
            self.makeThread('plugin_' + dex, self.plugins[dex].loop, daemon=True, restart=True)

        self.makeThread('transmit_queue', self.transmit_queue, daemon=True, restart=True)  # transmit queue as its own thread running
        self.makeThread('asyncore_loop', asyncore.loop, daemon=True)         # transmit queue as its own thread running

        while True:
            stdout("Main Sleeping for: " + str(60 - (int(time.time()) % 60)))
            time.sleep(60 - (int(time.time()) % 60))
            self.threadManager()

    def threadManager(self):
        curr_time = time.time()  # store time for a bit
        for dex, dat in Agent.threadCheckin.iteritems():
            if (dat is not None and curr_time - dat >= 300):  # lets restart the thread
                stderr("restarting thread: " + dex)
                meta = self.thread_meta[dex]
                stdout(meta)
                self.makeThread(dex, method=meta['method'], daemon=True, restart=meta['restart'])

    def agentLoginReq(self, payload):
        try:
            ip_mode = self.agentConfig.get('agent', 'ip_mode')
        except:
            ip_mode = None
        
        connects = self.get_http_connect(self.api+self.http_hostname, proto=self.http_proto, ip_mode=ip_mode)

        req_headers = {
            'User-Agent'      : self.makeUserAgent(),
            'et_id'           : self.agentConfig.get('agent', 'platform_id'),
            'X_AUTH_API_KEY'  : self.agentConfig.get('agent', 'api_key'),
            'X_AUTH_SECRET'   : self.agentConfig.get('agent', 'api_secret'),
            'Content-Type'    : 'application/json',
            'agent_version'   : self.agentVersion,
            'Content-Encoding': 'urlencode',
            'Host'            : connects['host']
        }
        
        if 'node_id' in self.agentConfig._sections['agent']:
            req_headers['node_id'] = self.agentConfig.get('agent', 'node_id')
        
        try:
            req = requests.post(connects['url']+'api/v1/node/login', data=payload, headers=req_headers, verify=connects['verify'])
            stdout("response: "+req.text)
            stdout("Response code: "+str(req.status_code))
            if req.status_code > 399:
                stderr("Invaild Login response code: "+str(req.status_code))
            else:
                return req.json()
                
        except requests.exceptions.ConnectionError:
            stderr("Issue connecting to: "+self.http_proto+'://' + self.api + self.http_hostname)
            
        except (requests.exceptions.HTTPError, requests.exceptions.Timeout, requests.exceptions.TooManyRedirects), e:
            stderr("Unexpected Login Request Error")
            stdout(payload)
        
        except:
            stderr("Unexpected Login Error")
            stdout(payload)
        exit()


    def agentLoginSpecs(self):
        loginPayload = {
            'hostname'     : self.agentConfig.get('agent', 'hostname'),
            'platform_id'  : self.agentConfig.get('agent', 'platform_id'),
            'agent_time'   : time.time(),
            'spec'         : {
                'version'  : os.popen("cat /proc/version").read(),
                'meminfo'  : float(os.popen('cat /proc/meminfo').read().split("\n")[0].split(" ")[-2]),
                'cpuInfo'  : dict(),
                'release'  : dict(),
                'uname'    : dict(),
            }
        }
        
        try:
            uname = os.uname()
            loginPayload['spec']['uname'].update(kernel=uname[2], version=uname[3], sysname=uname[0], machine=uname[4])
        except:
            pass

        try:  # try to give the node id
            loginPayload['node_id'] = self.agentConfig.get('agent', 'node_id')

        except:  # if we dont have one dont worry about it
            loginPayload['node_id'] = None

        lscpu = subprocess.Popen("lscpu", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        
        if lscpu.stderr is not None:
            stdout(lscpu.stderr.read()) ## throw this out if there is something
        
        for line in lscpu.stdout:
            line = line.strip("\n").split(':')
            try:
                val = line[1].strip().replace(',', '-')
                loginPayload['spec']['cpuInfo'][line[0].strip().lower().replace(' ', '_')] = float(val) if val.isdigit() else val
            except:
                pass
        
        release = glob.glob("/etc/*-release")
        if len(release) > 0:
            with open(release[0]) as line:
                for x in line.readlines():
                    x = x.strip("\n").split('=')

                    if len(x) == 2:
                        val = x[1].strip('"')
                        loginPayload['spec']['release'][x[0].lower().strip("()")] = float(val) if val.isdigit() else val

        return loginPayload

    def agentLogin(self):
        loginPayload = self.agentLoginSpecs()
        global options

        try:
            req = ""
            stdout(loginPayload)
            req = self.agentLoginReq(json.dumps(loginPayload))
        except Exception as e:
            stdout(str(e))
            stdout(req)
            stderr("Failed to encode login data")
            exit()

        try:
            req = dictConvert(req)  # decode
        except Exception as e:
            stdout(str(e))
            stderr("Failed to decode login data")
            exit()
            
        if 'time_diff' in req and abs(req['time_diff']) > 300:
            stderr('Your clock time is different from ours by {0} seconds please check your system clock if you think this has been reached in error please contact support'.format(req['time_diff']))
            exit()

        if 'session_id' in req:
            self.agentConfig.set('agent', 'session_id', req['session_id'])
            self.loadSession(req)
        else:
            stderr("Could not get session id")
            exit()

        if 'node_id' in req:
            if 'node_id' not in self.agentConfig._sections['agent'] or req['node_id'] != self.agentConfig.get('agent', 'node_id'):  # add the nodeId
                self.agentConfig.set('agent', 'node_id', req['node_id'])
        else:
            stderr('No nodeId was returned')
            exit()
        
        self.writeAgentConfig()

        if 'install' in options and options['install'] is True:
            print "Thank you for installing elasticTrace. \nHappy Tracing!!!"
            exit()

    def loadSession(self, data):

        if 'session' in data and 'metrics' in data['session']:  # orgnize the metrics that we have access to
            for dex, dat in data['session']['metrics'].iteritems():

                if dat['metric_type'] == 'procs':  # set procs under system
                    Agent.session['metrics']['system'][dex] = dat
                    continue

                if dat['metric_type'] not in Agent.session['metrics']:  # create a dict in case we have many
                    Agent.session['metrics'][dat['metric_type']] = dict() # need a test that if metric type is here but not in config add it to config

                dat['metrics_type_id']                           = dex
                Agent.session['metrics'][dat['metric_type']][dex] = dat

        if 'session' in data and 'config' in data['session']:  # need to take care if the cnfig
            Agent.session['config'] = data['session']['config']
            
        return None
            
    def makeUserAgent(self):  # make a user agenet string.
        version = sys.version_info  # get system info
        uname   = platform.uname()  # get the linux kernel info
        try:
            node_id = self.agentConfig.get('agent', 'node_id')
        except:
            node_id = ""
        return node_id+"/" + self.agentVersion + " (" + uname[0] + "; " + uname[1] + "; " + uname[2] + "; " + uname[4] + ") Python/" + str(version[0]) + "." + str(version[1]) + "." + str(version[2])

    """
    This just keeps a list of what still needs to be transmited to the beacon
    """
    def transmit_queue(self):
        
        #if Agent.transmitQueue is not None:
        #gent.transmitQueue.close()
        #Agent.transmitQueue = queuelib.FifoDiskQueue("{0}/agentTransmitQueue".format(self.dataDir), syncAll=True)
        
        while True:
            
            if len(Agent.transmitQueue) > 0:
                for x in range(len(Agent.transmitQueue)):
                    Agent.transmitDiskQueue.push(Agent.transmitQueue.pop())
            
            if Agent.transmit_failure > Agent.var['transmit_failure']['backoff_count']:
                time.sleep(Agent.var['transmit_failure']['backoff_time'])
            
            if len(Agent.transmitDiskQueue) > 0:
                stderr("Items in queue: " + str(len(Agent.transmitDiskQueue)))  # turning htis on by default because i wanna see this number more
            """
            else:
                #stdout("Items in queue: " + str(len(Agent.transmitQueue)))  # turning htis on by default because i wanna see this number more
            """
            if len(Agent.transmitDiskQueue) is 0:  # lets wait for a while
                time.sleep(5)
            else:
                queue_pop = Agent.transmitDiskQueue.pop()
                if queue_pop is None:
                    stderr("Skipping: TransmitQueue Value is type: {0}".format(type(queue_pop)))
                    time.sleep(random.randint(5, 20))
                else:
                    try:
                        
                        stack = json.loads(queue_pop)
                        self.transmit_now(stack)
                    except:
                        stderr("Failed to Transmit or Decode data from queue")
                        stdout(queue_pop)
                        pass

                if len(Agent.transmitDiskQueue) > 0:
                    sleepit = random.randint(1, (abs(60-datetime.now().second)/len(Agent.transmitDiskQueue))+2)
                    #stdout("sleeping for: " + str(sleepit))
                    self.niteNite(till=sleepit, plus=0, name='transmit_queue')
                else:
                    time.sleep(random.randint(5, 20))


    def transmit_now(self, payload):
        start = time.time()
        raw   = payload.copy()  #just in case we need it raw
        
        if 'logTime' not in payload:
            payload['logTime'] = self.get_last_min()

        if 'encoding' not in payload:  # we dont want the other end to reverse anything
            payload['encoding'] = [None]
            
        payload['meta'] = {
            'rez'         : 1,
            'logTime'     : payload['logTime'],
            'encoding'    : payload['encoding'],
            'node_id'     : self.config['agent']['node_id'],
            'hostname'    : self.config['agent']['hostname'],
            'platform_id' : self.config['agent']['platform_id'],
        }
        
        del payload['logTime'], payload['encoding']  # remove the log time from the payload since its in meta
        
        connects = self.get_http_connect(self.edge+self.http_hostname, proto=self.http_proto, ip_mode=None)
        req_headers = {
            'User-Agent'       : self.makeUserAgent(),
            'X_AUTH_NODE_ID'   : self.config['agent']['node_id'],
            'X_AUTH_SESSION'   : self.config['agent']['session_id'],
            'agent_version'    : self.agentVersion,
            'Content-Type'     : 'application/json',
            'Content-Encoding' : 'urlencode',
            'Host'             : connects['host']
        }
        
        try:
            payload = json.dumps(payload)
            req     = requests.put(connects['url']+'edge/v1/metrics/add', data=urllib.quote(payload), headers=req_headers, verify=connects['verify'])
            #stdout("response: "+req.text)
            stdout("Response code: "+str(req.status_code))
            
            if req.status_code == 401:
                stderr("Got a 401 time to shutdown")
                shutdown(True)
            
            elif req.status_code > 399:
                stderr("Invaild transmit response code: "+str(req.status_code))
            
            else:
                self.loadSession(req.json())
                stdout("Transmit Queue Send:  " + str(time.time() - start))
                stdout("Queue Bytes Sent:     " + str(len(payload)))
                stdout("logtTime:             " + str(raw['logTime']))
                stdout("metric_type_ids:      " + str([x for x in raw.keys() if x not in ['meta', 'logTime', 'encoding'] ]))
                stdout("Queue Ids:            " + str(req.json()['metrics']['job_ids']))
                stdout('"' + req.text + '"')
                Agent.transmit_failure = 0
                return True
                
        except requests.exceptions.ConnectionError:
            Agent.transmit_failure += 1
            stderr("Issue connecting to: "+self.http_proto+'://' + self.edge + self.http_hostname)
            
        except (requests.exceptions.HTTPError, requests.exceptions.Timeout, requests.exceptions.TooManyRedirects), e:
            Agent.transmit_failure += 1
            stderr("HTTP Error in transmiting")
            stdout(payload)
        """
        except:
            stderr("Error in transmiting")
            stdout(payload)
        """
        # if we made it down here lets re-queue
        self.transmitDiskQueue.push(json.dumps(raw))
        return False
    
    def get_metric_config(self, metric_type_ids=None):

        connects    = self.get_http_connect(self.edge+self.http_hostname, proto=self.http_proto, ip_mode=None)
        
        req_headers = {
            'User-Agent'       : self.makeUserAgent(),
            'X_AUTH_NODE_ID'   : self.config['agent']['node_id'],
            'X_AUTH_SESSION'   : self.config['agent']['session_id'],
            'agent_version'    : self.agentVersion,
            'Content-Type'     : 'application/json',
            'Content-Encoding' : 'urlencode',
            'Host'             : connects['host']
        }
        
        payload = {
            'metrics_type_id' : metric_type_ids
        }
        
        req = requests.post(connects['url']+'edge/v1/metrics/get/config', data=urllib.quote(json.dumps(payload)), headers=req_headers, verify=connects['verify'])
        stdout("Response code: "+str(req.status_code))
        
        if req.status_code < 399:
            try:
                return req.json()
            except:
                stderr("get_metrics_config: failed! "+json.dumps(payload))
                return False
                
        return False
        
    def get_http_connect(self, host, proto='https', ip_mode=None):
        final_host = host
        verify = True
        if ip_mode is not None or 'ip_mode' in self.config.get('agent', {}):
            addrs  = socket.getaddrinfo(host, 80)
            verify = False 
            
            if ('ip_mode' in self.config.get('agent', {}) and self.config['agent']['ip_mode'] == "ipv6") or ip_mode == "ipv6":
                host = random.choice([addr[4][0] for addr in addrs if addr[0] == socket.AF_INET6])
            else:
                host = random.choice([addr[4][0] for addr in addrs if addr[0] == socket.AF_INET])
            
        return {'host': final_host, 'url': "{0}://{1}/".format(proto, host), 'verify': verify}


def stdout(logLine):
    """
    Some defult functions that help make the world go round
    """
    global options

    if options['debug'] is True:
        if options['syslog'] is True:
            syslog.syslog(str("elasticTrace: " + logLine))
        else:
            print str(logLine)


def stderr(logLine):
    global options

    if options['syslog'] is True:
        syslog.syslog(syslog.LOG_ERR, str("elasticTrace: " + logLine))
    else:
        sys.stderr.write(logLine + "\n")


def signal_handler(signal, frame):
    shutdown(True)

def lockfile_exists():
    if os.path.isfile("/var/run/elastictrace.pid") is True:
        return True
        
    return False

def shutdown(me):
    if me is True:  # shutting my self down
        stderr("Shutting process down")
        
        try:
            Agent.transmitQueue.close()
        except:
            stderr("Issue closing Transmit Queue")
            pass
        
        try:
            os.unlink("/var/run/elastictrace.pid")
            stderr("Deleted lock file")
        except:
            stderr("Issue deleting /var/run/elastictrace.pid")
        sys.exit(0)
    else:  # shutdown another instance
        try:
            pid = open("/var/run/elastictrace.pid").read()
            os.kill(int(pid), 2)
            return True
        except:
            sys.stderr.write("Was unable to shutdown other processes: " + str(pid))
            return False

def install_agent():
    crontab_path = '/etc/crontab'
    cronD_path   = '/etc/cron.d' 
    rclocal_path = '/etc/rc.local'
    data_path    = '/var/lib/elastictrace'
    et_cron_path = '/etc/cron.d/elastictrace-agent'
    reboot_line  = '@reboot root /opt/elastictrace-env/bin/elastictrace-agent --fork --syslog\n'
    rc_line      = '/opt/elastictrace-env/bin/elastictrace-agent --fork --syslog\n'
    
    if os.path.isdir(cronD_path) is True and os.path.isfile(et_cron_path) is False:
        print "Installing reboot line into: {0}".format(et_cron_path)
        f = open(et_cron_path, 'w+')
        f.write(reboot_line)
        f.close()

    elif os.path.isdir(cronD_path) is False and os.path.isfile(rclocal_path) is True:
        if rc_line not in open(rclocal_path).read():
            print "Install reboot line into: {0}".format(rclocal_path)
            f = open(rclocal_path, 'a')
            f.write(rc_line)
            f.close()
        
    if os.path.islink('/usr/local/sbin/elastictrace-agent') is False:
        print "Creating Symlink between {0} <---> {1}".format('/opt/elastictrace-agent/elastictrace', '/usr/local/sbin/elastictrace-agent')
        try:
            os.symlink('/opt/elastictrace-agent/elastictrace', '/usr/local/sbin/elastictrace-agent')
        except:
            stderr("Failed to create symlink")
        
    if not os.path.exists(data_path):
        os.makedirs(data_path)

def uninstall_agent():
    crontab_path = '/etc/crontab'
    cronD_path   = '/etc/cron.d'
    data_path    = '/var/lib/elastictrace' 
    rclocal_path = '/etc/rc.local'
    et_cron_path = '/etc/cron.d/elastictrace-agent'
    rc_line      = '/opt/elastictrace-env/bin/elastictrace-agent --fork --syslog\n'
    
    shutdown(False) #shutdown any other running process
    
    if os.path.isdir("/etc/elastictrace") is True:
        shutil.rmtree("/etc/elastictrace")
        print "Removing config files"
    
    if os.path.isfile(et_cron_path) is True:
        os.remove(et_cron_path)
        print "Remove "+et_cron_path
    
    elif os.path.isdir(cronD_path) is False and os.path.isfile(rclocal_path) is True:
        if rc_line  in open(rclocal_path).read():
            print "Remove line from /etc/rc.local"
            
    if os.path.islink('/usr/local/sbin/elastictrace-agent') is True:
        os.unlink('/usr/local/sbin/elastictrace-agent')
        print "Remove execution link"
        
    if not os.path.exists(data_path):
        shutil.rmtree(data_path)
        
    print "Will now remove /opt/elastictrace-agent"
    shutil.rmtree("/opt/elastictrace-agent")
    
    return True

def dictConvert(data):
    """Recursively converts dictionary keys to strings."""
    if not isinstance(data, dict):
        return data
    return dict((str(k), dictConvert(v)) for k, v in data.items())


def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv


def config2dict(data):
    d = dict(data._sections)
    for k in d:
        d[k] = dict(data._defaults, **d[k])
        d[k].pop('__name__', None)
    return d


def my_range(start, end, step):
    while start <= end:
        yield start
        start += step
        
def logTime(rounded=False):
        if rounded is False:
            return math.floor(time.time() / 60)
        else:
            return math.round(math.floor(time.time() / 60), 0)
        
def agent_version():
    return "0.4.7.3"

def main():
    global options
    
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]", version="%prog "+agent_version())
    parser.add_option("--pltid",     dest="platform_id", help="The platform id of the accout")
    parser.add_option("--apikey",    dest="api_key",     help="The api key of the accout")
    parser.add_option("--apisec",    dest="api_secret",  help="The api secret of the accout")
    parser.add_option("--node-id",   dest="nodeId",      help="Give this machine an exisitng nodeId")
    parser.add_option("--config",    dest="config_file", default="/etc/elastictrace/agent.conf", help="Path to your config file (default: /etc/elastictrace/config.json)")
    parser.add_option("--fork",      dest="fork",        action="store_true", default=False,     help="Fork the tracing program")
    parser.add_option("--debug",     dest="debug",       action="store_true", default=False,     help="debug the application")
    parser.add_option("--syslog",    dest="syslog",      action="store_true", default=False,     help="output the logs to syslog")
    parser.add_option("--shutdown",  dest="shutdown",    action="store_true", default=False,     help="find the current running instance and kill it")
    parser.add_option("--restart",   dest="restart",     action="store_true", default=False,     help="restarts elastictrace")
    parser.add_option("--install",   dest="install",     action="store_true", default=False,     help="install the agent and set permissions")
    parser.add_option("--uninstall", dest="uninstall",   action="store_true", default=False,     help="uninstall agent")

    (options, args) = parser.parse_args()
    options = options.__dict__

    signal.signal(signal.SIGINT, signal_handler)   # shut down handler
    signal.signal(signal.SIGTERM, signal_handler)  # shut down handler

    if options['shutdown'] is True or options['restart'] is True:
        killjoy = shutdown(False)  # shutdown another processes
        if options['shutdown'] is True:
            sys.exit()
        elif killjoy is True and lockfile_exists() is True:
            sys.stderr.write("Giving other threads 60 seconds to shutdown")
            time.sleep(60)
        else:
            sys.exit()
            
    if options['uninstall'] is True:
        print "Would you like to remove elasticTrace from this server (y/n)?"
        i, o, e = select.select( [sys.stdin], [], [], 10 )
        response = sys.stdin.readline().strip().lower()
        
        if i and response == "y":
            uninstall_agent()
        elif i and response == "n":
            print "Exiting"
        else:
            print "You did not answer within 10 seconds and aporting uninstall."
            
        sys.exit()

    if options['install'] is True:
        install_agent()

    if options['syslog'] is True:
        import syslog

    d = Agent(options, parser.get_version())

if __name__ == '__main__':
    main()
