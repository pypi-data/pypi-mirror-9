#!/usr/bin/env python3

import os, re, sqlalchemy as sa
import moo.connector

class execute(moo.connector.execute):

    def get_connections(self, connections, config):
        if config and (connections is None):
            return self.read_file(config).splitlines()
        elif isinstance(connections, str) and (config is None):
            return [connections]
        elif connections and (config is None):
            return connections
        else:
            raise self.moo_error('get_connections({}, {})'.format(connections, config))

    def hide_password(self, connection):
        return re.sub(r':[^:]*@', r'@', connection)

    def execute_command(self, connection):
        r_queue = []
        r_queue.append('\n[{}] pid={}'.format(self.hide_password(connection), os.getpid()))
        try:
            engine = sa.create_engine(connection)
            connection = engine.connect()
            result = connection.execute(self.command)
            keys, rows = result.keys(), result.fetchall()
            result.close()
            connection.close()
            r_queue.append('{}'.format(keys))
            for row in rows:
                r_queue.append('{}'.format(row))
            if self.debug: r_queue.append('$num_rows={}$'.format(len(rows)))
            return r_queue
        except Exception as e:
            print('{}'.format(e))
            raise

if __name__ == '__main__':
    execute('sqlite:///:memory:', debug=True)('select 23 as number union select 42 as number')
    execute('sqlite:///:memory:')('select 23 as number union select 42 as number')
