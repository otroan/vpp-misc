# Operational data segment


## Open issues

### Expose all of the internal data structure? Or copy only required pieces?

### Model. A "custom" YANG model? Just use .api language?

### "External" data providers?

## Keys

### Hierarchical. Mimicking a YANG path hierarchy.

### Directory implemented as hash

Any change to the hash must be protected by an optimistic lock.

### Do we need parts of xpath? E.g. how to represent individual list element?

## Values

### Opaque object. Semantics is based on data model

### Supported data structures

- Pools

- Vectors

- Single values (embedded in directory?)

## VPP API

### vppdb_create_node()

### vppdb_lock_node()

### vppdb_unlock_node()

## Client

### Client library and applications (Similar to stat_client.c) vpp_get_stats. Language bindings

### Notification mechanism

### Query interface

### FUSE overlay

- Keys as directories, values represented as JSON objects

## Architecture

### Shared memory segment. Read-only by client.

The shared memory segment is mounted at a different memory location from VPP. That requires all pointer accesses to be recalculated based on the different base address. This has to be done by the client.

### Optimistic locking

A benefit from optimistic locking is that there is no need for communication primitives between the server and client.  
  
The server updates epoch/in_progress flags and the client checks them. The scheme requires client to do copy out.  
  
The client might read garbage, so all reads must do boundary checking, e.g. if following pointers/offsets.  
  


- On write, set in_progress, when done bump epoch.

- On read, note epoch, when copied all data, check in_progress and epoch

### Single writer multiple readers

## Model

### Auto-generate .api or YANG from C typedef?

