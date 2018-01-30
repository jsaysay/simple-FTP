#Jonathan Saysay
#Client code
#
import socket
import sys
import os
import commands

# Server address
serverAddr = sys.argv[1]

# Server port
serverPort = int(sys.argv[2])

# Create a TCP socket
connSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
connSock.connect((serverAddr, serverPort))


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

	#get command input from user
	userInput = raw_input('ftp> ')

	#get first argument for command. Should be either get/put/lls/ls
	usercommand = userInput.split(' ')[0]

	#get length of user input to send to server.
	commandLen = str(len(userInput))

	#prepend 0's up to 4 digit size of user input.
	while len(commandLen) < 4:
		commandLen = "0" + commandLen

	#prepend size of user input to user input
	userInput = commandLen + userInput

	#if command is either get/put/ls create new connection for data
	if usercommand == "get" or usercommand == "put" or usercommand == "ls":

		numSent = 0
		#send input command to server to establish data connection
		while len(userInput) > numSent:
			numSent += connSock.send(userInput[numSent:])
		
		#receive port number size of new socket from server for data connection
		dataPortSize = recvAll(connSock, 5)
		#print dataPortSize
		dataPortSize = int(dataPortSize)

		dataPort = recvAll(connSock, dataPortSize)

		#convert to int
		dataPort = int(dataPort)

		# Create a TCP socket
		dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Connect to the server for data connection
		dataSock.connect((serverAddr, dataPort))


		#perform operations on get/put/ls commands
		if usercommand == "get" and len(userInput.split(' ')) == 2:

			#get first char of recieved data, 
			#if S, then command is successful, else, failure occured
			commandStatus = recvAll(dataSock, 1)

			#store file name in variable
			fileName = userInput.split(' ')[1]

			#if file was successfully recieved
			if commandStatus == "S":
				

				# The size of the incoming file
				fileSize = 0	
				
				# The buffer containing the file size
				fileSizeBuff = ""
				
				# Receive the first 10 bytes indicating the
				# size of the file
				fileSizeBuff = recvAll(dataSock, 10)
					
				# Get the file size
				fileSize = int(fileSizeBuff)
				
				# Get the file data
				fileData = recvAll(dataSock, fileSize)
				
				#open file
				fileObj = open(fileName,"w")

				#write file data to file
				fileObj.write(fileData)

				#close file and socket
				fileObj.close()
				dataSock.close()

				print "SUCCESS:",fileName, "was downloaded! :)"
				print "The file size is ", fileSize, "bytes."

			#this means file could not be retrieved
			else:
				#close socket
				dataSock.close()

				print "FAILURE:",fileName, "was not downloaded. :("


		#if command is "put", send file to server
		elif usercommand == "put" and len(userInput.split(' ')) == 2:
			#get file name
			fileName = userInput.split(' ')[1]

			#check if file exists
			if os.path.isfile(fileName):
				#get file size
				fileSize = os.stat(fileName)
				fileSize = fileSize.st_size
				
				#open file in read mode
				fileObj = open(fileName,"r")
				#store file data in variable
				fileData = fileObj.read(fileSize)

				#convert file size to string
				datasizeStr = str(len(fileData))
				
				#prepend 0's to data size until size of 10
				while len(datasizeStr) < 10:
					datasizeStr = "0" + datasizeStr

				# Prepend the size of the data to the
				# file data.	
				fileData = datasizeStr + fileData

				#prepend S to indicate success to server.
				fileData = "S" + fileData

				#variable to keep track of number of bytes sent to server
				numSent = 0

				#send data
				while len(fileData) > numSent:
					numSent += dataSock.send(fileData[numSent:])

				print "SUCCESS:", fileName, "was sent!"
				print "Sent ", numSent, " bytes."

				#close file and socket
				dataSock.close()
				fileObj.close()

			#file was not found in client directory	
			else:
				#close data socket
				dataSock.close()
				print "FAILURE:",fileName, "was NOT sent!"

		#if command is "ls" get ls command data from server
		elif usercommand == "ls":
		
			# The size of the incoming data from ls command
			dataSize = 0	
			
			# The buffer containing the datasize
			dataSizeBuff = ""
			
			# Receive the first 10 bytes indicating the
			# size of data from ls command
			dataSizeBuff = recvAll(dataSock, 10)
				
			# Get the data size
			dataSize = int(dataSizeBuff)

			#get ls data
			lsData = recvAll(dataSock, dataSize)

			print "displaying server files:\n"
			print lsData

			#close socket
			dataSock.close()

		else:
			print "ERROR: action could not be performed!"

	#if command is lls, no connection required.
	elif usercommand == "lls":
		print "displaying current directory files:"
		for line in commands.getstatusoutput('ls -l'):
			print line		

	#if command is quit, exit server
	elif usercommand == "quit":
		connSock.send(userInput)
		print "disconnecting from server..."
		#close connection
		connSock.close()
		exit(0)

	else:
		print "incorrect command; use get/put/ls/lls/quit commands"

#close control connection
connSock.close()
			



	
