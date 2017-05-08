"""Runs json2proto3 for vpp apis and protoc with the gRPC plugin to generate messages and gRPC stubs."""

from grpc_tools import protoc
import json2proto3
 
json2proto3.vppprotogen(
    (
     '--services',
     'api/core/vpe.api.json',
     )
      )
protoc.main(
    (
	'',
	'-I.',
	'--python_out=.',
	'--grpc_python_out=.',
	'vpe.proto',
    )
     )
protoc.main(
    (
	'',
	'-I.',
	'--plugin=protoc-gen-custom=codegen_vpp_grpc_relay.py',
        '--custom_out=.',
	'vpe.proto',
    )
     )
