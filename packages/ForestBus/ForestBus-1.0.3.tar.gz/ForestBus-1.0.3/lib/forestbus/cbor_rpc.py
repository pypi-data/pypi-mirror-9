"""
The cbor_rpc module provides a multi-thread safe client API for making RPC calls encoded with CBOR.  The RPC protocol supported is that defined by Go (see http://golang.org/pkg/net/rpc/), encoded with the CBOR (see http://cbor.io) codec.  This package is used internally by the Forest Bus client.
"""

import cbor
import threading
import io
import socket

RpcIOException = Exception ("Connection failed while waiting for RPC response")
""" RpcIOException is thrown by Call when the connection to the RPC server failed before recieving a response."""

class _Response:
	"""
	An internal Response class used by the library to hold an outstanding RPC call and capture the result of the call.
	"""
	def __init__ (self, id):
		self.id = id
		self.cond = threading.Condition()
		self.receivedResponse = False
		self.linkBroken = False
		self.response = None
		self.errorMsg = None

	def getResponse (self):
		self.cond.acquire()
		# Double check to see if we already have a response before waiting
		if not self.receivedResponse:
			self.cond.wait()
		self.cond.release()
		# If the link is broken, raise an exception.
		if self.linkBroken:
			raise RpcIOException
		return (self.response, self.errorMsg)

	def setReponse (self, errorMsg, result):
		self.cond.acquire()
		self.response = result
		self.errorMsg = errorMsg
		self.receivedResponse = True
		self.cond.notify()
		self.cond.release()

	def setIOError (self):
		self.cond.acquire()
		self.receivedResponse = True
		self.linkBroken = True
		self.cond.notify()
		self.cond.release()



class Client:
	"""
	The RPC Client object wraps an existing socket connection and provides an RPC interface.  This is used by the forest.Client class to establish connections to each node in the cluster as required.

	The RPC protocol consists of sending two objects to make an RPC call:

 * A header object: {"ServiceMethod": "service.method", "Seq": sequenceNumber} where the service.method is the name of the service being called and sequenceNumber is a 64 bit number that is unique to this TCP session.
 * The parameters object required by the service.

The RPC response also consists of two objects:
 * A response object: {"ServiceMethod": "service.method", "Seq": sequenceNumber, "Error": errorMsg}.  The sequenceNumber is used to relate this RPC response to the call that was made and allows for multiple calls to be interleaved and returned in any order.  The Error field is an empty string for a successful call, or the error message if one occured.
 * The response object returned by the service.  This will be sent even if Error is not empty, although values in the response object may not have been populated depending on the error.

	"""
	def __init__ (self, connection):
		""" Create a Client using the given socket connection. """
		self._Closed = True
		self._Connection = connection
		self._Lock = threading.Lock()
		#self._Reader = io.BufferedReader (connection)
		#self._Writer = io.BufferedWriter (connection)
		fileobj = connection.makefile(mode='rwb')
		self._Reader = fileobj
		self._Writer = fileobj
		self._InFlightCalls = {}
		self._RPCIndex = 1
		self._Closed = False

		# Start a thread to manage reading responses
		self._ReadThread = threading.Thread (target = self.ReadResponses)
		self._ReadThread.start()

	def Call (self, serviceName, args):
		"""
		Call sends the RPC request to the serviceName given and with the given args object.

		This method is multi-thread safe and will block until there is either an error or a response from the service.

		Exceptions can be thrown if the client object does not have a connection to the RPC server.
		"""
		self._Lock.acquire()
		if self._Closed:
			self._Lock.release()
			raise Exception ("Client connection closed.")
		# Write the RPC header out
		cbor.dump({"ServiceMethod": serviceName, "Seq": self._RPCIndex}, self._Writer)
		# Now write out the arguments
		cbor.dump(args, self._Writer)
		resp = _Response(self._RPCIndex)
		self._InFlightCalls[self._RPCIndex] = resp
		self._RPCIndex += 1
		self._Writer.flush()
		self._Lock.release()
		# Wait on the reader notifying us that this call has completed.
		return resp.getResponse()

	def Close (self):
		"""
		Close shutsdown the RPC client.  This closes the wrapped connection, which triggers the end of the recieve thread and notifies any outstanding RPC client calls of the failure to complete. 
		"""
		self._Lock.acquire()
		self._Closed = True
		self._Connection.shutdown(socket.SHUT_RDWR)
		self._Connection.close()
		self._Lock.release()

	def ReadResponses (self):
		"""
		The ReadResposnes method is called automatically by the library to handle incoming RPC responses.  These will be handed off to the correct calling thread.  When the Client is closed or the socket connection fails any outstanding requests are notified of their failure.
		"""
		running = True
		while (running):
			# Get a response header
			try:
				resp = cbor.load (self._Reader)
				reply = cbor.load (self._Reader)
			except:
				running = False

			if running:
				self._Lock.acquire()
				waitingResponse = self._InFlightCalls[resp["Seq"]]
				del self._InFlightCalls[resp["Seq"]]
				self._Lock.release()
				waitingResponse.setReponse(resp["Error"], reply)
		# Tell any waiting clients that we have an exception
		self._Lock.acquire()
		self._Closed = True
		for seq in self._InFlightCalls:
			waitingResponse = self._InFlightCalls[seq]
			waitingResponse.setIOError()
		self._InFlightCalls = {}
		self._Lock.release()

		



