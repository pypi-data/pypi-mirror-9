#!/usr/bin/env python3

import os, paramiko
from configurator.formats import json as configurator
import moo.connector

class execute(moo.connector.execute):

    def get_connections(self, connections, config):    
        if config and (connections is None):
            return configurator.load(config)['connections']
        elif isinstance(connections, str) and (config is None):
            return [connections]
        elif connections and (config is None):
            return connections
        else:
            raise self.moo_error('get_connections({}, {})'.format(connections, config))

    def hide_password(self, connection):
        return '{username}@{hostname}'.format(**connection)

    def execute_command(self, connection):
        r_queue = []
        r_queue.append('\n[{}] pid={}'.format(self.hide_password(connection), os.getpid()))
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(**connection)
            stdin, stdout, stderr = client.exec_command(self.command)
            stdout_text, stderr_text = stdout.read().decode().strip(), stderr.read().decode().strip()
            if self.debug: r_queue.append('[stdout] ~>')
            if stdout_text: r_queue.append(stdout_text)
            if self.debug: r_queue.append('[stderr] ~>')
            if stderr_text: r_queue.append(stderr_text)
            client.close()
            return r_queue
        except Exception as e:
            print('{}'.format(e))
            raise

if __name__ == '__main__':
    execute([{'hostname': 'localhost', 'username': 'pm', 'password': '********'}], debug=True)('df -h')
    execute([{'hostname': 'localhost', 'username': 'pm', 'password': '********'}])('df -h')
