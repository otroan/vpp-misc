"""The Python test client VPP gRPC server"""

from __future__ import print_function

import grpc

import sys
sys.path.append('./build')
print(sys.path)

import vpe_pb2
import vpe_pb2_grpc
import interface_pb2
import interface_pb2_grpc
from  prettytable import PrettyTable

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

def show_interface(stub):
  results = stub.sw_interface_dump(interface_pb2.sw_interface_dump_request())
  table = PrettyTable(["name", "sw-index", "state", "l2 address"])
  for sw_interface in results:
    table.add_row([bytearray(sw_interface.interface_name).decode().rstrip('\0x00'), sw_interface.sw_if_index, sw_interface.admin_up_down, prettify(sw_interface.l2_address)])
  print(table)
  
def run():
  channel = grpc.insecure_channel('localhost:50052')
  stub = vpe_pb2_grpc.vpeStub(channel)
  vpp_show_version(stub)
  create_loopback(stub)
  cli_inband(stub, "show run")
  interface_stub = interface_pb2_grpc.interfaceStub(channel)
  show_interface(interface_stub)
  
if __name__ == '__main__':
  run()
