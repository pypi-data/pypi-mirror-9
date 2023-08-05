from credis.base import Connection


class RedisDecodeException(Exception):
    pass


class Redis(object):

    def __init__(self, conn):
        self.conn = conn

    @classmethod
    def connect(cls, *args, **kwargs):
        conn = Connection(*args, **kwargs)
        return cls(conn)

    def info(self):
        s = self.conn.execute('INFO')
        sections = []
        for line in s.split('\r\n'):
            if not line:
                # empty line
                continue
            elif line[0] == '#':
                # new section
                sections.append((line[2:], []))
                continue
            else:
                key, value = line.split(':', 1)
                if value.isdigit():
                    value = int(value)
                try:
                    section = sections[-1]
                except IndexError:
                    raise RedisDecodeException
                else:
                    section[1].append((key, value))
        return sections

    def cluster(self, subcmd):
        '''
        @subcmd:
            nodes
                list nodes
            slots
                list slots
            addslots [slot] [slot] ...
                alloc slots to this node
            set-config-epoch index
            meet
                join cluster
        '''
        subcmd = subcmd.upper()
        rsp = self.conn.execute('CLUSTER', subcmd)
        if subcmd=='NODES':
            rsp.split()
        elif subcmd=='SLOTS':


