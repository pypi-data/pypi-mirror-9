"""
The forest module provides an easy to use Python client API for interacting with a Forest Bus cluster.
"""

import cbor_rpc
import socket
import threading

ErrNoNodesAvailable = Exception ("No nodes available")
""" ErrNoNodesAvailable is thrown when the Client is not able to fulfill the request against any of the nodes in the cluster. """

ErrClusterIDMismatch = Exception ("ClusterID given doesn't match that used by the node")
""" ErrClusterIDMismatch is thrown if the nodes in the cluster have been configured with a different id to the one given when the Client is created. """

class Client:
	""" 
	The Client class provides a multi-thread safe connection to a Forest Bus cluster.  This class will establish connections to the nodes in the cluster as required.
	"""
	def __init__ (self, clusterID, nodes):
		"""
		Creates a new Client instance.  The clusterID will be checked against the -id that the Forest Bus nodes were started with.

		The nodes parameter is a list of strings in the format hostname:port and should match the -cbor parameter given when the nodes where started.
		"""
		self._clusterID = clusterID
		self._nodes = nodes

		self._connections = {}
		self._topic_leaders = {}
		self._lock = threading.Lock()
		self._lastUsedGetNodeName = ""

	def GetMessages (self, topic, index, quantity, wait):
		"""
		GetMessages takes the topic (a string), the index (a 64 bit integer), target quantity (integer) and a wait flag (boolean).  If wait is True then the method will block until new messages become available.

		GetMessages returns a tuple of the received messages (a list of sequence of bytes) and the index of the next message in this topic sequence.

		GetMessages will usually return more or fewer messages than the quantity requested.  This ensures effeicient message retrieval from the node as messages are aligned to offset and cache boundaries.  If any messages are available at the requested index then at least one message will be returned.

		If the index requested is no longer available on this node (i.e. clean-up has removed old data) then zero messages will be returned and the nextID will be the index of the first available message.

		If the messages returned bring the client up to the end of the available messages, the nextID will contain the index of what will become the next message when it has been sent.  By setting wait to True and passing in the index returned by nextID, GetMessages will block until at least one new message is available, before returning that message/messages.


		GetMessages throws Exceptions if no nodes are available, a network error occurs or the topic could not be found.  Even if an exception has been thrown - Client.Close() must be called to close down all threads.
		"""
		factory = self._rpcConnect()
		while (True):
			rpcClient = factory()
			if rpcClient is None:
				raise ErrNoNodesAvailable
			result, error = rpcClient.Call("RPCHandler.ReceiveMessages", {"ClusterID": self._clusterID, "Topic": topic, "ID": index, "Quantity": quantity, "WaitForMessages": wait})
			if error != "":
				raise Exception (error)

			return (result["ReceivedMessages"], result["NextID"])

	def GetTopicMaxAvailableIndex (self, topic):
		"""
		GetTopicMaxAvailableIndex returns the maximum available index from the currently connected node for the given topic.

		If the cluster has been completely shutdown and restarted (rather than a rolling restart of individual nodes) then the commit index may be zero, in which case the maxAvailableIndex will be zero.  Once a message has been sent to the cluster in this topic the commit index will be recalculated and the maximum commit index will return as normal.

		GetTopicMaxAvailableIndex throws Exceptions if no nodes are available, a network error occurs or the topic could not be found.  Even if an exception has been thrown - Client.Close() must be called to close down all threads.
		"""
		factory = self._rpcConnect()
		while (True):
			rpcClient = factory()
			if rpcClient is None:
				raise ErrNoNodesAvailable
			result, error = rpcClient.Call("RPCHandler.GetTopicDetails", {"Topic": topic})
			if error != "":
				self._removeBrokenConnection (rpcClient)
				raise Exception (error)

			return result["CommitIndex"]

	def SendMessages (self, topic, messages, waitForCommit):
		"""
		SendMessages sends a batch of messages to the Forest Bus cluster.

		Messages are a list of sequences of bytes.  Sending many messages (hundreds) at once gives better through-put than sending individual messages.

		If waitForCommit is false then SendMessages will return as soon as the message has been saved on the leader node for this topic.  If waitForCommit is true then SendMessages will only return once the messages have been replicated to a majority of the nodes in the cluster and are therefore committed.

		SendMessages throws Exceptions if no leader node is available, a network error occurs or the topic could not be found.  Even if an exception has been thrown - Client.Close() must be called to close down all threads.
		"""
		factory = self._rpcConnect(topic)
		while (True):
			rpcClient = factory()
			if rpcClient is None:
				raise ErrNoNodesAvailable
			result, error = rpcClient.Call("RPCHandler.SendMessages", {"Topic": topic, "SentMessages": messages, "WaitForCommit": waitForCommit})
			if error != "":
				self._removeBrokenConnection (rpcClient)
				raise Exception (error)

			if result["Result"]["Code"] == 0:
				# Success - send it back
				return result["IDs"]

	def Close (self):
		"""
		Close shutsdown the Forest Bus Client and closes all connections to the underlying nodes.

		A closed Client can be reused - new node connections will be established as required.
		"""
		#print ("Acquiring lock in close")
		self._lock.acquire()
		#print ("Looping through connections in close")
		for nodeName in self._connections:
			#print ("Closing connection " + nodeName + " close")
			self._connections[nodeName].Close()
		self._connections = {}
		self._lock.release()


	def _rpcConnect (self, topic = None):
		# Start with the last used connection
		lastUsed = 0
		self._lock.acquire()
		if topic is not None:
			# See if we have a last seen leader
			if topic in self._topic_leaders:
				lastSeenTopicLeader = self._topic_leaders[topic]
				lastUsed = self._nodes.index (lastSeenTopicLeader)
				#print ("Last seen leader " + str (lastSeenTopicLeader) + " is index " + str (lastUsed))
			else:
				# Just use the first one
				#print ("Topic not found, using 0")
				lastUsed = 0
		elif self._lastUsedGetNodeName != "":
			lastUsed = self._nodes.index (self._lastUsedGetNodeName)
		self._lock.release()

		ournodes = []
		for node in self._nodes:
			ournodes.append (node)
		# Prioritise the first one
		#print ("Nodes before sort: " + str (ournodes) + " lastUsed: " + str (lastUsed))
		if lastUsed != 0:
			ournodes[lastUsed], ournodes[0] = ournodes[0], ournodes[lastUsed]
		#print ("Nodes after sort: " + str (ournodes))
		lastTried = [0]

		def factory ():
			while lastTried[0] < len (ournodes):
				try:
					result = self._getConnection (ournodes[lastTried[0]])
					if result != None:
						self._lock.acquire()
						if topic is not None:
							self._topic_leaders[topic] = ournodes[lastTried[0]]
						else:
							self._lastUsedGetNodeName = ournodes[lastTried[0]]
						self._lock.release()
						lastTried[0] += 1
						return result
					else:
						lastTried[0] += 1
				except Exception, e:
					if e == ErrClusterIDMismatch:
						raise e
					lastTried[0] += 1

			return None
		return factory

	def _getConnection (self, nodeName):
		self._lock.acquire()
		if nodeName in self._connections:
			#print ("Returning existing connection to " + nodeName)
			result = self._connections[nodeName]
			self._lock.release()
		else:
			try:
				#sock = socket.socket()
				address = (nodeName[:nodeName.index(":")], int (nodeName[nodeName.index(":")+1:]))
				#print ("Trying to connect to " + str(address))
				#sock.connect(address)
				sock = socket.create_connection (address)
				result = cbor_rpc.Client (sock)

				# Check cluster IDs match
				response, err = result.Call("RPCHandler.GetClusterDetails", {})
				if err == "" and response["Result"]["Code"] == 0:
					if self._clusterID != response["ClusterID"]:
						result.Close()
						raise ErrClusterIDMismatch
				self._connections[nodeName] = result
			except Exception, e:
				if e == ErrClusterIDMismatch:
					raise e
				#print ("Exception in _getConnection: " + str (e))
				result.Close()
				result = None
				del self._connections[nodeName]
			finally:
				self._lock.release()
		return result

	def _removeBrokenConnection (self, client):
		self._lock.acquire()
		for nodeName in self._connections:
			nodeClient = self._connections[nodeName]
			if nodeClient == client:
				del self._connections[nodeName]
				nodeClient.Close()
				self._lock.release()
				return
		self._lock.release()




