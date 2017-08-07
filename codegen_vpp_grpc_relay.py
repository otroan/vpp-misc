#!/usr/bin/env python
"""
Plugin for generation of grpc to vpp python APIs
It's a plugin for protoc as per https://developers.google.com/protocol-buffers/docs/reference/other
Usage:
     protoc --plugin=protoc-gen-custom=<script path>/protobuf-json-docs.py <proto file>
"""

import sys
import collections

import re
from google.protobuf.compiler import plugin_pb2 as plugin
import itertools
import json
from google.protobuf.descriptor_pb2 import DescriptorProto, EnumDescriptorProto, EnumValueDescriptorProto, FieldDescriptorProto, ServiceDescriptorProto, MethodDescriptorProto

def simplify_name(name):
    "Remove all the namespace information to make short names for Sphinx"
    return name.split(".")[-1]

def convert_protodef_to_editable(proto):
    """
    Protobuf objects can't have arbitrary fields addedd and we need to later on
    add comments to them, so we instead make "Editable" objects that can do so
    """
    class Editable(object):
        def __init__(self, prot):
            self.kind = type(prot)
            self.name = prot.name
            self.comment = ""
            self.options = dict([(key.name, value) for (key, value) in prot.options.ListFields()])
            if isinstance(prot, EnumDescriptorProto):
                self.value = [convert_protodef_to_editable(x) for x in prot.value]
            elif isinstance(prot, DescriptorProto):
                self.field = [convert_protodef_to_editable(x) for x in prot.field]
                self.enum_type = [convert_protodef_to_editable(x) for x in prot.enum_type]
                self.nested_type = prot.nested_type
                self.oneof_decl = prot.oneof_decl
            elif isinstance(prot, EnumValueDescriptorProto):
                self.number = prot.number
            elif isinstance(prot, FieldDescriptorProto):
                if prot.type in [11, 14]:
                    self.ref_type = prot.type_name[1:]
                self.type = prot.type
                self.label = prot.label
            elif isinstance(prot, ServiceDescriptorProto):
                self.method = [convert_protodef_to_editable(x) for x in prot.method]
            elif isinstance(prot, MethodDescriptorProto):
                self.input_type = prot.input_type
                self.output_type = prot.output_type
            else:
                raise Exception, type(prot)

    return Editable(proto)

def traverse(proto_file):
    """
    proto_file is a FileDescriptorProto from protoc. We walk the SourceCodeInfo
    in this file, and find all the comments, and return a flattened out tree
    of all the messages and enums
    """
    def _collapse_comments(comments):
        return '\n'.join(
            [c.strip() for c in (comments["leading_comments"] + comments["trailing_comments"]).split('\n')])

    def _traverse(package, items, tree):
        for item_index, item in enumerate(items):
            item = convert_protodef_to_editable(item)
            if item_index in tree:
                comments = tree[item_index]
                if "leading_comments" in comments or "trailing_comments" in comments:
                    item.comment = _collapse_comments(comments)
                    del comments["leading_comments"]
                    del comments["trailing_comments"]
                if item.kind is EnumDescriptorProto:
                    if 2 in comments: # value in EnumDescriptorProto
                        for k in comments[2]:
                            value_comment = comments[2][k]
                            if value_comment != {}:
                                item.value[k].comment = _collapse_comments(value_comment)
                elif item.kind is DescriptorProto:
                    if 2 in comments: # field in DescriptorProto
                        for k in comments[2]:
                            field_comment = comments[2][k]
                            if field_comment != {}:
                                item.field[k].comment = _collapse_comments(field_comment)
                elif item.kind is ServiceDescriptorProto:
                    if 2 in comments: # method in ServiceDescriptorProto
                        for k in comments[2]:
                            method_comment = comments[2][k]
                            if method_comment != {}:
                                item.method[k].comment = _collapse_comments(method_comment)
                else:
                    raise Exception, item.kind

            yield item, package

            if item.kind is DescriptorProto:
                for enum in item.enum_type:
                    yield enum, package

                for nested in item.nested_type:
                    nested_package = package + "." + item.name

                    for nested_item, np in _traverse(nested_package, [nested], tree[item_index]):
                        yield nested_item, np

    tree = collections.defaultdict(collections.defaultdict)
    for loc in proto_file.source_code_info.location:
        if loc.leading_comments or loc.trailing_comments:
            place = tree
            for p in loc.path:
                if not place.has_key(p):
                    place[p] = collections.defaultdict(collections.defaultdict)
                place = place[p]
            place["leading_comments"] = loc.leading_comments
            place["trailing_comments"] = loc.trailing_comments
    
    # Only message, services, enums, extensions, options
    #if set(tree.keys()).difference(set([4, 5, 6, 7, 8])) != set():
    #    raise Exception, tree

    return {"types":
        list(itertools.chain(
            _traverse(proto_file.package, proto_file.service, tree[6]), # 6 is service_type in FileDescriptorProto
            _traverse(proto_file.package, proto_file.enum_type, tree[5]), # 5 is enum_type in FileDescriptorProto
            _traverse(proto_file.package, proto_file.message_type, tree[4]), # 4 is message_type in FileDescriptorProto
        )),
        "file": ["".join(x.leading_detached_comments) for x in proto_file.source_code_info.location if len(x.leading_detached_comments) > 0]
    }

