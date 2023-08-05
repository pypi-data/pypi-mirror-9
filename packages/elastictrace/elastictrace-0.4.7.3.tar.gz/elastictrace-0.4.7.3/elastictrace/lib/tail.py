#!/usr/bin/env python

'''
Python-Tail - Unix tail follow implementation in Python. 

python-tail can be used to monitor changes to a file.

Example:
    import tail

    # Create a tail instance
    t = tail.Tail('file-to-be-followed')

    # Register a callback function to be called when a new line is found in the followed file. 
    # If no callback function is registerd, new lines would be printed to standard out.
    t.register_callback(callback_function)

    # Follow the file with 5 seconds as sleep time between iterations. 
    # If sleep time is not provided 1 second is used as the default time.
    t.follow(s=5) '''

# Author - Alexis Okuwa <alexisokuwa at gmail.com>
# Source - https://github.com/wojons/python-tail
# Forked - https://github.com/kasun/python-tail

import os
import sys
import time

class Tail(object):
	''' Represents a tail command. '''
	tailed_files  = list()
	tailed_points = list()
	callbacks     = dict()
	inode         = list()
	last          = {'filename' : ""}
	
	def __init__(self):
		''' Initiate a Tail instance.
			Check for file validity, assigns callback function to standard out.
			
			Arguments:
				tailed_file - File to be followed. '''
	
	def tail(self, tailed_files, callback=None):
		if type(tailed_files).__name__ == 'str': #we allow strings we will just handle the converstion
			tailed_files = [tailed_files]
		
		for tailed_file in tailed_files: #make sure we have good files all around
			self.check_file_validity(tailed_file)
			Tail.tailed_files.append(tailed_file)
			Tail.callbacks[tailed_file] = callback #if callback == None else sys.stdout.write
		#self.callback = sys.stdout.write
		self.track_name(-1)
	
	def follow(self, s=1):
		''' Do a tail follow. If a callback function is registered it is called with every new line. 
		Else printed to standard out.

		Arguments:
			s - Number of seconds to wait between each iteration; Defaults to 1. '''
		Tail.tailed_points = []
		Tail.god_time = time.time()
		for filename in Tail.tailed_files:
			Tail.tailed_points.append(open(filename)) #get all the file points
			Tail.tailed_points[len(Tail.tailed_points)-1].seek(0, os.SEEK_END) #handle all the seeking
			
		while True:
			start_t = time.time() #gotta keep track of how long we been in this
			for num, file_ in enumerate(Tail.tailed_points):
				file_ = self.read_2_EOF(num, file_)
			time_lap = time.time()-start_t
			if(time_lap < s):
				self.check_inode()
				time.sleep(s - time_lap)
			
	def read_2_EOF(self, dex, file_):
		line = True #reset line value
		while line:
			curr_position = file_.tell() #get current postion
			line = file_.readline() #read the next line we use readline() and not readlines because we may read a line that is still being written to.
			if not line:
				file_.seek(curr_position) #reset the seek point so we can try from the same point again
			else:
				self.exec_callback(line, Tail.tailed_files[dex])
		return file_
	
	def exec_callback(self, line, filename):
		#print line
		Tail.callbacks[filename]({'line':line, 'filename':filename})
	
	"""
	def register_callback(self, func, mode=0):
		''' Overrides default callback function to provided function. '''
		self.callback = func
		self.callback_mode = mode
	"""
	def track_name(self, timer):
		Tail.follow_timer = {'wait' : timer, 'last' : time.time()}
		Tail.inode = list()
		for filename in Tail.tailed_files: #loop though all the files we want to track
			Tail.inode.append(os.stat(filename).st_ino) #get the inode of the file
	
	def check_inode(self):
		if Tail.follow_timer['wait'] > 0 and time.time()-Tail.follow_timer['last'] >= Tail.follow_timer['wait']: #check to see if we have this tracking on
			for dex, filename in enumerate(self.tailed_files):
				if os.stat(filename).st_ino != Tail.inode[dex]: #check if the inode has changed
					self.read_2_EOF(dex, Tail.tailed_points[dex]) #read the current but old file to EOF
					Tail.tailed_points[dex] = open(filename) # reopen the file pointer to the replacment file
					Tail.tailed_points[dex].seek(0, os.SEEK_SET)#change the location on the file pointer to be the start of the file
					Tail.inode[dex] = os.stat(filename).st_ino #write the new inode

	def check_file_validity(self, file_):
		''' Check whether the a given file exists, readable and is a file '''
		if not os.access(file_, os.F_OK):
			raise TailError("File '%s' does not exist" % (file_))
		if not os.access(file_, os.R_OK):
			raise TailError("File '%s' not readable" % (file_))
		if os.path.isdir(file_):
			raise TailError("File '%s' is a directory" % (file_))

class TailError(Exception):
    def __init__(self, msg):
        self.message = msg
    def __str__(self):
        return self.message

def print2(dump):
	print str(dump)

if __name__ == "__main__":
	import tail
	#t = tail.Tail()
	#t.tail('/tmp/tail1.txt', print2)
	#t.follow(1)
