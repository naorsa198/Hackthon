import socket
import struct
import time
import sys
import select
from threading import Thread


def flush_input():
    try: # for Windows
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios    #for linux/unix
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def getPlayerAnswer():
    # only need to collect 1 char from player, since the game is over after server receives 1 char from either players
    # thus, any subsequent input from the player won't effect the game at all and is therefore unimportant
    char = None
    try:
        char = sys.stdin.read(1).encode()
        print(f"getAnswer thread: the player's input was {char} - is that correct?")
    except Exception as err:
        print(err)
    if char != None:
        tcpSock.send(char)

    try:
        flush_input()
    except Exception as err:
        print(err)


udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
udpSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#udp_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)

# try to bind UDP sock to port 13117
clientPort = 13117
hostname = socket.gethostname()
clientIP =  socket.gethostbyname(hostname)
address = (clientIP, clientPort)
try:
    udpSock.bind(address)
except socket.error as msg:
    print("\nBind failed. Error code: " + str(msg[0]) + '\nMessage ' + msg[1])

# teamName = "Zrubavel"
teamName = "Naor"
print('\nClient started, listening for offer requests...')
msg, serverAddr = udpSock.recvfrom(1024)
print(f"\nserverAddr={serverAddr}") # (ip, port)
udpSock.close()

try:
    #decode server's message + check validity
    decodedMsg = struct.unpack('IbH', msg)
    print(f"\nthe udp msg from server is: {decodedMsg}")
    magicCookie = decodedMsg[0]
    ServerTcpPort = decodedMsg[2] #todo should be the 3rd element, i.e. msg[2]
    print(f"\nmagicCookie = {magicCookie}")
    print(f"\nServer TCP Port = {ServerTcpPort}")
except Exception as e:
    print(e)
    msg = msg.decode().split(',')
    magicCookie = int(msg[0])
    ServerTcpPort = int(msg[2])


if(magicCookie == int(0xabcddcba)):
    tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(f"\nReceived offer from {serverAddr[0]},attempting to connect...")
        tcpSock.connect((serverAddr[0], ServerTcpPort))
        tcpSock.send(teamName.encode())

        mathProblem = tcpSock.recv(1024)
        print(mathProblem.decode())

        # get 1 char from player
        threadGetAnswer = Thread(target=getPlayerAnswer)
        threadGetAnswer.start()
    except ConnectionResetError as e: # specifically: ConnectionResetError
        print(e)
        # try to reconnect to server ? assume server went down, so maybe it comes back up again?

    # check the stream to see if server sent the game summary (game over)
    results = None
    try:
        while not results:
            results = tcpSock.recv(1024) # server sends game summary
            print(f"client {teamName}: looping to get summary msg from server, got: {results}")
    except ConnectionResetError as err: # if server has runtime exception/network issues the attempts to connect to it throws exception
        print(err)

    # game over!
    try:
        if threadGetAnswer.is_alive(): # stop getting player keyboard input
                #threadGetAnswer._stop.set()
                threadGetAnswer.join()
    except Exception as e:
            print(e)
    print(results.decode())
    tcpSock.close()

#todo add infinite loop because client needs to run forever

