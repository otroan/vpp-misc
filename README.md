# vpp-misc
gRPC python relay server to VPP. 
This repo will contain script to autogenerate gRPC proto3 messages from VPP .api(.json), 
custom plugin to protoc to autogenerate servicer class definition, relay server, test gRPC client..

## To run this..

1.pip install grpcio grpcio_tools 
2.python run_codegen.py
3.Start vpp
4.Start gRPC relay server: python vpp_relay_server.py
5.Run test grpc vpp client: python test_vpp_client.py



Setting up python virtual env with vpp:
From : https://wiki.fd.io/view/VPP/Python_API

sudo apt-get install python-virtualenv
 
export VPP=~vpp/
cd $VPP
 
# build vpp
make bootstrap build
 
# create virtualenv
virtualenv virtualenv
 
virtualenv/bin/pip install cffi futures grpc grpcio grpcio_tools
virtualenv/bin/pip install ipaddress
virtualenv/bin/pip install scapy
 
# install vpp python api
pushd $VPP/src/vpp-api/python/
$VPP/virtualenv/bin/python setup.py install
popd
 
# Now set the LD_LIBRARY_PATH such that it points to the directory containing libpneum.so
export LD_LIBRARY_PATH=`find $VPP -name "libpneum.so" -exec dirname {} \; | head -n 1`
 
# You will now need two windows :
# one for vpp, and the other for python
 
# VPP
cd $VPP
make run
 
# python
# (as root, as vpp.connect() requires root privileges)
# Note that sudo cannot not preserve LD_LIBRARY_PATH
cd $VPP
 
# you can run a relay server
# cd to the location of this repo 
sudo -E LD_LIBRARY_PATH=$LD_LIBRARY_PATH $VPP/virtualenv/bin/python vpp_relay_server.py
 
