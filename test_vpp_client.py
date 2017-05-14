"""The Python test client VPP gRPC server"""

from __future__ import print_function

import grpc

import vpe_pb2
import vpe_pb2_grpc

def vpp_show_version(stub):
  version = stub.show_version(vpe_pb2.show_version_request())
  print('VPP version =', bytearray(version.version).decode().rstrip('\0x00'))
  print('VPP program =', bytearray(version.program).decode().rstrip('\0x00'))
  print('VPP build date =', bytearray(version.build_date).decode().rstrip('\0x00'))
  print('VPP build dir =', bytearray(version.build_directory).decode().rstrip('\0x00'))

def prettify(mac_string):
  return ':'.join('%02x' % ord(b) for b in mac_string)

def create_loopback(stub):
  mac_address="00:45:36:45:F2:00".replace(':', '').decode('hex')
  print("Creating loopback with mac:",prettify(mac_address))
  result = stub.create_loopback(vpe_pb2.create_loopback_request(mac_address=mac_address))
  print('loopback created')
  print(result)

def cli_inband(stub, cmd):
  result = stub.cli_inband(vpe_pb2.cli_inband_request(cmd = cmd))
  print(bytearray(result.reply).decode().rstrip('\0x00'))

def run():
  channel = grpc.insecure_channel('localhost:50052')
  stub = vpe_pb2_grpc.vpeStub(channel)
  print("-------------- show version --------------")
  vpp_show_version(stub)
  create_loopback(stub)
  cli_inband(stub, "show run")

if __name__ == '__main__':
  run()
