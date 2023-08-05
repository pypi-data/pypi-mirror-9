#
# Example Python code showing sending, receiving and getting the maximum index 
# available from a topic on Forest Bus.
# 
# The example requires forest-bus-server to be running with three nodes on localhost with a
# cluster Id of "testcluster" and cbor listening on ports 5000 through 5001.
# For example:
# forest-bus-server -id testcluster -cbor :5000 -name :3000 -path ~/forest-data/bus1
# forest-bus-server -id testcluster -cbor :5001 -name :3001 -path ~/forest-data/bus2
# forest-bus-server -id testcluster -cbor :5002 -name :3002 -path ~/forest-data/bus3
#
# On first start the servers need configuring with their peers:
# forest-admin -id testcluster peers :3000,:3001,:3002
#
# A test topic also needs to have been created:
# forest-admin -id testcluster topic test
#
import json
import socket
from forestbus import forest

print ("Attempting client connection.")

client = forest.Client ("testcluster", ["localhost:5000","localhost:5001", "localhost:5002"])

try:
	print ("Calling GetMessages on missing topic test-wrong")
	result = client.GetMessages ("test-wrong", 1, 1, False)
	print (result)
except Exception as e:
	print(("Error as expected when calling GetMessages on non-existant topic: " + str (e)))

msgs = json.dumps ({"Test field 1": "Hello", "Test field 2": "World"})

try:
	maxIndex = client.GetTopicMaxAvailableIndex("test")
	print(("Maximum index for test: " + str (maxIndex)))

	print ("Sending messages to the test topic")
	ids = client.SendMessages("test", [msgs], True)
	print(("Resulting IDs: " + str (ids)))

	print ("Calling GetMessages on topic test")
	result = client.GetMessages ("test", 1, 1, True)
	print (result)

	print ("Sending further messages to the test topic")
	ids = client.SendMessages("test", [msgs], True)
	print(("Resulting IDs: " + str (ids)))


except Exception as e:
	print(("Unexpected error during test: " + str (e)))


print ("Requesting close")
client.Close()

print ("Close done")