def type_to_string(f, map_types):
    """
    Convert type info to pretty names, based on numbers from from FieldDescriptorProto
    https://developers.google.com/protocol-buffers/docs/reference/cpp/google.protobuf.descriptor.pb
    """
    if f.type in [1]:
        return "double"
    elif f.type in [2]:
        return "float"
    elif f.type in [3]:
        return "long"
    elif f.type in [4]:
        return "uint64"
    elif f.type in [5]:
        return "integer"
    elif f.type in [6]:
        return "fixed64"
    elif f.type in [7]:
        return "fixed32"
    elif f.type in [8]:
        return "boolean"
    elif f.type in [9]:
        return "string"
    # missing type 10 - Group
    elif f.type in [11, 14]:
        ref_name = f.ref_type
        if ref_name in map_types:
            ref_fields = map_types[ref_name]
            return {
                "type": "map",
                "key": " %s "% type_to_string(ref_fields["key"], map_types),
                "value": " %s "% type_to_string(ref_fields["value"], map_types)
            }
        else:
            kind = ":protobuf:message:`%s`" % simplify_name(f.ref_type)
            if f.label == 3: # LABEL_REPEATED
                return "list of " + kind
            else:
                return kind
    elif f.type in [12]:
        return "bytes"
    elif f.type in [13]:
        return "uint32"
    elif f.type in [15]:
        return "sfixed32"
    elif f.type in [16]:
        return "sfixed64"
    elif f.type in [17]:
        return "sint32"
    elif f.type in [18]:
        return "sint64"
    else:
        raise Exception, f.type

def generate_request_response_service_class (item, package, proto_file, protofile_grpc):
    service_class_code_gen = 'class %sServicer( %s.%sServicer):\n' % (item.name, protofile_grpc, item.name)
    service_class_code_gen += ' def __init__(self, vpp):\n  self.vpp = vpp\n'
    for m in item.method:
        if "dump" in m.name:
            service_class_code_gen += ' def %s (self, request, context):\n' % m.name
            service_class_code_gen += '  rv = self.vpp.%s(**grpcmsg_to_namedtuple(request, self.len_of_dict))\n' % m.name
            service_class_code_gen += '  for m in rv:\n'
            dump_reply = re.sub('dump', 'details', m.name)
            service_class_code_gen += '    yield %s_pb2.%s(**vppmsg_to_namedtuple(m))\n' % (
            proto_file.name.split("/")[-1].split(".")[0], dump_reply)

        else:
            service_class_code_gen += ' def %s (self, request, context):\n' % m.name
            service_class_code_gen += '  rv = self.vpp.%s(**grpcmsg_to_namedtuple(request, self.len_of_dict))\n' % m.name
            service_class_code_gen += '  return %s_pb2.%s_reply(**vppmsg_to_namedtuple(rv))\n' % (
            (proto_file.name.split("/")[-1].split(".")[0], m.name))
    return(service_class_code_gen)

