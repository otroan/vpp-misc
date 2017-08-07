"""The Python test client VPP gRPC server"""

from __future__ import print_function
from concurrent import futures
from argparse import ArgumentParser

import grpc
import socket
import sys
sys.path.append('./build')
print(sys.path)

import vpe_pb2
import vpe_pb2_grpc
import interface_pb2
import interface_pb2_grpc
from  prettytable import PrettyTable
import time

test_server = "localhost"
test_server_port = "50052"
test_local_port = "50053"
_ONE_DAY_IN_SECONDS = 60 * 60 * 24

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
  channel = grpc.insecure_channel(test_server + ':'+test_server_port)
  stub = vpe_pb2_grpc.vpeStub(channel)
  vpp_show_version(stub)
  create_loopback(stub)
  cli_inband(stub, "show run")
  interface_stub = interface_pb2_grpc.interfaceStub(channel)
  show_interface(interface_stub)

  # Subscribe to interface stats

  subscriber_stub = vpe_pb2_grpc.vpe_subscribeStub(channel)
  s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  s.connect((test_server, int(test_server_port)))
  grpc_target = s.getsockname()[0] + ':' + test_local_port
  s.close()
  print(grpc_target)
  s
  subscriber_stub.want_stats(vpe_pb2.want_stats_request(enable_disable=1,
                                                        grpc_target=grpc_target))

class vpeNotificationServicer(vpe_pb2_grpc.vpe_notificationsServicer):
  def vnet_interface_counters_notification(self, request, context):
    print(request)
    return vpe_pb2.vpe_vpp_notification_ack(ack=1)
  
if __name__ == '__main__':
  parser = ArgumentParser()
  parser.add_argument("-s", "--server", help="vpp relay server address",
                        )
  parser.add_argument("-p", "--port", help="vpp relay server port",
                        )
  parser.add_argument("-l", "--local_port", help="local port to receive notifications over grpc",
                        )
  args = parser.parse_args()
  if args.server:
    test_server = args.server
  if args.port:
    test_server_port = args.port
  if args.local_port:
    test_local_port = args.local_port

  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  vpe_pb2_grpc.add_vpe_notificationsServicer_to_server(
    vpeNotificationServicer(), server)
  server.add_insecure_port('[::]:'+test_local_port)
  server.start()
  run()
  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except KeyboardInterrupt:
    server.stop(0)