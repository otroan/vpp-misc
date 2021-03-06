from concurrent import futures
import time
import fnmatch
import grpc
import os
import re
import sys
import inspect
import types
sys.path.append('./build')

from vpp_papi import VPP

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

notifactions_db = {}
def relay_server_register_event_callback(msg_name, obj, callback):
    notifactions_db[msg_name] = [obj,callback]

def grpcmsg_to_namedtuple(obj, len_of_dict, subscribe=False):
  pr = {}
  if subscribe:
      pr["pid"] = os.getpid()
  for i in obj.DESCRIPTOR.fields:
    value = getattr(obj, i.name)
    if not i.name in ["_vl_msg_id", "context", "client_index","grpc_target"]:
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
   
def vppmsg_to_namedtuple(obj, grpc_module_name):
  pr = {}
  for name,value in obj.__dict__.iteritems():
    if not name.startswith('_'):
      #print(name, value, type(value))
      if isinstance(value, list) and getattr(value[0], '__module__', None) == "vpp_papi":
        #if isinstance(value, list) and inspect.isclass(value[0]):
        #convert from vpp_papi to grpc_module_name
        new_value = []
        for element in value:
            new_value.append(getattr(grpc_module_name, element.__class__.__name__)
                             (**vppmsg_to_namedtuple(element,grpc_module_name)))
        #print(type(new_value[0]))
        pr[name] = new_value
      elif getattr(value, '__module__', None) == "vpp_papi":
        #elif inspect.isclass(value):
        #convert from vpp_papi to grpc_module_name
        new_value = getattr(grpc_module_name, value.__class__.__name__)(**vppmsg_to_namedtuple(value,grpc_module_name))
        #print(type(new_value))
        pr[name] = new_value
      else:
        pr[name] = value
  return pr

results = []

for root, dirs, files in os.walk('build'):
    sys.path.append(root)
    for _file in files:
        if fnmatch.fnmatch(_file, '*.proto.py'):
            results.append(re.sub('.proto.py','',_file))
            exec(compile(source=open(os.path.join(root, _file)).read(), filename=_file, mode='exec'))
print(results)


def publish_events(msgname, result):
    print('VPP relay server received event %s from VPP' % msgname)
    if msgname in notifactions_db:
        getattr(notifactions_db[msgname][0],notifactions_db[msgname][1])(msgname, result)


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
      subscriber_servicer = service_name + '_subscribeServicer'
      subscribe_defined = False
      try:
        if getattr(module,subscriber_servicer):
            #print(" %s found %s" % (subscriber_servicer, module_name))
            subscribe_defined = True
      except AttributeError:
          #print( "%s not found" % subscriber_servicer)
          pass
      if subscribe_defined:
            add_servicer = 'add_' + service_name + '_subscribeServicer_to_server'
            getattr(module, add_servicer)(globals()[subscriber_servicer](vpp), server)
  vpp.register_event_callback(publish_events)
  print(notifactions_db)
                                          
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
