from concurrent import futures
import time
import fnmatch
import grpc
import os
from google.protobuf import descriptor
import re
import sys

import vpe_pb2
import vpe_pb2_grpc
from vpp_papi import VPP

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

def grpcmsg_to_namedtuple(obj, len_of_dict):
  pr = {}
  for i in obj.DESCRIPTOR.fields:
    value = getattr(obj, i.name)
    if not i.name in ["_vl_msg_id", "context", "client_index"]:
      if i.type == 12: #repeated bytes
        pr[i.name] = str(bytearray(value))
        # if this is a variable len array, set the len field
        field_is_var_array = obj.DESCRIPTOR.name + '.' + i.name
        if field_is_var_array in len_of_dict:
          pr[len_of_dict[field_is_var_array]] = len(pr[i.name])
      else:
        pr[i.name] = value
      #print (' %s: %s = %s' % (i.type, i.name, pr[i.name]))
  return(pr)
   
def vppmsg_to_namedtuple(obj):
  pr = {}
  for name,value in obj.__dict__.iteritems():
    if not name.startswith('_'):
      pr[name] = value
      #print(name, value, type(value))
  return pr

results = []

for root, dirs, files in os.walk('build'):
    sys.path.append(root)
    for _file in files:
        if fnmatch.fnmatch(_file, '*.proto.py'):
            results.append(re.sub('.proto.py','',_file))
            exec(compile(source=open(os.path.join(root, _file)).read(), filename=_file, mode='exec'))
print(results)

def serve():
  # directory containing all the json api files.
  # if vpp is installed on the system, these will be in /usr/share/vpp/api/
  vpp_json_dir = os.environ['VPP'] + '/build-root/install-vpp_debug-native/vpp/share/vpp/api/core'
  vpp_plugins_json_dir = os.environ['VPP'] + '/build-root/install-vpp_debug-native/vpp/share/vpp/api/plugins'
  # construct a list of all the json api files

  jsonfiles = []
  for root, dirnames, filenames in os.walk(vpp_json_dir):
      for filename in fnmatch.filter(filenames, '*.api.json'):
          jsonfiles.append(os.path.join(vpp_json_dir, filename))

  for root, dirnames, filenames in os.walk(vpp_plugins_json_dir):
      for filename in fnmatch.filter(filenames, '*.api.json'):
          jsonfiles.append(os.path.join(vpp_plugins_json_dir, filename))

  if not jsonfiles:
      print('Error: no json api files found')
      exit(-1)

  vpp = VPP(jsonfiles)

  r = vpp.connect("grpc_relay_server")
  print(r)

  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  for service_name in results:
      module_name = service_name + '_pb2_grpc'
      module = __import__(module_name)
      add_servicer = 'add_'+service_name+'Servicer_to_server'
      init_servicer = service_name + 'Servicer'
      getattr(module, add_servicer) (globals()[init_servicer] (vpp), server)
                                          
  server.add_insecure_port('[::]:50052')
  server.start()
  try:
    while True:
      time.sleep(_ONE_DAY_IN_SECONDS)
  except KeyboardInterrupt:
    server.stop(0)
  exit(vpp.disconnect())

if __name__ == '__main__':
  serve()
