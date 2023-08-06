#
# Copyright (c) 2014, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
import sys
import re
import socket
import struct

from pyeapi.api import Entity, EntityCollection

ACE_PROTO_AHP = 51
ACE_PROTO_GRE = 47
ACE_PROTO_ICMP = 1
ACE_PROTO_IGMP = 2
ACE_PROTO_IP = 0
ACE_PROTO_OSPF = 89
ACE_PROTO_PIM = 103
ACE_PROTO_TCP = 6
ACE_PROTO_UDP = 17
ACE_PROTO_VRRP = 112

ACL_RULE_RE = re.compile(r'^[\s|\d]+([p|d].+)$', re.M)

ANY_RE = re.compile(r'(?<=[permit|deny]\s)(any)')

IP_WITH_HOST_RE = re.compile(r'(?<=host\s)(?P<subnet>[0-9]+(?:\.[0-9]+){3})')

IP_WITH_LEN_RE = re.compile(r'(?P<subnet>[0-9]+(?:\.[0-9]+){3})'
                            r'/(?P<len>[0-9]{1,3})')

IP_WITH_MASK_RE = re.compile(r'(?P<subnet>[0-9]+(?:\.[0-9]+){3})'
                             r'\s(?P<mask>[0-9]+(?:\.[0-9]+){3})')

class Acl(EntityCollection):

    def get(self, name):

        config = self.get_block('ip access-list standard %s' % name)
        if not config:
            return None

        response = dict(name=name, type='standard')
        rules = ACL_RULE_RE.findall(config, re.M)
        response['rules'] = [r.strip() for r in rules]
        return response

    def getall(self):
        acls_re = re.compile(r'(?<=list\sstandard\s)(.+)$', re.M)

        response = dict()
        for name in acls_re.findall(self.config, re.M):
            acl = self.get(name)
            if acl:
                response[name] = acl
        return response

    def create(self, name):
        return self.configure('ip access-list standard %s' % name)

    def delete(self, name):
        return self.configure('no ip access-list standard %s' % name)

    def default(self, name):
        return self.configure('default ip access-list standard %s' % name)

    def set_rules(self, name, entries):
        commands = ['no ip access-list standard %s' % name,
                    'ip access-list standard %s' % name]
        commands.extend(entries)
        return self.configure(commands)

    def add_entry(self, name, ace, seqno=None):
        if seqno is not None and isint(seqno, 1, 4294967295):
            ace = '%s %s' % (seqno, ace)
        commands = ['ip access-list standard %s' % name, ace]
        return self.configure(commands)

    def remove_entry(self, name, seqno):
        if not isint(seqno, 1, 4294967295):
            raise TypeError('invalid seqno')

        commands = ['ip access-list standard %s' % name, 'no %s' % seqno]
        return self.configure(commands)

def convert_prefix_length(mask):
    mask = int(mask)
    bits = 0xffffffff ^ (1 << 32 - mask) - 1
    return socket.inet_ntoa(struct.pack('>I', bits))

def get_network(prefix, mask):
    prefix = struct.unpack('!L', socket.inet_aton(prefix))[0]
    mask = struct.unpack('!L', socket.inet_aton(mask))[0]
    net = prefix & mask
    return socket.inet_ntoa(struct.pack('!L', net))

def transform_ace(rule):

    patterns = [
        IP_WITH_HOST_RE,
        IP_WITH_LEN_RE,
        IP_WITH_MASK_RE,
        ANY_RE
    ]

    aclentry = 'permit' if 'permit' in rule else 'deny'

    for index, pattern in enumerate(patterns):
        match = pattern.search(rule)
        if match:
            if index == 0:
                aclentry += ' host %s' % match.group('subnet')

            elif index == 1:
                mask = convert_prefix_length(match.group('len'))
                network = get_network(match.group('subnet'), mask)
                aclentry += ' %s/%s' % (network, match.group('len'))

            elif index == 2:
                network = get_network(match.group('subnet'),
                                      match.group('mask'))
                aclentry += ' %s %s' % (network, match.group('mask'))

            elif index == 3:
                aclentry += ' any'

    aclentry += ' %s' % 'log' if rule.endswith('log') else ''
    return aclentry

def ace(acetype, *args, **kwargs):
    if acetype == 'standard':
        return stdace(*args, **kwargs)
    elif acetype == 'extended':
        return extace(*args, **kwargs)
    else:
        TypeError('unknown ace type requested')


def stdace(action, src, mask=None, log=False):
    if action not in ['permit', 'deny']:
        raise TypeError('invalid action specified')

    if mask is not None:
        if not isint(mask, maxvalue=32):
            raise TypeError('invalid value for mask')

    entry = action
    entry += ' %s' % ace_address(src, mask)

    if log:
        entry += ' log'

    return transform_ace(entry)

def extace(action, proto, src, dst, src_mask=None, dst_mask=None, options=None):
    src = ace_address(src, src_mask)
    dst = ace_address(dst, dst_mask)

    if not isint(proto, 1, 255):
        raise TypeError('invalid protocol value specified')

    entry = '%s %s' % (action, proto)
    entry += ' %s %s' % (src, dst)
    if options:
        entry += ' %s' % options
    return entry

def ace_address(addr, mask=None):
    entry = ''
    if addr == 'any':
        entry += 'any'
    elif mask in ['32', '255.255.255.255', None]:
        entry += 'host %s' % addr
    elif isint(mask, maxvalue=32):
        entry += '%s/%s' % (addr, mask)
    else:
        entry += '%s %s' % (addr, mask)
    return entry

def isint(value, minvalue=0, maxvalue=sys.maxint):
    try:
        value = int(value)
        return minvalue <= value <= maxvalue
    except ValueError:
        return False

def instance(api):
    return Acl(api)

