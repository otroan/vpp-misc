from concurrent import futures
import time
import fnmatch
import grpc
import os
from google.protobuf import descriptor

import vpe_pb2
import vpe_pb2_grpc
from vpp_papi import VPP

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

def grpcmsg_to_namedtuple(obj):
  pr = {}
  for i in obj.DESCRIPTOR.fields:
    value = getattr(obj, i.name)
    if not i.name in ["_vl_msg_id", "context", "client_index"]:
      if i.type == 12: #repeated bytes
        pr[i.name] = bytes(bytearray(value))
      else:
        pr[i.name] = value
      #print (' %s: %s = %s' % (i.type, i.name, pr[i.name]))
  return(pr)
   
def vppmsg_to_namedtuple(obj):
  pr = {}
  for name,value in obj.__dict__.iteritems():
    if not name.startswith('_'):
      pr[name] = value
  return pr

exec(compile(source=open('vpe.proto.py').read(), filename='vpe.proto.py', mode='exec'))

def serve():
  # directory containing all the json api files.
  # if vpp is installed on the system, these will be in /usr/share/vpp/api/
  vpp_json_dir = os.environ['VPP'] + '/build-root/install-vpp_debug-native/vpp/share/vpp/api/core'

  # construct a list of all the json api files
  jsonfiles = []
  for root, dirnames, filenames in os.walk(vpp_json_dir):
      for filename in fnmatch.filter(filenames, '*.api.json'):
          jsonfiles.append(os.path.join(vpp_json_dir, filename))

  if not jsonfiles:
      print('Error: no json api files found')
      exit(-1)

  vpp = VPP(jsonfiles)

  r = vpp.connect("grpc_relay_server")
  print(r)

  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  vpe_pb2_grpc.add_vpeServicer_to_server(
      vpeServicer(vpp), server)
  server.add_insecure_port('[::]:50051')
  server.start()
  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except KeyboardInterrupt:
    server.stop(0)
  exit(vpp.disconnect())

if __name__ == '__main__':
  serve()
