import socket
import struct
import time
import sys
import select

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
udp_socket.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
clientPort = 13117
hostname = socket.gethostname()
ip =  socket.gethostbyname(hostname)
address = (ip,clientPort)
udp_socket.bind((ip,clientPort))
teamName = "Naor"

print('Client started, listening for offer requests...”')
msg, serverAddr = udp_socket.recvfrom(1024)
udp_socket.close()
msg = msg.decode().split(',')
ServerTcpPort = int(msg[1])
print(serverAddr) # (port,ip)
if(str(msg[0])== "offer"):
    print(f"Received offer from {serverAddr[0]},attempting to connect...")
    tcp_client =  socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcp_client.connect((serverAddr[0],ServerTcpPort))
    tcp_client.send(teamName.encode())
    modifiedSenctence = tcp_client.recv(1024)
    print(modifiedSenctence.decode())
    char = sys.stdin.read(1)
    tcp_client.send(char.encode())
    tcp_client.close()



