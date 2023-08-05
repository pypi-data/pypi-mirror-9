#!/usr/bin/env python
#
#  Copyright (c) 2010-2012 Corey Goldberg (http://goldb.org)
#
#  This file is part of linux-metrics
#
#  License :: OSI Approved :: MIT License:
#      http://www.opensource.org/licenses/mit-license
#
#      Permission is hereby granted, free of charge, to any person obtaining a copy
#      of this software and associated documentation files (the "Software"), to deal
#      in the Software without restriction, including without limitation the rights
#      to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#      copies of the Software, and to permit persons to whom the Software is
#      furnished to do so, subject to the following conditions:
#
#      The above copyright notice and this permission notice shall be included in
#      all copies or substantial portions of the Software.
#


"""
    proc_stat - Python Module for CPU Stats on Linux


    requires:
    - Python 2.6+
    - Linux 2.6+

"""

import os
import glob


def get_procs():
	"""
	Returns a list of all the processes on the system
	"""
	return [pid for pid in os.listdir('/proc') if pid.isdigit()]

def get_cmd(pid):
	"""
	Returns the command used to run that processes
	"""
	return open('/proc/'+pid+'/cmdline', 'rb').read().replace('\x00', ' ').split()

def get_exe(pid):
	"""
	Returns path to exucatable file that started this processes
	"""
	if os.path.isfile('/proc/'+pid+'/exe') == True:
		return os.path.realpath('/proc/'+pid+'/exe')
	return None

def get_stat(pid):
	"""
	Returns some great information about the processes
	https://www.kernel.org/doc/Documentation/filesystems/proc.txt
	Table 1 - 4
	"""
	keys = ['pid', 'comm', 'state', 'ppid', 'pgrp', 'sid', 'tty_nr', 'tty_pgrp', 'flags', 'min_flt', 'cmin_flt', 'maj_flt', 'cmaj_flt', 'utime', 'stime', 'cutime', 'cstime', 'priority', 'nice', 'num_threads', 'it_real_vaules', 'start_time', 'vsize', 'rss', 'rsslim', 'start_code', 'end_code', 'start_stack', 'esp', 'eip', 'pending', 'blocked', 'sigign', 'sigcatch', 'wchan','0','0','exit_signal', 'task_cpu', 'rt_priority', 'policy', 'block_ticks', 'gtime', 'cgtime', 'start_data', 'end_data','start_brk', 'arg_start', 'arg_end', 'env_start', 'env_end', 'env_code']
	stat = open(os.path.join('/proc', pid, 'stat'), 'rb').read().split("\n")[0].split(" ")
	return dict(zip(keys, stat))

def get_status(pid):
	status = dict()
	for line in open('/proc/'+str(pid)+'/status', 'rb').read().split("\n")[0:-1]:
		line = line.replace("\t", "").split(":")
		#print line
		status[line[0]] = line[1]

	return status

def get_statm(pid):
	"""
	Return some great information about the processes statm (memory stats)
	"""
	stat = open(os.path.join('/proc/'+pid+'/statm'), 'rb').read().split(" ")
	return dict(zip(['size', 'resident', 'share', 'text', 'lib', 'data', 'dt'], stat))

def get_io(pid):
	"""
	Returns the IO usage of a processes since birth
	"""
	io = dict()
	for line in open('/proc/'+pid+'/io', 'rb').read().split("\n")[0:-1]:
		line = line.split(": ")
		io[line[0]] = int(line[1])

	return io
