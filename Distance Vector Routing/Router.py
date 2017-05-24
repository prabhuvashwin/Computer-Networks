import threading
import socket
import sys
import time

## Used for thread synchronization
def synchronized(func):
	func.__lock__ = threading.Lock()

	def synced_func(*args, **kws):
		with func.__lock__:
			return func(*args, **kws)

	return synced_func

class Router:
	networkVectors = list(list())
	portNumbers = list()
	nodes = list()
	ID = 0
	vectorList = list()
	nextHopList = list()
	file = ""
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	neighbours = list()
	count = 1

	## Method to initialize network vectors
	@staticmethod
	def InitializeNetworkVectors(length, nodesCommand):
		Router.networkVectors = [[float("inf") for x in range(length)] for y in range(length)]
		Router.portNumbers = [0 for x in range(length)]
		Router.nodes = ["" for x in range(length)]
		temp = nodesCommand.split('-')
		for i in range(length):
			Router.networkVectors[i][i] = 0.0
			t = temp[i].split(":")
			Router.nodes[i] = t[0]
			Router.portNumbers[i] = int(t[1])

	## Find the index of the node
	@staticmethod
	def IndexOf(s):
		for i in range(Router.nodes.__len__()):
			if Router.nodes[i] == s:
				return i
		return -1

	## Method to initialize local vectors
	@staticmethod
	def InitializeLocalVectors(id, parent, length):
		Router.ID = id
		Router.vectorList = [float("inf") for x in range(length)]
		Router.nextHopList = ["" for x in range(length)]
		Router.file = parent
		print("Router " + Router.nodes[id-1] + " is working.")
		Router.sock.bind(("127.0.0.1", int(Router.portNumbers[Router.ID-1])))

	## Read data file
	@staticmethod
	def ReadDataFile():
		for x in range(Router.networkVectors.__len__()):
			Router.networkVectors[Router.ID-1][x] = float("inf")
		Router.networkVectors[Router.ID-1][Router.ID-1] = 0.0
		fileContents = open(Router.file, 'r')
		length = int(fileContents.readline())
		Router.neighbours = ["" for _ in range(length)]
		for i in range(length):
			temp = fileContents.readline().split(' ')
			index = Router.IndexOf(temp[0])
			Router.neighbours[i] = temp[0]
			if (Router.count == 1):
				Router.nextHopList[index] = temp[0]
				Router.vectorList[index] = float(temp[1])
				Router.networkVectors[Router.ID-1][index] = float(temp[1])
		fileContents.close()

	## Display routes
	@staticmethod
	def DisplayRoutes():
		print("Output #: " + str(Router.count))
		Router.count = Router.count + 1
		source = Router.nodes[Router.ID-1]
		for i in range(Router.vectorList.__len__()):
			if i != Router.ID - 1:
				destination = Router.nodes[i]
				s = ""
				if Router.vectorList[i] == float("inf"):
					s = "No routes found"
				else:
					s = "Next hop is: " + Router.nextHopList[i] + " and the cost is: " + str(Router.vectorList[i])
				print("Shortest path: " + source + "-" + destination + ": " + s)

	## Method to update network vectors
	@staticmethod
	@synchronized
	def UpdateNetworkVectors(vector, port):
		index = 0
		for index in range(Router.portNumbers.__len__()):
			if Router.portNumbers[index] == port:
				break
		if index == Router.portNumbers.__len__():
			return
		for i in range(vector.__len__()):
			Router.networkVectors[index][i] = float(vector[i])

	## Compute distance vector
	@staticmethod
	def ComputerDistanceVector():
		for i in range(Router.neighbours.__len__()):
			index = Router.IndexOf(Router.neighbours[i])
			for j in range(Router.vectorList.__len__()):
				if j == Router.ID - 1:
					continue
				elif Router.vectorList[j] > Router.networkVectors[Router.ID-1][index] + Router.networkVectors[index][j]:
					Router.vectorList[j] = Router.networkVectors[Router.ID-1][index] + Router.networkVectors[index][j]
					Router.nextHopList[j] = Router.neighbours[i]

	## Read network vector info coming from other nodes
	@staticmethod
	def ReadNetworkVectors():
		message, addr = Router.sock.recvfrom(1024)
		t3 = threading.Thread(target=Router.UpdateNetworkVectors, args=(message.split(":"), addr))
		t3.start()

	## Send network vector info to other nodes
	@staticmethod
	def WriteToNetworkVectors():
		for i in range(Router.neighbours.__len__()):
			data = ""
			for j in range(Router.vectorList.__len__()):
				if Router.neighbours[i] == Router.nextHopList[j]:
					data = data + str(float("inf"))
				else:
					data = data + str(Router.vectorList[j])
				if j + 1 != Router.vectorList.__len__():
					data = data + ":"
			port = Router.portNumbers[Router.IndexOf(Router.neighbours[i])]
			Router.sock.sendto(data, ("127.0.0.1", port))

	@staticmethod
	def WriteVector():
		Router.DisplayRoutes()
		Router.WriteToNetworkVectors()
		time.sleep(15)
		Router.ReadNetworkVectors()
		Router.ComputerDistanceVector()
		time.sleep(15)
		threading.Timer(15, Router.WriteVector())

if __name__ == "__main__":
	Router.InitializeNetworkVectors(int(sys.argv[3]), sys.argv[4])
	Router.InitializeLocalVectors(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]))

	Router.ReadDataFile()

	t1 = threading.Thread(target=Router.ReadNetworkVectors, args=())
	t1.start()

	Router.WriteVector()
