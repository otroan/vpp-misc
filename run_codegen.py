"""Runs json2proto3 for vpp apis and protoc with the gRPC plugin to generate messages and gRPC stubs."""

import os
import fnmatch
from grpc_tools import protoc
import json2proto3
import re


# create build dir
build_directory = 'build'
if not os.path.exists(build_directory):
        os.makedirs(build_directory)

results = []
protos = []
for root, dirs, files in os.walk('api'):
    for _file in files:
        if fnmatch.fnmatch(_file, '*.api.json'):
            results.append(os.path.join(root, _file))
            protos.append(re.sub('.api.json', '.proto', _file))

# generate protos
for api_json in results:
    json2proto3.vppprotogen(
        (
         '--services',
         '--proto-out','build',
         api_json,
         )
          )

os.chdir('build')
for proto_file in protos:
    # compile protos
    protoc.main(
        (
            '',
            '-I.',
            '--python_out=.',
            '--grpc_python_out=.',
            proto_file,
        )
         )
    protoc.main(
        (
            '',
            '-I.',
            '--grpc_out=.',
            '--plugin=protoc-gen-grpc=/usr/local/bin/grpc_cpp_plugin',
            proto_file,
        )
         )
    protoc.main(
        (
            '',
            '-I.',
            '--plugin=protoc-gen-custom=../codegen_vpp_grpc_relay.py',
            '--custom_out=.',
            proto_file,
        )
         )
