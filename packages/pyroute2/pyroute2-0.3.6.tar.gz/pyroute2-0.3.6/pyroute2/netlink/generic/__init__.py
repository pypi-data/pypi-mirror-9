'''
Generic netlink
===============

Describe
'''

from pyroute2.netlink import CTRL_CMD_GETFAMILY
from pyroute2.netlink import GENL_ID_CTRL
from pyroute2.netlink import NLM_F_REQUEST
from pyroute2.netlink import ctrlmsg
from pyroute2.netlink.nlsocket import NetlinkSocket


class GenericNetlinkSocket(NetlinkSocket):
    '''
    Low-level socket interface. Provides all the
    usual socket does, can be used in poll/select,
    doesn't create any implicit threads.

    Provides two additional methods:
    * get_protocol_id() -- resolve generic netlink proto
    * get() -- receive and parse netlink messages
    '''

    def bind(self, proto, msg_class, groups=0, pid=0, async=False):
        '''
        Bind the socket and performs generic netlink
        proto lookup. The `proto` parameter is a string,
        like "TASKSTATS", `msg_class` is a class to
        parse messages with.
        '''
        NetlinkSocket.bind(self, groups, pid, async)
        self.marshal.msg_map[GENL_ID_CTRL] = ctrlmsg
        self.prid = self.get_protocol_id(proto)
        self.marshal.msg_map[self.prid] = msg_class

    def get_protocol_id(self, proto):
        '''
        Resolve generic netlink protocol -- takes a string
        as the only parameter, return integer proto ID
        '''
        msg = ctrlmsg()
        msg['cmd'] = CTRL_CMD_GETFAMILY
        msg['version'] = 1
        msg['attrs'].append(['CTRL_ATTR_FAMILY_NAME', proto])
        msg['header']['type'] = GENL_ID_CTRL
        msg['header']['flags'] = NLM_F_REQUEST
        msg['header']['pid'] = self.pid
        msg.encode()
        self.sendto(msg.buf.getvalue(), (0, 0))
        msg = self.get()[0]
        err = msg['header'].get('error', None)
        if err is not None:
            raise err
        return msg.get_attr('CTRL_ATTR_FAMILY_ID')
