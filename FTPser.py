#Jonathan Saysay
#Server code
#
import socket
import sys
import os
import commands

listenPort = int(sys.argv[1])

# Create a welcome socket for control connection. 
welcomeSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
welcomeSock.bind(('', listenPort))

# Start listening on the socket
welcomeSock.listen(1)

print "Waiting for connections on port ",listenPort,"..."
	

# ************************************************
# Receives the specified number of bytes
# from the specified socket
# @param sock - the socket from which to receive
# @param numBytes - the number of bytes to receive
# @return - the bytes received
# *************************************************
def recvAll(sock, numBytes):

	# The buffer
	recvBuff = ""
	
	# The temporary buffer
	tmpBuff = ""
	
	# Keep receiving till all is received
	while len(recvBuff) < numBytes:
		
		# Attempt to receive bytes
		tmpBuff =  sock.recv(numBytes)
		
		# The other side has closed the socket
		if not tmpBuff:
			break

		
		# Add the received bytes to the buffer
		recvBuff += tmpBuff
		
	return recvBuff

while True:

	# Accept connections for control connection
	clientSock, addr = welcomeSock.accept()

	print "Establiished control connection from client: ", addr
	print "\n"

	#variable for user command from client
	usercommand = ""

	#handle get/put/ls commands from client
	#and establish a new connection with a new socket for data handling.
	while usercommand != "quit":
		

		#get size of user input and convert to int
		userInputSizeStr = recvAll(clientSock,4)
		userInputSize = int(userInputSizeStr)

		#get user input.
		userInput = recvAll(clientSock,userInputSize)
		
		#get first argument for user input. determine if (get/put/ls)
		usercommand = userInput.split(' ')[0]

		#create data connection if command was get/put/ls
		if (usercommand == "get" or usercommand == "put" or usercommand == "ls"):
			# Create a data socket for data connection. 
			dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

			# Bind the socket to the port
			dataSock.bind(('', 0))

			#store port of data connection in a variable
			portNumStr = str(dataSock.getsockname()[1])

			#store length of port number in bytes and convert to string
			portSize = str(len(portNumStr))

			while len(portSize) < 5:
				portSize = "0" + portSize

			portNumStr = portSize + portNumStr

			# The number of bytes sent
			numSent = 0
					
			#send port number of new socket to client to establish connection
			while len(portNumStr) > numSent:
				numSent += clientSock.send(portNumStr[numSent:])


			# Start listening on the socket
			dataSock.listen(1)

			print "Waiting for connections on port ",dataSock.getsockname()[1],"..."
			
			# Accept connections
			newSock, newaddr = dataSock.accept()

			print "Established data connection from client: ", newaddr
			print "\n"

		
			#variable to store file data
			fileData = None

			#if user issued a get command along with a file name 
			if usercommand == "get" and len(userInput.split(' ')) == 2:
				#get file name
				fileName = userInput.split(' ')[1]

				#check if file exists
				if os.path.isfile(fileName):

					#get file size
					fileSize = os.stat(fileName)
					fileSize = fileSize.st_size
					# Open the file
					fileObj = open(fileName, "r")

					#read file data
					fileData = fileObj.read(fileSize)

					#get file size and convert to string
					dataSizeStr = str(len(fileData))

					# Prepend 0's to the size string
					# until the size is 10 bytes
					while len(dataSizeStr) < 10:
						dataSizeStr = "0" + dataSizeStr


					# Prepend the size of the data to the
					# file data.
					fileData = dataSizeStr + fileData	

					#prepend S to data to indicate success
					fileData = "S" + fileData

					# The number of bytes sent
					numSent = 0
					
					# Send the data on the data connection
					while len(fileData) > numSent:
						numSent += newSock.send(fileData[numSent:])
					
					print "SUCCESS:",fileName, "was sent to client."
					print "Sent ", numSent, " bytes.\n"

					#close socket
					newSock.close()
					#close file
					fileObj.close()

				#this means file could not be found in directory of server
				else:
					print "Error:",fileName," does not exist in this directory\n"
					#send F to indicate failure to client
					newSock.send("F")
			
			#if user issued a put command
			elif usercommand == "put" and len(userInput.split(' ')) == 2:

				#get first char of recieved data, 
				#if S, then command is successful, else, failure occured
				commandStatus = recvAll(newSock, 1)

				#get file name
				fileName = userInput.split(' ')[1]

				if commandStatus == "S":
					

					# The size of the incoming file
					fileSize = 0	
					
					# The buffer containing the file size
					fileSizeBuff = ""
					
					# Receive the first 10 bytes indicating the
					# size of the file
					fileSizeBuff = recvAll(newSock, 10)
						
					# Get the file size
					fileSize = int(fileSizeBuff)
					
					print "The file size is ", fileSize, "bytes."

					# Get the file data
					fileData = recvAll(newSock, fileSize)
					
					#open file
					fileObj = open(fileName,"w")

					#write file data to file
					fileObj.write(fileData)

					#close file and socket
					fileObj.close()
					newSock.close()

					print fileName, "successfully retrieved.\n"

				#file was not received from client.
				else:
					newSock.close()
					print "Error:",fileName," file was not placed in directory\n"

			#if user issued an ls command
			elif usercommand == "ls":

				#variable to store "ls" command data
				lsData = ""

				#get each line from "ls" command and store in variable
				for line in commands.getstatusoutput('ls -l'):
					lsData += str(line)

				#get size of ls command data and cast to string
				datasizeStr = str(len(lsData))

				#prepend 0's to data size until size of 10
				while len(datasizeStr) < 10:
					datasizeStr = "0" + datasizeStr

				#prepend data size to ls command data
				lsData = datasizeStr + lsData

				#variable to store number of bytes sent	
				numSent = 0

				#send ls data
				while len(lsData) > numSent:
					numSent += newSock.send(lsData[numSent:])

				#close data socket	
				newSock.close()

				print "SUCCESS: server file list sent to client.\n"

			else:
				print "ERROR: command could not be performed.\n"
				newSock.close()
    
	print  addr,"has disconnected from server.\n "		
	clientSock.close()
	print "waiting for connections..\n"