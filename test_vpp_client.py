# Copyright 2015, Google Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""The Python implementation of the gRPC route guide client."""

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
  result = stub.cli_inband(vpe_pb2.cli_inband_request(cmd = cmd, length=len(cmd)))
  print(len(result.reply))
  print(bytearray(result.reply).decode().rstrip('\0x00'))

def run():
  channel = grpc.insecure_channel('localhost:50051')
  stub = vpe_pb2_grpc.vpeStub(channel)
  print("-------------- show version --------------")
  vpp_show_version(stub)
  create_loopback(stub)
  cli_inband(stub, "show run")

if __name__ == '__main__':
  run()
