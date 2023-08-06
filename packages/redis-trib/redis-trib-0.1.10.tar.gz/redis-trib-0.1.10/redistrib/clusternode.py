import socket
import hiredis
import logging

SYM_STAR = '*'
SYM_DOLLAR = '$'
SYM_CRLF = '\r\n'
SYM_EMPTY = ''


def encode(value, encoding='utf-8'):
    if isinstance(value, bytes):
        return value
    if isinstance(value, (int, long)):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, unicode):
        return value.encode(encoding)
    if not isinstance(value, basestring):
        return str(value)
    return value


def pack_command(command, *args):
    output = []
    if ' ' in command:
        args = tuple([s for s in command.split(' ')]) + args
    else:
        args = (command,) + args

    buff = SYM_EMPTY.join((SYM_STAR, str(len(args)), SYM_CRLF))

    for arg in map(encode, args):
        if len(buff) > 6000 or len(arg) > 6000:
            buff = SYM_EMPTY.join((buff, SYM_DOLLAR, str(len(arg)), SYM_CRLF))
            output.append(buff)
            output.append(arg)
            buff = SYM_CRLF
        else:
            buff = SYM_EMPTY.join((buff, SYM_DOLLAR, str(len(arg)),
                                   SYM_CRLF, arg, SYM_CRLF))
    output.append(buff)
    return output

CMD_PING = pack_command('ping')
CMD_INFO = pack_command('info')
CMD_CLUSTER_NODES = pack_command('cluster', 'nodes')
CMD_CLUSTER_INFO = pack_command('cluster', 'info')


class Talker(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.reader = hiredis.Reader()
        self.last_raw_message = ''

        self.sock.settimeout(8)
        logging.debug('Connect to %s:%d', host, port)
        self.sock.connect((host, port))

    def _recv(self):
        while True:
            m = self.sock.recv(16384)
            self.last_raw_message += m
            self.reader.feed(m)
            r = self.reader.gets()
            if r != False:
                return r

    def talk_raw(self, command):
        for c in command:
            self.sock.send(c)
        r = self._recv()
        if r is None:
            raise ValueError('No reply')
        if isinstance(r, hiredis.ReplyError):
            raise r
        return r

    def talk(self, *args):
        return self.talk_raw(pack_command(*args))

    def close(self):
        return self.sock.close()


class ClusterNode(object):
    # What does each field mean in "cluster nodes" output
    # > http://oldblog.antirez.com/post/2-4-and-other-news.html
    # but assigned slots / node_index not listed
    def __init__(self, node_id, latest_know_ip_address_and_port,
                 role_in_cluster, node_id_of_master_if_it_is_a_slave,
                 last_ping_sent_time, last_pong_received_time, node_index,
                 link_status, *assigned_slots):
        self.node_id = node_id
        host, port = latest_know_ip_address_and_port.split(':')
        self.host = host
        self.port = int(port)
        self.role_in_cluster = (role_in_cluster.split(',')[1]
                                if 'myself' in role_in_cluster
                                else role_in_cluster)
        self.master_id = node_id_of_master_if_it_is_a_slave
        self.assigned_slots = []
        for slots_range in assigned_slots:
            if '[' == slots_range[0] and ']' == slots_range[-1]:
                # exclude migrating slot
                continue
            if '-' in slots_range:
                begin, end = slots_range.split('-')
                self.assigned_slots.extend(range(int(begin), int(end) + 1))
            else:
                self.assigned_slots.append(int(slots_range))

        self._talker = None

    def talker(self):
        if self._talker is None:
            self._talker = Talker(self.host, self.port)
        return self._talker

    def close(self):
        if self._talker is not None:
            self._talker.close()
            self._talker = None


class BaseBalancer(object):
    def weight(self, clusternode):
        return 1


def base_balance_plan(nodes, balancer=None):
    if balancer is None:
        balancer = BaseBalancer()
    nodes = [n for n in nodes if 'master' == n.role_in_cluster]
    origin_slots = [len(n.assigned_slots) for n in nodes]
    total_slots = sum(origin_slots)
    weights = [balancer.weight(n) for n in nodes]
    total_weight = sum(weights)

    result_slots = [total_slots * w / total_weight for w in weights]
    frag_slots = total_slots - sum(result_slots)

    migratings = [[n, r - o] for n, r, o in
                  zip(nodes, result_slots, origin_slots)]

    for m in migratings:
        if frag_slots > -m[1] > 0:
            frag_slots += m[1]
            m[1] = 0
        elif frag_slots <= -m[1]:
            m[1] += frag_slots
            break

    migrating = sorted([m for m in migratings if m[1] != 0],
                       key=lambda x: x[1])
    mig_out = 0
    mig_in = len(migrating) - 1

    plan = []
    while mig_out < mig_in:
        if migrating[mig_in][1] < -migrating[mig_out][1]:
            plan.append((migrating[mig_out][0], migrating[mig_in][0],
                         migrating[mig_in][1]))
            migrating[mig_out][1] += migrating[mig_in][1]
            mig_in -= 1
        elif migrating[mig_in][1] > -migrating[mig_out][1]:
            plan.append((migrating[mig_out][0], migrating[mig_in][0],
                         -migrating[mig_out][1]))
            migrating[mig_in][1] += migrating[mig_out][1]
            mig_out += 1
        else:
            plan.append((migrating[mig_out][0], migrating[mig_in][0],
                         migrating[mig_in][1]))
            mig_out += 1
            mig_in -= 1

    return plan
