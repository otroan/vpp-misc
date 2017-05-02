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
