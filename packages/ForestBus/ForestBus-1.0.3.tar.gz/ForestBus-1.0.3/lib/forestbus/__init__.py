"""
The forestbus package provides a Python client API for connecting to a Forest Bus cluster.

Connections are made using CBOR encoded RPC calls over TCP.  The nodes in the cluster must be started with the -cbor flag to enable connections from Python.

To connect to a Forest Bus cluster create an instance of the forest.Client class.  This class will in turn create instances of cbor_rpc.Client as required.

"""

__version__ = "1.0.3"

