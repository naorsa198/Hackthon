import socket
import time
import struct
import random

print('Server started, listening on IP address 132.72.66.42')
dict_names = {}
group_1 = []
group_2 = []
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serverPort = 2097
tcp_socket.bind(('',serverPort))
tcp_socket.listen(1)

tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
# Enable broadcasting mode
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

message = struct.pack('Ibh', 0xfeedbeef, 0x2, 2098)

i = 1
while i<= 10:
    i = i + 1
    udp_socket.sendto(message, ('<broadcast>', 2221))
    time.sleep(1)

connectionSocket, addr = tcp_socket.accept()
message_name = connectionSocket.recv(1024)

dict_names[addr[0]] = message_name
rnd = random.randint(1,2)
if(rnd == 1):
    group_1.append(message_name)
else:
    group_2.append(message_name)

group_1_names = b''
for name in group_1:
    group_1_names = group_1_names+name
group_2_names = b''

for name in group_2:
    group_2_names = group_2_names+name

connectionSocket.send(b'Welcome to Keyboard Spamming Battle Royale.\n Group 1: \n==\n'+ group_1_names+b'\n Group 2:\n==\n'+ group_2_names + b'\nStart pressing keys on your keyboard as fast as you can!!')
start = time.time()
end = time.time()
counter = 0
while end - start <= 10:
    try:
        connectionSocket.settimeout(0.1)
        char = connectionSocket.recv(1024).decode("utf-8")
        if(len(char) > 0):
            counter = counter + 1
        print(char)
    except:
        pass
    end = time.time()

print(counter)
val_score = str(counter)
val_score_bytes = val_score.encode()
connectionSocket.send(b'Game over!\nGroup 1 typed in ' + val_score_bytes)
connectionSocket.close()
tcp_socket.close()