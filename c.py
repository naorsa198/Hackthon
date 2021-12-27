import socket
import struct
import time
import sys
import select
import tty
import termios

##### Naor & Leej

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT)
udp_sock.bind(("", 13117))
msg, serverAddr = udp_sock.recvfrom(4080)

##########################################################################

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

print('Client started, listening for offer requests...”')
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
udp_socket.bind(("", 2221))
data, addr = udp_socket.recvfrom(1024)
message = struct.unpack('Ibh', data)
# check if start with cookie

print('Received offer from ' + addr[0] + ', attempting to connect...')
TCP_IP = addr[0]
TCP_PORT = message[2]
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #tcp
tcp_socket.connect((TCP_IP, TCP_PORT))
tcp_socket.send(b'blalala')

welcome = tcp_socket.recv(1024)
print(welcome.decode("utf-8"))

start = time.time()
end = time.time()
while end - start <= 5:
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        if isData():
            char = sys.stdin.read(1)
            #char = getch.getch()
            char_b = char.encode()
            tcp_socket.settimeout(0.1)
            tcp_socket.send(char_b)
    except:
        print('time out')
    end = time.time()

res = tcp_socket.recv(1024)
print(res.decode("utf-8"))
tcp_socket.close()