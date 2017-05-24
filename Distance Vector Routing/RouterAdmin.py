import sys
import os
import subprocess
import time

## Check if the port entered is in use
def IsPortinUse(ports, len, port):
	for i in range(len):
		if ports.__len__() == 0:
			return False
		if ports[i] == [port]:
			return True
	return False

def main():
	if sys.argv.__len__() != 2:
		print("Incorrect usage.")
		return

	folderPath = sys.argv[1]
	if not os.path.exists(folderPath):
		print("This directory does not exist")
		return

	datFiles = os.listdir(folderPath)
	portNumbers = []
	nodes = ""

	print("Initializing simulation for " + str(datFiles.__len__()) + " routers.")

	for i in range(datFiles.__len__()):
		temp = datFiles[i]
		print("Enter UDP port (1025-65535) for router " + temp[0] + ":")
		flag = False

		while not flag:
			try:
				p = int(input())
				portNumbers.append(p)
				flag = True
			finally:
				pass
		nodes = nodes + temp[0] + ":" + str(portNumbers[i])
		if i + 1 != datFiles.__len__():
			nodes = nodes + "-"

	for i in range(datFiles.__len__()):
		path = folderPath + "/" + datFiles[i]
		subprocess.call(['python terminal.py python Router.py ' + str(i+1) + ' ' + path + ' ' + str(datFiles.__len__()) + ' ' + nodes], shell=True)
		time.sleep(2)

if __name__ == "__main__":
	main()