def generate_subscriber_service_class (item, package, proto_file, protofile_grpc):
    service_class_code_gen = '\nclass %sServicer( %s.%sServicer):\n' % (item.name, protofile_grpc, item.name)
    service_class_code_gen += ' def __init__(self, vpp):\n'
    service_class_code_gen += '  self.vpp = vpp\n'
    service_class_code_gen += '  self.vpp.register_event_callback(self.publish_events)\n'
    #service_class_code_gen += '  self.subscription_db = defaultdict(list)\n'
    service_class_code_gen += '  self.subscription_db =[]\n'
    service_class_code_gen += ' def publish_events(self, msgname, result):\n'
    service_class_code_gen += '  print(\'received event %s\' % msgname)\n'
    service_class_code_gen += "  notification_event = getattr(%s_pb2,msgname)(**vppmsg_to_namedtuple(result))\n" % \
                              ((proto_file.name.split("/")[-1].split(".")[0]))
    #service_class_code_gen += '  for client_stub in self.subscription_db[msgname]:\n'
    # TODO: refine this, if a client subscribes to one event it receives all notifications for the class
    service_class_code_gen += '  for client_stub in self.subscription_db:\n'
    service_class_code_gen += '   getattr(client_stub, msgname + \'_notification\')(notification_event)\n'
    for m in item.method:
        service_class_code_gen += ' def %s (self, request, context):\n' % m.name
        # context.peer() gives the channel client/peer has for request response. But the
        # channel it is listening for notifications could be different
        service_class_code_gen += '  channel = grpc.insecure_channel(request.grpc_target)\n'
        service_class_code_gen += '  stub = %s_pb2_grpc.%s_notificationsStub(channel)\n' % \
                                  ((proto_file.name.split("/")[-1].split(".")[0]),
                                   (proto_file.name.split("/")[-1].split(".")[0]))
        #TODO: append to the notification requested not to the entire class
        #self.subscription_db["notification_name"].append(stub)'
        service_class_code_gen += '  self.subscription_db.append(stub)\n'
        service_class_code_gen += '  rv = self.vpp.%s(**grpcmsg_to_namedtuple(request, self.len_of_dict, subscribe=True))\n'\
                                  % m.name
        service_class_code_gen += '  return %s_pb2.%s_reply(**vppmsg_to_namedtuple(rv))\n' % (
        (proto_file.name.split("/")[-1].split(".")[0], m.name))
    return(service_class_code_gen)

def generate_code(request, response):
    """
    Core function. Starts from a CodeGeneratorRequest and adds files to
    a CodeGeneratorResponse
    """
    for proto_file in request.proto_file:
        types = []
        messages = {}
        len_of_dict = {}

        results = traverse(proto_file)
        map_types = {}

        protofile_pb2 = '%s_pb2' % proto_file.name.split("/")[-1].split(".")[0]
        protofile_grpc = '%s_pb2_grpc' % proto_file.name.split("/")[-1].split(".")[0]
        import_code_gen = 'import %s\n' % protofile_pb2
        import_code_gen += 'import %s\n' % protofile_grpc
        import_code_gen += 'from collections import defaultdict\n'
        subscriber_class_code_gen = ""
        for item, package in results["types"]:
            if item.kind == DescriptorProto:
                for f in item.field:
                    field_comment = f.comment
                    try:
                        len_of_field = re.search('len_of:(.+)$', f.comment).group(1).rstrip(' ')
                    except AttributeError:
                        len_of_field = ''
                    if len_of_field: 
                        len_of_dict[item.name + '.'+ len_of_field] = f.name
            if item.kind == ServiceDescriptorProto:
                if "notifications" in item.name:
                    continue #skip subscribtion service for now
                elif "subscribe" in item.name:
                    subscriber_class_code_gen = generate_subscriber_service_class (item, package,
                                                                                  proto_file, protofile_grpc)
                else:
                    service_class_code_gen = generate_request_response_service_class (item, package,
                                                                                  proto_file, protofile_grpc)
        f = response.file.add()
        f.name = proto_file.name + '.py'
        f.content = import_code_gen
        f.content += service_class_code_gen
        f.content += ' len_of_dict = {'
        for k,v in len_of_dict.iteritems():
            f.content += '\''+k+'\':\''+v+'\','
        f.content += '}\n'
        if len(subscriber_class_code_gen):
            f.content += subscriber_class_code_gen
            f.content += ' len_of_dict = {'
            for k, v in len_of_dict.iteritems():
                f.content += '\'' + k + '\':\'' + v + '\','
            f.content += '}\n'



if __name__ == '__main__':
    # Read request message from stdin
    data = sys.stdin.read()

    # Parse request
    request = plugin.CodeGeneratorRequest()
    request.ParseFromString(data)

    # Create response
    response = plugin.CodeGeneratorResponse()

    # Generate code
    generate_code(request, response)

    # Serialise response message
    output = response.SerializeToString()

    # Write to stdout
    sys.stdout.write(output)
