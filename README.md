# simple-FTP
a simple FTP server/client for transferring files. The program will establish a connection for control/commands and establish a secondary connection for the data transfer.

Executing FTPser.py: python FTPser.py <Port_num>

Executing FTPcli.py: python FTPcli.py <server_machine> <server_port>

FTP commands:
  
  - get <file_name> (retrieve file from server.)
  - put <file_name> (send file to server.)
  - ls  (List of files on the server.)
  - lls (List of files on host.)
