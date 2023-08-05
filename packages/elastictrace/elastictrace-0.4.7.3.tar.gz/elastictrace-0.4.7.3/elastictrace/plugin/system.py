import plugin
import os
import glob
import time
import hashlib
import json
import syslog
import psutil

import elastictrace.lib.linux_metrics as lm


class system(plugin.Plugin):

    def __init__(self, **kwargs):
        super(system, self).__init__(kwargs)
        self.kwargs         = kwargs
        self.config         = kwargs['config']
        self.metric_type_id = {'system': self.get_metric_type_id('system'), 'procs': self.get_metric_type_id('procs')}

        self.stdout(self.config)
        self.old = {  # keeps last pass values
            'cpu'         : dict(),
            'portListMD5' : "",
            'net' : dict(),
            'dev' : {
                'space' : dict(),
                'io'    : dict()
            },
            'proc' : {
                'io'     : dict(),
                'stat'   : dict(),
                'status' : dict(),
                'pids'   : list()
            },
            'misc': {
                'procs': dict(),
            }
        }

        #return self

    def procInfo(self, cpu_jiffies=0):
        if self.last_min % 1 == 0:

            # processes list
            self.payload['procList'] = dict()
            pid_list                 = list()
            pslist = os.popen("ps -eo pid,user,pcpu,pmem,rss,vsz,comm")
            #print pslist.read()
            

            for line in pslist.read().split("\n"):
                line = [x for x in line.split(' ') if x != '']
                
                if len(line) == 0:
                    break

                try:
                    pid, user, pcpu, pmem, rss, vsz, cmd = line[0], line[1], line[2], line[3], line[4], line[5], line[6]

                    if pid == 'PID':  # ignore this lets me skip having to do a tail or head on the call its self
                        continue
                        
                    try:
                        proc_psutil = psutil.Process(int(pid)).as_dict(['num_threads', 'threads', 'cwd', 'exe', 'name', 'username', 'uids', 'gids', 'terminal', 'status', 'memory_percent', 'nice', 'ionice', 'create_time', 'ppid', 'num_fds'])
                    except psutil.NoSuchProcess:
                        self.stderr("Pid(Status): {0} is gone for better or worse".format(pid))

                    if os.path.isfile('/proc/' + pid + '/status') is False:
                        
                        self.stderr("Pid(Status): {0} is gone for better or worse".format(pid))
                        continue

                    else:
                        status = lm.proc_stat.get_status(pid)
                        stat   = lm.proc_stat.get_stat(pid)

                        if (int(status['PPid']) <= 2 and os.getpid() != int(pid)) or os.path.isfile('/proc/' + pid + '/exe') is False:
                            continue

                    if os.path.isfile('/proc/' + pid + '/io') is False:
                        self.stderr("Pid(Status): {0} is gone for better or worse".format(pid))
                        continue

                    else:
                        io = lm.proc_stat.get_io(pid)

                    pid_list.append(int(pid))

                    statTemp = stat.copy()
                    cpu_times = {'utime' : 0, 'stime' : 0, 'cstime' : 0, 'cutime': 0}
                    falts     = {'min_flt': 0, 'maj_flt': 0, 'cmin_flt': 0, 'cmaj_flt': 0}

                    if pid in self.old['proc']['stat']:
                        if cpu_jiffies > 0:  # wanna avid any div 0
                            cpu_times['utime']  = (float(int(stat['utime'])  - self.old['proc']['stat'][pid]['utime'])  / float(cpu_jiffies))*100
                            cpu_times['stime']  = (float(int(stat['stime'])  - self.old['proc']['stat'][pid]['stime'])  / float(cpu_jiffies))*100
                            cpu_times['cstime'] = (float(int(stat['cstime']) - self.old['proc']['stat'][pid]['cstime']) / float(cpu_jiffies))*100
                            cpu_times['cutime'] = (float(int(stat['cutime']) - self.old['proc']['stat'][pid]['cutime']) / float(cpu_jiffies))*100
                            
                            if 'gtime' in self.old['proc']['stat']:
                                cpu_times['gtime'] = (float(int(stat['gtime'])  - self.old['proc']['stat'][pid]['gtime'])  / float(cpu_jiffies))*100
                                cpu_times['gtime'] = (float(int(stat['cgtime']) - self.old['proc']['stat'][pid]['cutime']) / float(cpu_jiffies))*100

                        falts['min_flt']  = int(stat['min_flt'])  - self.old['proc']['stat'][pid]['min_flt']
                        falts['maj_flt']  = int(stat['maj_flt'])  - self.old['proc']['stat'][pid]['maj_flt']
                        falts['cmin_flt'] = int(stat['cmin_flt']) - self.old['proc']['stat'][pid]['cmin_flt']
                        falts['cmaj_flt'] = int(stat['cmaj_flt']) - self.old['proc']['stat'][pid]['cmaj_flt']

                    self.old['proc']['stat'][pid] = {  # set the current values for old on next round
                        'utime'   : int(statTemp['utime']),
                        'stime'   : int(statTemp['stime']),
                        'cutime'  : int(statTemp['cutime']),
                        'cstime'  : int(statTemp['cstime']),
                        'min_flt' : int(statTemp['min_flt']),
                        'maj_flt' : int(statTemp['maj_flt']),
                        'cmin_flt': int(statTemp['cmin_flt']),
                        'cmaj_flt': int(statTemp['cmaj_flt'])
                    }
                    
                    if 'gtime' in statTemp:
                        self.old['proc']['stat'][pid]['gtime']  = int(statTemp['gtime'])
                        self.old['proc']['stat'][pid]['cgtime'] = int(statTemp['cgtime'])
                    
                    statusTmp   = status.copy()
                    ctx_switches = {'nonvoluntary': 0, 'voluntary': 0}
                    
                    if pid not in self.old['proc']['status']:
                        self.old['proc']['status'][pid] = {'voluntary_ctxt_switches': 0,  'nonvoluntary_ctxt_switches': 0}

                    if pid in self.old['proc']['status']:
                        ctx_switches['voluntary']    = int(status['voluntary_ctxt_switches'])    - self.old['proc']['status'][pid]['voluntary_ctxt_switches']
                        ctx_switches['nonvoluntary'] = int(status['nonvoluntary_ctxt_switches']) - self.old['proc']['status'][pid]['nonvoluntary_ctxt_switches']

                    self.old['proc']['status'][pid]['voluntary_ctxt_switches']    = int(statusTmp['voluntary_ctxt_switches'])
                    self.old['proc']['status'][pid]['nonvoluntary_ctxt_switches'] = int(statusTmp['nonvoluntary_ctxt_switches'])

                    if pid not in self.old['proc']['io']:
                        self.old['proc']['io'][pid] = io  # next time it wont be so easy

                    else:
                        for dex, dat in io.iteritems():
                            io[dex] -= self.old['proc']['io'][pid][dex]
                            self.old['proc']['io'][pid][dex] = dat

                    self.payload['procList'][pid] = dict()
                    self.payload['procList'][pid]['num_threads'] = proc_psutil.get('num_threads', 0)
                    self.payload['procList'][pid]['threads']     = proc_psutil.get('threads', [])
                    self.payload['procList'][pid]['cmd']         = cmd
                    self.payload['procList'][pid]['cwd']         = proc_psutil.get('cwd', '')
                    self.payload['procList'][pid]['exe']         = proc_psutil.get('exe', '')
                    self.payload['procList'][pid]['name']        = proc_psutil.get('name', '')
                    self.payload['procList'][pid]['user']        = proc_psutil.get('username', '')
                    self.payload['procList'][pid]['uids']        = proc_psutil.get('uids', [])
                    self.payload['procList'][pid]['gids']        = proc_psutil.get('gids', [])
                    self.payload['procList'][pid]['tty']         = proc_psutil.get('terminal', '')
                    self.payload['procList'][pid]['state']       = proc_psutil.get('status', '')
                    self.payload['procList'][pid]['pcpu']        = float(line[2])
                    self.payload['procList'][pid]['pmem']        = proc_psutil.get('memory_percent', 0.0)
                    self.payload['procList'][pid]['vsize']       = int(vsz)
                    self.payload['procList'][pid]['rss']         = int(rss)
                    self.payload['procList'][pid]['nice']        = proc_psutil.get('nice', 0)
                    self.payload['procList'][pid]['io_nice']     = proc_psutil.get('ionice', 0)
                    self.payload['procList'][pid]['uptime']      = proc_psutil.get('create_time', 0)
                    # self.payload['procList'][pid]['shr']       = self.payload['procList'][cmd]['shr']
                    self.payload['procList'][pid]['pid']         = int(pid)
                    self.payload['procList'][pid]['ppid']        = proc_psutil.get('ppid', 0)
                    self.payload['procList'][pid]['fd']          = proc_psutil.get('num_fds', 0)
                    self.payload['procList'][pid]['cmdline']     = lm.proc_stat.get_cmd(line[0])
                    self.payload['procList'][pid]['ctx_switch']  = ctx_switches
                    self.payload['procList'][pid]['cpu_times']   = cpu_times
                    self.payload['procList'][pid]['faults']      = falts
                    self.payload['procList'][pid]['io']          = io
                    # still gonna need to add a lot of other stuff

                except Exception, e:
                    self.stderr("ProcList errror: " + str(e))

                finally:
                    pass

            for old_pid in self.old['proc']['pids']:
                try:
                    pid_list.index(old_pid)

                except:  # i know werid i need the excpetion for this to work
                    if str(old_pid) in self.old['proc']['stat']:
                        del self.old['proc']['stat'][str(old_pid)]
                        self.stdout("procInfo: {0} remove stat history".format(str(old_pid)))

                    else:
                        self.stderr("procInfo: {0} remove stat history failed".format(str(old_pid)))

                    if str(old_pid) in self.old['proc']['status']:
                        del self.old['proc']['status'][str(old_pid)]
                        self.stdout("procInfo: {0} remove status history")

                    else:
                        self.stderr("procInfo: {0} remove status history failed".format(str(old_pid)))

                    if str(old_pid) in self.old['proc']['io']:
                        del self.old['proc']['io'][str(old_pid)]
                        self.stdout("procInfo: {0} remove io history".format(str(old_pid)))

                    else:
                        self.stderr("procInfo: {0} remove io history failed".format(str(old_pid)))

            self.old['proc']['pids'] = list(pid_list)
            self.stdout("procList      : " + str(time.time() - self.start))

    def netInfo(self):
        for key in lm.net_stat.get_interfaces():
            self.payload['sysMetrics']['net'][key] = dict()

        netAttr = ('rxBytes', 'rxPack', 'rxErr', 'rxDrop', 'rxMulti', 'txBytes', 'txPack', 'txErr', 'txDrop')
        for interface in self.config['interfaces']:  # loop network interfaces

            try:  # diff model so its easier to work with
                try:  # just in case the interface wants to be mean
                    netDump = lm.net_stat.rx_tx_dump(interface)
                except:
                    netDump = (0, 0, 0, 0, 0, 0, 0, 0, 0)

                netDump = (netDump[0][0], netDump[0][1], netDump[0][2], netDump[0][3], netDump[0][7]) + (netDump[1][0], netDump[1][1], netDump[1][2], netDump[1][3])
                now     = dict(zip(netAttr, [y - self.old['net'][str(interface)][x] for (x, y) in enumerate(netDump)]))

                self.payload['sysMetrics']['net'][str(interface)] = now.copy()
                self.old['net'][str(interface)] = list(netDump)

            except:  # non diff becuase we dont have anything to diff aganast
                self.old['net'][str(interface)] = list(netDump)
                self.payload['sysMetrics']['net'][str(interface)] = dict(zip(netAttr, (0, 0, 0, 0, 0, 0, 0, 0, 0)))

        # open ports
        self.payload['portList'] = {
            'tcp'  : dict(),
            'udp'  : dict(),
            'tcp6' : dict(),
            'udp6' : dict()
        }

        portsHash = hashlib.md5(os.popen("netstat -lptue --numeric-hosts --numeric-ports 2>&1 | tail -n +3").read()).hexdigest()

        try:
            if self.old['portListMD5'] != portsHash:  # check to see if the list has changed yet
                for line in os.popen("netstat -lptue --numeric-hosts --numeric-ports 2>&1 | tail -n +3"):
                    port = line.replace("LISTEN", "").split()
                    addr = port[3].split(":")  # get the addr into an array
                    self.payload['portList'][port[0]][addr[-1]] = dict(zip(('ip', 'user', 'pid', 'name'), list((":".join(addr[:-1]), port[5])) + port[7].split("/")))
                self.old['portListMD5'] = portsHash  # set it to this value
            else:
                del self.payload['portList']  # we dont need it to be sent
        except:
            self.old['portListMD5'] = ""  # set it to this value
            
            if 'portList' in self.payload:
                del self.payload['portList']  # we dont need it to be sent

    def devInfo(self):
        for key in lm.disk_stat.list_disks():
            self.payload['sysMetrics']['dev']['io'][key] = dict()

        for key in  list(lm.disk_stat.list_parts()):
            self.payload['sysMetrics']['dev']['size'][key] = dict()

        try:
            for disk in list(lm.disk_stat.list_parts()):  # loop the disks
                self.payload['sysMetrics']['dev']['size'][disk] = {'device' : '', 'used': 0, 'free': 0, 'mount': ''} # set default just incase
            
                diskSpace = list(lm.disk_stat.disk_usage(disk))
                self.payload['sysMetrics']['dev']['size'][disk] = dict(zip(('device', 'used', 'free', 'mount'), diskSpace[0:1] + diskSpace[2:4] + diskSpace[5:]))

                if diskSpace[0].startswith('/dev/disk/by-uuid/'):  # if mounted by uuid this will work great :)
                    self.payload['sysMetrics']['dev']['size'][disk]['device'] = os.path.realpath(diskSpace[0])

        except Exception, e:
            self.stderr("Disk size " + str(e))
        
        print self.payload['sysMetrics']['dev']['size']

        if len(lm.disk_stat.list_disks()) > 0:
            IOnow = lm.disk_stat.disk_stats()
            for disk in self.config['disks']:  # loop the disks
                if os.path.exists('/proc/diskstats') is True:  # patching for openvz and when systems dont allow reading that
                    # print disk
                    try:  # diff model so its easier to work with

                        diff = dict((k, int(IOnow[str(disk)][k]) - int(self.old['dev']['io'][str(disk)][k])) for k in IOnow[str(disk)] if k in self.old['dev']['io'][str(disk)])
                        self.payload['sysMetrics']['dev']['io'][str(disk)] = diff.copy()
                        self.old['dev']['io'][str(disk)] = IOnow[str(disk)].copy()

                    except Exception, e:  # non diff becuase we dont have anything to diff aganast
                        self.stderr('IO Stats: ' + str(e))

                        self.old['dev']['io'][str(disk)] = IOnow[str(disk)].copy()
                        self.payload['sysMetrics']['dev']['io'][str(disk)] = dict((k, 0) for k in IOnow[str(disk)])
                else:
                    self.stderr("/proc/diskstats does not exist, there wont be IO metrics")
                    self.payload['sysMetrics']['dev']['io'][str(disk)] = {'numReads' : 0, 'numWrites' : 0, 'secReads' : 0, 'secWrites' : 0, 'wmsIO': 0, 'msIO': 0, 'msReads': 0, 'msWrites': 0, 'mergeReads': 0, 'mergeWrites': 0, 'currIo': 0}
                    
        else:
            self.stderr("/proc/partitions does not exist, there wont be IO metrics")
            self.payload['sysMetrics']['dev']['io']['/'] = {'numReads' : 0, 'numWrites' : 0, 'secReads' : 0, 'secWrites' : 0, 'wmsIO': 0, 'msIO': 0, 'msReads': 0, 'msWrites': 0, 'mergeReads': 0, 'mergeWrites': 0, 'currIo': 0}

    def getUptime(self):
        if os.path.exists('/proc/uptime') is True:
            with open('/proc/uptime', 'r') as f:
                return float(f.readline().split()[0])
        return None

    def observe(self):
        # get system stats
        self.payload = {  # start the var with nothing in it
            'sysMetrics': {
                'cpu'  : dict(),
                'mem'  : dict(),
                'misc' : {
                    'procs': dict(),
                },
                'net'  : dict(),
                'dev': {
                    'io'   : dict(),
                    'size' : dict()
                }
            },
            'portList' : dict()
        }

        cpuTimes, devices = dict(), dict()
        self.log_time = self.logTime()

        self.devInfo()
        self.netInfo()
        
        try:
            proc_sum = lm.cpu_stat.proc_sum() #get value from system
            self.payload['sysMetrics']['misc']['procs'] = {
                'max': lm.cpu_stat.proc_max(),
                'count': proc_sum - self.old['misc']['procs'].get('count', 0) #get value will blast if not exist wanted effect for on boot. will be bad if module crashes.
            }
            self.old['misc']['procs']['count'] = proc_sum #update the old value
        except:
            self.stderr("Issue getting process count")

        # get cpu times
        try:
            cpuTimes['new'], cpuTimes['math'] = lm.cpu_stat.cpu_times(), list()  # get the current cpu times
            cpuTimes['sum'] = sum(cpuTimes['new']) - sum(self.old['cpu'])  # sum up the total amount of times

            for dex, dat in enumerate(cpuTimes['new']):  # loop for differ and then get perantage in one loop
                cpuTimes['math'].insert(dex, (float(cpuTimes['new'][dex] - self.old['cpu'][dex]) / cpuTimes['sum']) * 100)

            self.payload['sysMetrics']['cpu']['times'] = dict(zip(('user', 'nice', 'system', 'idle', 'iowait', 'irq', 'softirq', 'steal', 'guest'), cpuTimes['math']))

        except Exception, e:
                self.stderr("System Cpu: " + str(e))

        self.old['cpu'] = list(cpuTimes['new'])  # use a copy save us the pain
        self.payload['sysMetrics']['cpu']['loadAvg']       = lm.cpu_stat.load_avg()
        self.payload['sysMetrics']['misc']['fileDesc']     = lm.cpu_stat.file_desc()      # file descripters
        self.payload['sysMetrics']['misc']['procsBlocked'] = lm.cpu_stat.procs_blocked()  # blocked prcesses proces
        self.payload['sysMetrics']['misc']['threads']       = {
            'count': lm.cpu_stat.thread_count(),  # returns number of threads
            'max'  : lm.cpu_stat.thread_max(),    # returns max number of threads
        }
        self.payload['sysMetrics']['misc']['procsRunning'] = lm.cpu_stat.procs_running()  # running processes
        self.payload['sysMetrics']['misc']['uptime']       = self.getUptime()             # get the amount of time the system has been online
        self.payload['sysMetrics']['mem']                  = lm.mem_stat.mem_info()       # mem usage
        
        # print self.payload['sysMetrics']['dev']['io']
        """
        print json.dumps(self.payload['sysMetrics']).encode('zlib').encode('base64').decode('base64').decode('zlib')
        print json.dumps(self.payload['sysMetrics']).encode('zlib').encode('base64')
        print json.dumps(self.payload['procList']).encode('zlib').encode('base64')
        exit()
        """
        self.procInfo(cpu_jiffies=cpuTimes['sum'])  # takes place late because we need some cpu times
        self.transmit_queue({self.metric_type_id['system']: json.dumps(self.payload['sysMetrics']).encode('zlib').encode('base64'), 'logTime': self.log_time, 'encoding': ['base64', 'gzip', 'json']})
        self.transmit_queue({self.metric_type_id['procs']: json.dumps(self.payload['procList']).encode('zlib').encode('base64'), 'logTime': self.log_time, 'encoding': ['base64', 'gzip', 'json', 'array']})

        #self.stdout(self.payload)
