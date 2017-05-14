#!/usr/bin/env python
#
# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import print_function
import sys, os, logging, collections, struct, json, glob
import pprint, argparse

# Globals
messages = {}

def __struct (t, n = None, e = -1, vl = None):
    base_types = { 'u8' : 'bytes',
                   'u16' : 'uint32',
                   'u32' : 'uint32',
                   'i32' : 'int32',
                   'u64' : 'uint64',
                   'f64' : 'float',
                   'bool' : 'bool',
                   }
    pack = None
    if t in base_types:
        if e >= 0:
            return 'repeated ' + base_types[t]
        else:
            return base_types[t]

    if t in messages:
        ### Return a list in case of array ###
        if e > 0 and not vl:
            return 'repeated ' + t
        if vl:
            return 'repeated ' + t
        elif e == 0:
            # Old style VLA
            raise NotImplementedError(1, 'No support for compound types ' + t)
        return 'repeated ' + t
    raise ValueError(1, 'Invalid message type: ' + t)


def add_message(name, msgdef, typeonly = False):
    if name in messages:
        raise ValueError('Duplicate message name: ' + name)

    args = collections.OrderedDict()
    msg = {}

    for i, f in enumerate(msgdef):
        if type(f) is dict and 'crc' in f:
            msg['crc'] = f['crc']
            continue
        field_type = f[0]
        field_name = f[1]
        if len(f) == 3 and f[2] == 0 and i != len(msgdef) - 2:
            raise ValueError('Variable Length Array must be last: ' + name)

        # Assume u8 + is_ means bool
        if field_name.startswith('is_') and f[0] == "u8":
            args[field_name + '_comment'] = field_type
            field_type = f[0] = 'bool'
        # u16 is unsupported
        elif field_type == 'u16':
            args[field_name + '_comment'] = field_type

        args[field_name] = __struct(*f)

        if len(f) == 4: # Find offset to # elements field
            # Ensure length/count field is commented out?
            #args[f[3]] = '// ' + args[f[3]]
            args[f[3] + '_comment'] = 'len_of:' + field_name

        if len(f) >= 3:
            if field_name + '_comment' in args:
                args[field_name + '_comment'] += 'length = ' + str(f[2])
            else:
                args[field_name + '_comment'] = 'length = ' + str(f[2])

    messages[name] = msg
    messages[name]['args'] = args
    messages[name]['typeonly'] = typeonly
    return messages[name]

def add_type(name, typedef):
    return add_message('vl_api_' + name + '_t', typedef, typeonly=True)

def print_pubsub_services():
    print('service', module + '_subscribe', '{')
    for name, msgdef in messages.iteritems():
        if messages[name]['typeonly']:
            continue
        if name.endswith('_reply') or name.endswith('_details'):
            continue
        if name.startswith('want_'):
            reply = name + '_reply'
        else:
            continue
        request = name + '_request'
        if not reply in messages:
            print('// WARNING Cannot find reply matching request ' + request + ' ' + reply)
            continue
        print('  rpc ' + name + ' (' + request + ') returns (' +  reply + ');')
    print('}')

def print_req_response_services():
    print('service', module, '{')
    for name, msgdef in messages.iteritems():
        if messages[name]['typeonly']:
            continue
        if name.startswith('want_'):
            continue
        if name.endswith('_reply') or name.endswith('_details'):
            continue
        if name.endswith('_dump'):
            reply = name.rstrip('_dump') + '_details'
            stream = 'stream '
        else:
            reply = name + '_reply'
            stream = ''
        request = name + '_request'
        if not reply in messages:
            print('// WARNING Cannot find reply matching request ' + request + ' ' + reply)
            continue
        print('  rpc ' + name + ' (' + request + ') returns (' + stream + reply + ');')
    print('}')

def print_services():
   print_req_response_services()
   print_pubsub_services()
#
# Main
#
def vppprotogen(command_arguments):
    global module
    parser = argparse.ArgumentParser()
    parser.add_argument('jsonfile')
    parser.add_argument('--services', dest='services', action='store_true',
                        help="Produce GRPC services section")
    parser.add_argument('--no-services', dest='services', action='store_false',
                        help="Do not produce GRPC services section")
    parser.set_defaults(services=True)

    args = parser.parse_args(command_arguments)
    with open(args.jsonfile) as apidef_file:
        api = json.load(apidef_file)
        for t in api['types']:
            add_type(t[0], t[1:])

        for m in api['messages']:
            add_message(m[0], m[1:])

    module = args.jsonfile.split('.', 1)[0]
    module = module.split('/')[-1:][0]
    orig_stdout = sys.stdout
    f = open(module+'.proto', 'w')
    sys.stdout = f
    print('// File:', args.jsonfile)
    print('syntax = "proto3";')
    #
    # Generate messages
    #
    for name, msgdef in messages.iteritems():
        count = 1
        if not name.endswith('_reply') and not name.endswith('_details') and not messages[name]['typeonly']:
            name_req = name + '_request'
        else:
            name_req = name
        if messages[name]['typeonly']:
            print('// Type')
        print('message', name_req, '{')
        for k,v in msgdef['args'].iteritems():
            # XXX: _comment stuff is a bit of a hack...
            if k.endswith('_comment'):
                continue
            if type(v) is list:
                raise ValueError(1, 'Wrong list')
            if k + '_comment' in msgdef['args']:
                comment = ' // ' + msgdef['args'][k + '_comment']
            else:
                comment = ''
            print (' ', v, k, '=', str(count) + ';' + comment)
            count += 1
        print('}')

    #
    # Generate services
    #
    if args.services:
        print_services()
    sys.stdout = orig_stdout
    f.close()

if __name__ == '__main__':
    sys.exit(vppprotogen(sys.argv[1:]))
