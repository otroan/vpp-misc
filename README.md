# vpp-misc
gRPC python relay server to VPP. 
This repo will contain script to autogenerate gRPC proto3 messages from VPP .api(.json), 
custom plugin to protoc to autogenerate servicer class definition, relay server, test gRPC client..

## To run this..

- pip install grpcio grpcio_tools
- python run_codegen.py
- Start vpp
- Start gRPC relay server  vpp_relay_server.py: after setting up vpp follow [Setting up python virtual env with vpp]
- Run test grpc vpp client: python test_vpp_client.py

### If you want to generate other language bindings..

Install grpc that brings in the language specific plugins:
```sh
- git clone https://github.com/grpc/grpc.git
- git submodule update --init
- sudo apt-get install pkg-config
- make
- sudo make install
- cd grpc/third_party/protobuf
- make
- sudo make install
```
Modify run_codegen.py to create additional language bindings using the protoc plugin for the desired language.

***

## Setting up python virtual env with vpp:
From : https://wiki.fd.io/view/VPP/Python_API
```sh
sudo apt-get install python-virtualenv
export VPP=~vpp/
cd $VPP
``` 
### build vpp
```sh
make bootstrap build
```
### create virtualenv
```sh
virtualenv virtualenv
 
virtualenv/bin/pip install cffi futures grpc grpcio grpcio_tools
virtualenv/bin/pip install ipaddress
virtualenv/bin/pip install scapy
``` 
### install vpp python api
```sh
pushd $VPP/src/vpp-api/python/
$VPP/virtualenv/bin/python setup.py install
popd
```
### Now set the LD_LIBRARY_PATH such that it points to the directory containing libpneum.so
```
export LD_LIBRARY_PATH=`find $VPP -name "libpneum.so" -exec dirname {} \; | head -n 1`
``` 
### You will now need two windows :
One for vpp, and the other for python
 
#### VPP
```sh
cd $VPP
make run
```
#### Run VPP GRPC relay server
```sh
# python
# (as root, as vpp.connect() requires root privileges)
# Note that sudo cannot not preserve LD_LIBRARY_PATH
# you can run a relay server
# cd to the location of this repo 
sudo -E LD_LIBRARY_PATH=$LD_LIBRARY_PATH $VPP/virtualenv/bin/python vpp_relay_server.py
``` 
