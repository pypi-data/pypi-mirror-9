import plugin
import os
import glob
import time
import hashlib
import json
import syslog
import socket
import telnetlib
import sys
import random
import requests


class rethinkdb(plugin.Plugin):

    def __init__(self, *args, **kwargs):
        super(rethinkdb, self).__init__()
        self.kwargs         = kwargs
        self.config         = kwargs['config']
        self.conf           = None
        self.metric_type_id = {'rethinkdb': self.get_metric_type_id('rethinkdb')}
        self.Agent_self     = kwargs['agent_self']

        self.stdout(self.config)
        
        self.old = {'tables': {}}

        #return self
        
    
    def getServerBlock(self, stats):
        return {
            'active_coroutines': int(stats.get('active_coroutines')),
            'allocated_coroutines' : int(stats.get('allocated_coroutines')),
            'query_language': int(stats.get('query_language', {}).get('ops_running')),
            'eventloop': {
                'active': int(stats.get('eventloop', {}).get('active_count')),
                'total': int(stats.get('eventloop', {}).get('total'))
            },
            'proc': {
                'pid': int(stats.get('proc', {}).get('pid')),
                'uptime': int(stats.get('proc', {}).get('uptime')),
                'version': stats.get('proc', {}).get('version'),
            },
            'sys': {
                'global_disk_space_free': int(stats.get('sys', {}).get('global_disk_space_free')),
                'global_disk_space_total': int(stats.get('sys', {}).get('global_disk_space_total')),
                'global_disk_space_used': int(stats.get('sys', {}).get('global_disk_space_used'))
            }
        }
    
    def getTableBlock(self, table_stats):
        serializer = table_stats.get('serializers', {}).get('serializer', {})
        master = {
            'serializer' : {
                'serializer_block_writes': int(serializer.get('serializer_block_writes')),
                'serializer_bytes_in_use': int(serializer.get('serializer_bytes_in_use')),
                'serializer_data_extents': int(serializer.get('serializer_data_extents')),
                'serializer_data_extents_allocated': int(serializer.get('serializer_data_extents_allocated')),
                'serializer_data_extents_gced': int(serializer.get('serializer_data_extents_gced')),
                'serializer_extents_in_use': int(serializer.get('serializer_extents_in_use')),
                'serializer_index_reads': int(serializer.get('serializer_index_reads')),
                'serializer_lba_extents': int(serializer.get('serializer_lba_extents')),
                'serializer_lba_gcs': int(serializer.get('serializer_lba_gcs')),
                'serializer_old_garbage_block_bytes': int(serializer.get('serializer_old_garbage_block_bytes')),
                'serializer_old_total_block_bytes': int(serializer.get('serializer_old_total_block_bytes')),
                
                'serializer_index_writes': {
                    'active': int(serializer.get('serializer_index_writes', {}).get('active_count')),
                    'total': int(serializer.get('serializer_index_writes', {}).get('total'))
                },
                
                'serializer_block_reads': {
                    'active': int(serializer.get('serializer_block_reads', {}).get('active_count')),
                    'total': int(serializer.get('serializer_block_reads', {}).get('total'))
                },
            },
            'btree': {}
        }
        
        for dex2, dat2 in table_stats.get('serializers', {}).iteritems():
            if dex2.startswith('shard_') is True:
                for dex3,dat3 in dat2.iteritems():
                    if dex3 != "cache":
                        
                        if dex3 not in master['btree']:
                            master['btree'][dex3] = {'keys_set': float(0), 'keys_read': float(0)}
                        
                        master['btree'][dex3]['keys_set']  += float(dat3.get('total_keys_set'))
                        master['btree'][dex3]['keys_read'] += float(dat3.get('total_keys_read'))
        
        return master
        
    def diffDict(self, dict1, dict2):
        master = dict()
        for k in dict1:
            if k in dict2:
                if isinstance(dict1, int) or  isinstance(dict1, float):
                    master[k] = dict1[k] - dict2[k]
                else:
                    master[k] = dict1
        
        return master
        #return dict((k, dict1[k] - dict2[k]) for k in dict1 if k in dict2 and ())

    def observe(self):
        self.log_time = self.logTime()
        config = self.Agent.session['metrics']['rethinkdb'][self.metric_type_id['rethinkdb']].get('metric_type_config', {'hostname': 'localhost', 'port' :'8080'})

        semilattice = requests.get('http://{0}:{1}/ajax/semilattice'.format(config['hostname'], config['port']))
        semilattice = semilattice.json()
        
        meta, server, tables = dict(), dict(), dict()
        meta['me']          = semilattice['me']
        meta['machines']    = semilattice['machines']
        meta['databases']   = semilattice['databases']
        meta['datacenters'] = semilattice['datacenters']
        meta['tables']      = dict()
        
        #handle name spacing
        for dex, dat in semilattice.get('rdb_namespaces').iteritems():
            if dat is not None and dat.get('name') is not None and dat.get('database') is not None:
                meta['tables'][dex] = {
                    'name': dat.get('name'),
                    'database': dat.get('database')
                }
        
        start = time.time()
        stats = requests.get('http://{0}:{1}/ajax/stat'.format(config['hostname'], config['port']))
        stats = stats.json().get(meta['me'])
        server = self.getServerBlock(stats) #get the server stats
        
        # diff old on server data
        if 'server' in self.old:
            server['eventloop']['total'] -= self.old['server']['eventloop']['total']
        
        for dex, dat in stats.iteritems():
            if len(dex) == 36 and dat.get('regions') is not None and len(dat.get('regions')): #is table uuid
                
                tables[dex] = self.getTableBlock(dat) #get the data for this table

                if dex in self.old['tables'] and server['proc']['uptime'] > self.old['server']['proc']['uptime']:
                    
                    new_s = tables[dex]['serializer']
                    old_s = self.old['tables'][dex]['serializer']
                    
                    new_s['serializer_lba_gcs']               -= old_s['serializer_lba_gcs']
                    new_s['serializer_index_reads']           -= old_s['serializer_index_reads']
                    new_s['serializer_block_writes']          -= old_s['serializer_block_writes']
                    new_s['serializer_data_extents_gced']     -= old_s['serializer_data_extents_gced']
                    new_s['serializer_block_reads']['total']  -= old_s['serializer_block_reads']['total']
                    new_s['serializer_index_writes']['total'] -= old_s['serializer_index_writes']['total']
                    
                    for index,val in tables[dex]['btree'].iteritems():
                        try:
                            if index in self.old['tables'][dex]['btree']:
                                tables[dex]['btree'][index]['keys_set']  -= self.old['tables'][dex]['btree'][index]['keys_set']
                                tables[dex]['btree'][index]['keys_read'] -= self.old['tables'][dex]['btree'][index]['keys_read']
                        except:
                            pass
                            
                
                self.old['tables'][dex] = self.getTableBlock(dat)  #set old value for table
                
        self.old['server'] = self.getServerBlock(stats) # set the old value to what current is
        
        self.payload = {
            'meta': meta,
            'server': server,
            'tables': tables
        }
        
        self.transmit_queue({self.metric_type_id['rethinkdb']: json.dumps(self.payload).encode('zlib').encode('base64'), 'logTime': self.log_time, 'encoding': ['base64', 'gzip', 'json']})
