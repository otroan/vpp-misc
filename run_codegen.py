"""Runs json2proto3 for vpp apis and protoc with the gRPC plugin to generate messages and gRPC stubs."""

import os
import fnmatch
from grpc_tools import protoc
import json2proto3
import re
import sys

def find_executable(executable, path=None):
    """Find if 'executable' can be run. Looks for it in 'path'
    (string that lists directories separated by 'os.pathsep';
    defaults to os.environ['PATH']). Checks for all executable
    extensions. Returns full path or None if no command is found.
    """
    if path is None:
        path = os.environ['PATH']
    paths = path.split(os.pathsep)
    extlist = ['']
    if os.name == 'os2':
        (base, ext) = os.path.splitext(executable)
        # executable files on OS/2 can have an arbitrary extension, but
        # .exe is automatically appended if no dot is present in the name
        if not ext:
            executable = executable + ".exe"
    elif sys.platform == 'win32':
        pathext = os.environ['PATHEXT'].lower().split(os.pathsep)
        (base, ext) = os.path.splitext(executable)
        if ext.lower() not in pathext:
            extlist = pathext
    for ext in extlist:
        execname = executable + ext
        if os.path.isfile(execname):
            return execname
        else:
            for p in paths:
                f = os.path.join(p, execname)
                if os.path.isfile(f):
                    return f
    else:
	return None


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
cpp_plugin = find_executable('grpc_cpp_plugin')
go_plugin = find_executable('protoc-gen-go')
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
    if cpp_plugin:
    	protoc.main(
        	(
            	'',
            	'-I.',
            	'--grpc_out=.',
            	'--plugin=protoc-gen-grpc='+cpp_plugin,
            	proto_file,
        	)
         	)
    if go_plugin:
    	protoc.main(
        	(
            	'',
            	'-I.',
            	'--go_out=.',
            	'--plugin=protoc-gen-go='+go_plugin,
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
