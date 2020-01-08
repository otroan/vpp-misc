# Table of contents
[ACL Based Forwarding](#acl-based-forwarding)  
[ACLs for Security Groups](#acls-for-security-groups)  
[Address Resolution Protocol](#address-resolution-protocol)  
[Adjacency](#adjacency)  
[Bidirectional Forwarding Detection (BFD)](#bidirectional-forwarding-detection-(bfd))  
[Bit Indexed Explicit Replication](#bit-indexed-explicit-replication)  
[Bonding](#bonding)  
[Buffer Metadata Change Tracker (mdata)](#buffer-metadata-change-tracker-(mdata))  
[Builtin URL support for the static http/https server (builtinurl)](#builtin-url-support-for-the-static-http/https-server-(builtinurl))  
[Data-Plane Objects](#data-plane-objects)  
[Dynamic Host Configuration Protocol (DHCP)](#dynamic-host-configuration-protocol-(dhcp))  
[GTPU](#gtpu)  
[Generic Routing Encapsulation](#generic-routing-encapsulation)  
[IP Neighbour Database](#ip-neighbour-database)  
[IP Security](#ip-security)  
[IP in IP tunnelling](#ip-in-ip-tunnelling)  
[IPFIX probe](#ipfix-probe)  
[IPSec crypto engine provided by Intel IPSecMB library](#ipsec-crypto-engine-provided-by-intel-ipsecmb-library)  
[IPSec crypto engine provided by Openssl library](#ipsec-crypto-engine-provided-by-openssl-library)  
[IPSec crypto engine provided by native implementation](#ipsec-crypto-engine-provided-by-native-implementation)  
[IPv6 Neeighbour Discovery](#ipv6-neeighbour-discovery)  
[Internet Group Management Protocol](#internet-group-management-protocol)  
[LB](#lb)  
[Layer 2 Forwarding (L2)](#layer-2-forwarding-(l2))  
[Layer 3 cross connect](#layer-3-cross-connect)  
[Link Aggregation Control Protocol (LACP)](#link-aggregation-control-protocol-(lacp))  
[Link Layer Discovery Protocol (LLDP)](#link-layer-discovery-protocol-(lldp))  
[Locator/ID Separation Protocol (LISP) Control Plane](#locator/id-separation-protocol-(lisp)-control-plane)  
[Locator/ID Separation Protocol Generic Protocol Extension (LISP-GPE)](#locator/id-separation-protocol-generic-protocol-extension-(lisp-gpe))  
[Mapping of Address and Port (MAP)](#mapping-of-address-and-port-(map))  
[Multi-Protocol Label Switching](#multi-protocol-label-switching)  
[NSH](#nsh)  
[Netmap Device](#netmap-device)  
[Network Address Translation (NAT)](#network-address-translation-(nat))  
[Network Delay Simulator](#network-delay-simulator)  
[PPPoE](#pppoe)  
[Pipe Device](#pipe-device)  
[Quality of Service](#quality-of-service)  
[SRv6 Mobuile](#srv6-mobuile)  
[Session Layer](#session-layer)  
[Source VRF Select](#source-vrf-select)  
[Static http/https server (http_static)](#static-http/https-server-(http_static))  
[Tap Device](#tap-device)  
[Time-range-based MAC-address filter (mactime)](#time-range-based-mac-address-filter-(mactime))  
[Transmission Control Protocol (TCP)](#transmission-control-protocol-(tcp))  
[Transport Layer Security (TLS)](#transport-layer-security-(tls))  
[User Datagram Protocol (UDP)](#user-datagram-protocol-(udp))  
[VPP Comms Library (VCL)](#vpp-comms-library-(vcl))  
[Virtio PCI Device](#virtio-pci-device)  
[Virtual eXtensible LAN (VXLAN)](#virtual-extensible-lan-(vxlan))  
[VxLAN-GPE](#vxlan-gpe)  
[host-interface Device (AF_PACKET)](#host-interface-device-(af_packet))  
[rdma device driver](#rdma-device-driver)  
[vmxnet3 device driver](#vmxnet3-device-driver)  

# ACL Based Forwarding
- Policy Based Routing
- ACLs match traffic to be forwarded
- Each rule in the ACL has an associated 'path' which determines how the traffic will be forwarded. This path is described as a FIB path, so anything possible with basic L3 forwarding is possible with ABF (with the exception of output MPLS labels)
- ACLs are grouped into a policy
- ACL priorities within the policy determine which traffic is preferentially matched
- Policies are attached to interfaces.
- ABF runs as an input feature in the L3 path

ACL Based Forwarding

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# ACLs for Security Groups
- Inbound MACIP ACLs
  - filter the source IP:MAC address statically configured bindings
- Stateless inbound and outbound ACLs
  - permit/deny packets based on their L3/L4 info
- Stateful inbound and outbound ACLs
  - create inbound sessions based on outbound traffic and vice versa

The ACL plugin allows to implement access control policies
at the levels of IP address ownership (by locking down
the IP-MAC associations by MACIP ACLs), and by using network
and transport level policies in inbound and outbound ACLs.
For non-initial fragments the matching is done on network
layer only. The session state in stateful ACLs is maintained
per-interface (e.g. outbound interface ACL creates the session
while inbound ACL matches it), which simplifies the design
and operation. For TCP handling, the session processing
tracks "established" (seen both SYN segments and seen ACKs for them),
and "transient" (all the other TCP states) sessions.

Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# Address Resolution Protocol
- ARP responder

ARP

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Adjacency
- An adjacency represents how to send different traffic types to a peer
- The principles properties of an adjacency are the interface and rewrite. The rewrite will be prepended to the packet as it is forward through the interface.
- The rewrite is provided either by the interface type. It can be constructed either from fixed interface properties (i.e. src,dst IP address on a P2P tunnel) or from a resolution protocol (like ARP on an Ethernet link).
- An Adjacency is said to be complete when the rewrite is present and incomplete when it is not,
- An adjacency that is a leaf in the DPO graph is terminal/normal (i.e on a physical interface). When not terminal it is termed a midchain (i.e. one on a virtual interface, e.g. GRE tunnel). Midchain adjacencies can be stacked/joined onto the the DPO graph that described subsequent forwarding (i.e. how to send the the GRE tunnel's destination address).
- Glean adjacencies describe how to broadcast packets onto a subnet

Adjacency

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Bidirectional Forwarding Detection (BFD)
- BFD protocol implementation

Bidirectional Forwarding Detection implementation

Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# Bit Indexed Explicit Replication
- Multicast Using Bit Index Explicit Replication (https://tools.ietf.org/html/rfc8279)
- Encapsulation for Bit Index Explicit Replication (BIER) in MPLS and Non-MPLS Networks (https://tools.ietf.org/html/rfc8296)

BIER

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Bonding
- Interface bonding support with the following options - mode active-backup - mode lacp - load-balance l2 | l23 | l34 - numa-only - mode xor - load-balance l2 | l23 | l34 - mode round-robin - mode broadcast

Bonding implementation

Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# Buffer Metadata Change Tracker (mdata)
- Buffer Metadata Change Tracker

Buffer Metadata Change Tracker
Uses the before / after graph node main loop performance
callback hooks to snapshoot buffer metadata, then
compare and summarize results per-node.
Answers the question "what buffer metadata does a particular
graph node change?" by direct observation.
Zero performance impact until enabled.

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Builtin URL support for the static http/https server (builtinurl)
- Builtin URLs for the static http/https server

Adds a set of URLs to the static http/https server. Current URLs, all of which return data in .json fmt: <root-url>/version.json - vpp version info <root-url>/interface_list.json - list of interfaces <root-url>/interface_stats - single interface via HTTP POST <root-url>/interface_stats - all intfcs via HTTP GET.

Feature maturity level: development  
Supports: API CLI MULTITHREAD  
# Data-Plane Objects
- A DPO is a generic term (a.k.a abstract base class) for objects that perform [a set of] actions on packets in the data-plane
- Concrete examples of DPO types are; adjacency, mpls-imposition, replication.
- DPOs are stacked/joined to form a processing graph that packets traverse to describe the full set of actions a packet should experience.
- DPO graphs can be rooted at any point in the VLIB graph - notable examples are L3 FIB lookup, ABF, L3XC.

DPO

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Dynamic Host Configuration Protocol (DHCP)
- DHCP client (v4/v6)
- DHCPv6 prefix delegation
- DHCP Proxy / Option 82

DHCP client

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# GTPU
- GTPU decapsulation
- GTPU encapsulation

GPRS Tunnelling Protocol

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Generic Routing Encapsulation
- L3 tunnels, all combinations of IPv4 and IPv6
- Encap/Decap flags to control the copying of DSCP, ECN, DF from overlay to underlay and vice-versa.
- L2 tunnels
Not yet implemented:
  - GRE keys

GRE

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# IP Neighbour Database
- IP protocol independent Database of Neighbours (aka peers)
- limits on number of peers, recycling and aging

IP-neighbor

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# IP Security
- IPSec (https://tools.ietf.org/html/rfc4301)
- Authetication Header (https://tools.ietf.org/html/rfc4302)
- Encapsulating Security Payload (https://tools.ietf.org/html/rfc4303)

IPSec

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# IP in IP tunnelling
- IPv4/IPv6 over IPv4/IPv6 encapsulation
  - Fragmentation and Reassembly
  - Configurable MTU
  - Inner to outer Traffic Class / TOS copy
  - Configurable Traffic Class / TOS
- ICMPv4 / ICMPv6 proxying
- 6RD (RFC5969)
  - Border Relay

Implements IP{v4,v6} over IP{v4,v6} tunnelling as
described in RFC2473. This module also implements the
border relay of 6RD (RFC5969).

Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
Not yet implemented:
  - Tunnel PMTUD
  - Tracking of FIB state for tunnel state
  - IPv6 extension headers (Tunnel encapsulation limit option)
# IPFIX probe
- L2 input feature
- IPv4 / IPv6 input feature
- Recording of L2, L3 and L4 information

IPFIX flow probe. Works in the L2, or IP input feature path.

Not yet implemented:
  - Output path
  - Export over IPv6
  - Export over TCP/SCTP
Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# IPSec crypto engine provided by Intel IPSecMB library
- SHA(1, 224, 256, 384, 512)
- CBC(128, 192, 256)
- GCM(128, 192, 256)

IPSecMB crypto-engine

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# IPSec crypto engine provided by Openssl library
- SHA(1, 224, 256, 384, 512)
- CBC(128, 192, 256)
- GCM(128, 192, 256)
- CTR(128, 192, 256)
- DES, 3DES
- MD5

openssl crypto-engine

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# IPSec crypto engine provided by native implementation
- CBC(128, 192, 256)
- GCM(128, 192, 256)

native crypto-engine

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# IPv6 Neeighbour Discovery
- Nieghbour discovery.
- ND Auto address configuration
- Multicast Listener Discovery - only as host role to send adverts
- Router Advertisements

IPv6-ND

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Internet Group Management Protocol
- IGMPv3 only.

IGMP

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# LB
- GRE tunnel mode
- NAT mode
- L3DSR mode
- Consistent Hash
- Connection Track

Load Balancer

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Layer 2 Forwarding (L2)
- L2 Cross-connect (xconnect) of two interfaces
- L2 Bridging of multiple interfaces in a bridge domain (BD)
  - Forwarding via destination MAC address of packet
  - MAC learning enable/disable on BD or per interface
  - MAC aging with specified aging interval enable/disable
  - MAC flush of learned MACs on interface down, BD deletion, or by user
  - User added static MACs not subject to aging nor overwritten by MAC learn
  - User added MACs not subject to aging but can be overwritten by MAC learn
  - Unicast forwarding enable/disable
  - Unknown unicast flooding enable/disable
  - Multicast/broadcast flooding enable/disable
  - ARP-termination to avoid flooding of ARP requests
  - Enable/disable unicast of ARP requests instead of flooding
  - BVI (Bridge Virtual Interface) for IP forwarding from or to BD
  - Set interface in BD to send unknown unicast packets instead of flooding
  - Support of split horizon group (SHG) on BD interfaces
- VLAN tag rewrite on L2 bridging or xconnect interfaces

Layer 2 Bridging and Cross-Connect Support

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Layer 3 cross connect
- cross connect all ingress traffic on an L3 interface to an output FIB path.
- the path can describe any output (with the exception of MPLS labels)
- The same functions can be acheived by using a dedicated VRF for the table and adding a default route with the same path. However, the L3XC is more efficient in memory and CPU

L3-xconnect

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Link Aggregation Control Protocol (LACP)
- Support LACP version 1 specification including marker protocol

Link Aggregation Control Protocol implementation

Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# Link Layer Discovery Protocol (LLDP)
- link layer discovery protocol implementation

Link Layer Discovery Protocol implementation

Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# Locator/ID Separation Protocol (LISP) Control Plane
- ITR, ETR and RTR mode of operation
- Multitenancy
- Multihoming
- Source/dest map-cache lookups
- RLOC-probing
- Support for Ethernet, IPv4, IPv6 and NSH EIDs (payloads)
- Map-resolver failover algorithm

LISP control plane implementation

Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# Locator/ID Separation Protocol Generic Protocol Extension (LISP-GPE)
- ITR, ETR and RTR modes
- Support for Ethernet, IPv4, IPv6 and NSH EIDs (payloads)
- Source/dest forwarding
- IPv4 and IPv6 RLOCs

LISP-GPE implementation

Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# Mapping of Address and Port (MAP)
- LW46 BR (RFC7596)
  - Fragmentation and Reassembly
- MAP-E BR (RFC7597)
- MAP-T BR (RFC7599)

IPv4 as a service mechanisms. Tunnel or translate an IPv4 address, an IPv4 subnet or a shared IPv4 address. In shared IPv4 address mode, only UDP, TCP and restricted ICMP is supported.

Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# Multi-Protocol Label Switching
- Label imposition/disposition - pipe and uniform mode
- Tunnels - unidirectional

MPLS

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# NSH
- NSH Classifier
- NSH Forwarder
- NSH SF
- NSH Proxy
- NSH OAM
- NSH Metadata

NSH for SFC

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Netmap Device
- L4 checksum offload

Create a netmap interface, which is a high speed user-space interface that allows VPP to patch into a linux namespace, a linux container, or a physical NIC without the use of DPDK.

Not yet implemented:
  - API dump
Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# Network Address Translation (NAT)
- NAT44
  - 1:1 NAT
  - 1:1 NAT with ports
  - VRF awareness
  - Multiple inside interfaces
  - Hairpinning
  - IPFIX
  - Syslog
  - Endpoint dependent NAT
  - TCP MSS clamping
  - Local bypass (DHCP)
- CGN - deterministic NAT
- NAT64
- NAT66
- DS-lite
- 464XLAT

The NAT plugin offers a multiple address translation functions. These can be used in a raft of different scenarios. CPE, CGN, etc.

Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# Network Delay Simulator
- Network delay and loss fraction simulator

Introduces configurable network delay and loss

Feature maturity level: production  
Supports: CLI MULTITHREAD  
# PPPoE
- PPPoE Control Plane packet dispatch
- PPPoE decapsulation
- PPPoE encapsulation

PPP over Ethernet

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Pipe Device
- L4 checksum offload

Create a pipe device interface, which can pass packets bidirectionally in one side of the pipe to the other side of the pipe. While similar in behavior to a unix pipe, it is not a host-based pipe.

Not yet implemented:
  - does not use hw-address
  - does not support tagged traffic
  - API dump filtering by sw_if_index
Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# Quality of Service
- Record - extract QoS bits from packets headers and write in metadata
- Mapp - defines simple transform of QoS bits from/to each packet layer
- Mark - write [mapped] QoS bits into packet headers
- Store - write in packet metadata a fixed QoS value

QoS

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# SRv6 Mobuile
- GTP4.D
- GTP4.E
- GTP6.D
- GTP6.D.Di
- GTP6.E

SRv6 Mobile End Functions. GTP4.D, GTP4.E, GTP6.D, GTP6.D.Di and GTP6.E are supported.

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Session Layer
- Manages allocation and tracking of sessions (6-tuple lookup tables)
- App namespaces that constrain application access to network resources
- Conveys data and notifications (ctrl and io) between transport protocols and apps
- Transport protocol interface
  - Provides generic transport protocol template
  - Converts between transport and application representation of data
  - Schedules sessions/connections for sending
- Application interface
  - Maintains per application state
  - Manages allocation of shared memory resources used for exchanging data between applications and transports
  - Exposes a native C and a binary api for builtin and external apps respectively

The session layer facilitates the interaction between northbound applications and southbound transport protocols. To this end, northbound, through the app-interface sub layer, the session layer exposes APIs for applications to interact with abstract units of communication, i.e., sessions. And southbound, through the transport protocol interface, it exposes APIs that allow transport protocols to exchange data and events (ctrl and io) with applications, without actually being aware of how that communication is carried out.

Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# Source VRF Select
- Determine the input VRF/table based on the source IP address
- routes are added to tables.
- route lookup is performed using the packet's source address
- The route is programmed with the table in which the subsequent destination address lookup will be performed
- Tables are bound to interfaces.
- SVS runs as an input feature in the L3 path

Source VRF Select

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Static http/https server (http_static)
- An extensible static http/https server with caching

A simple caching static http / https server A built-in vpp host stack application. Supports HTTP GET and HTTP POST methods.

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Tap Device
- Virtio

Create a tap v2 device interface, which connects to a tap interface on the host system.

Not yet implemented:
  - API dump filtering by sw_if_index
Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# Time-range-based MAC-address filter (mactime)
- Static / time-range / data quota based MAC address filter

Device-input/output arc driver level MAC filter. Checks to see if traffic is allowed to/from the given MAC address, and takes the appropriate action. Intended for the home gateway use-case, where WAN traffic is billed per bit.

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Transmission Control Protocol (TCP)
- Core functionality (RFC793, RFC5681, RFC6691)
- Extensions for high performance (RFC7323)
- Congestion control extensions (RFC3465, RFC8312)
- Loss recovery extensions (RFC2018, RFC3042, RFC6582, RFC6675, RFC6937)
- Detection and prevention of spurious retransmits (RFC3522)
- Defending spoofing and flooding attacks (RFC6528)
- Partly implemented features (RFC1122, RFC4898, RFC5961)
- Delivery rate estimation (draft-cheng-iccrg-delivery-rate-estimation)

High speed and scale TCP implementation

Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# Transport Layer Security (TLS)
- Framework that supports pluggable TLS engines
- OpenSSL, Picotls and MbedTLS engines

TLS protocol implementation that consists of a set of engines that act as wrappers for existing TLS implementations, e.g., OpenSSL, Picotls and MbedTLS, and a framework that integrates the engines into VPP's host stack

Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# User Datagram Protocol (UDP)
- host stack integration via session layer
- standalone per port dispatcher for tunneling protocols

UDP implementation

Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# VPP Comms Library (VCL)
- Abstracts vpp host stack sessions to integer session handles
- Exposes its own async communication functions, i.e., epoll, select, poll
- Supports multi-worker applications
- Sessions cannot be shared between multiple threads/processes
- VCL Locked Sessions (VLS)
  - Ensure through locking that only one thread accesses a session at a time
  - Detects and registers forked processes as new VCL workers. It does not register threads as new workers.
- LD_PRELOAD shim (LDP)
  - Intercepts syscalls and injects them into VLS.
  - Applications that are supported work with VCL and implicitly with VPP's host stack without any code change
  - It does not support all syscalls and syscall options

VCL simplifies app interaction with session layer by exposing APIs that are similar to but not POSIX-compliant.

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# Virtio PCI Device
- connection to the emulated pci interface presented to vpp from the host interface.

Create a virtio-backed PCI device interface

Not yet implemented:
  - API dump filtering by sw_if_index
Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# Virtual eXtensible LAN (VXLAN)
- VXLAN tunnel for support of L2 overlay/virtual networks (RFC-7348)
- Support either IPv4 or IPv6 underlay network VTEPs
- Flooding via headend replication if all VXLAN tunnels in BD are unicast ones
- Multicast VXLAN tunnel can be added to BD to flood via IP multicast
- VXLAN encap with flow-hashed source port for better underlay IP load balance
- VXLAN decap optimization via vxlan-bypass IP feature on underlay interfaces
- VXLAN decap HW offload using flow director with DPDK on Intel Fortville NICs

VXLAN tunnels support L2 overlay networks that span L3 networks

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# VxLAN-GPE
- VxLAN-GPE decapsulation
- VxLAN-GPE encapsulation

VxLAN-GPE tunnel handling

Feature maturity level: production  
Supports: API CLI MULTITHREAD  
# host-interface Device (AF_PACKET)
- L4 checksum offload

Create a host interface that will attach to a linux AF_PACKET interface, one side of a veth pair. The veth pair must already exist. Once created, a new host interface will exist in VPP with the name 'host-<ifname>', where '<ifname>' is the name of the specified veth pair. Use the 'show interface' command to display host interface details.

Not yet implemented:
  - API dump details beyond sw_if_index and name
Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# rdma device driver
- rdma driver for Mellanox ConnectX-4/5 adapters

rdma device driver support

Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  
# vmxnet3 device driver
- vmxnet3 device driver to connect to ESXi server, VMWare Fusion, and VMWare Workstation

vmxnet3 device driver support

Feature maturity level: production  
Supports: API CLI STATS MULTITHREAD  

