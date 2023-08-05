#!/usr/bin/env python3

# $$todo$$ ~> multiprocessing unexpectedly kill encfs mount-points

import os
from multiprocessing import Pool
from multiprocessing.dummy import Pool
from multiprocessing.pool import ThreadPool as Pool # http://stackoverflow.com/questions/3033952/python-thread-pool-similar-to-the-multiprocessing-pool

class execute():

    class moo_error(Exception): pass

    def __init__(self, connections=None, *, config=None, script_directory='', parallel=None, debug=False):
        self.connections = self.get_connections(connections, config)
        self.script_directory = script_directory
        self.parallel = parallel
        self.debug = debug
        if self.debug:
            self.print_debug = print
        else:
            self.print_debug = self.nothing
        self.print_debug('$debug={}$'.format(self.debug))

    def nothing(*args, **kwargs): pass

    def get_command(self, command, script):
        if script and (command is None):
            return self.read_file(os.path.join(self.script_directory, script)).strip()
        elif command and (script is None):
            return command
        else:
            raise self.moo_error('get_command({}, {})'.format(command, script))

    def read_file(self, filename):
        if os.path.exists(filename):
            with open(filename, mode='r', encoding='utf-8') as f:
                return f.read()
        else:
            raise self.moo_error('file {} does not exist'.format(filename))

    def get_parallel(self, parallel):
        parallel = parallel or self.parallel or None
        self.print_debug('$parallel={}$'.format(parallel))
        return parallel

    def __call__(self, command=None, *, script=None, parallel=None): # functor
        self.command = self.get_command(command, script)
        print('[{}]'.format(self.command))
        with Pool(self.get_parallel(parallel)) as pool:
            pool.map_async(self.execute_command, self.connections, 1, self.r_print)
            pool.close()
            pool.join()
        print()

    def script(self, script=None, *, parallel=None):
        self.__call__(script=script, parallel=parallel)

    def hide_password(self, connection):
        return connection

    def r_print(self, r_queue):
        for rows in r_queue:
            for row in rows:
                print(row)
