import socket
import struct
import time
import sys
import select
from threading import Thread
from scapy.all import *


def flush_input():
    try: # for Windows
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import termios    #for linux/unix
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

def getPlayerAnswer():
    # only need to collect 1 char from player, since the game is over after server receives 1 char from either players
    # thus, any subsequent input from the player won't effect the game at all and is therefore unimportant
    char = None
    try:
        char = sys.stdin.read(1).encode()
    except Exception as err:
        pass
    if char != None:
        tcpSock.send(char)

    try:
        flush_input()
    except Exception as err:
        pass

while True:
    udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    #udpSock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udpSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1) #todo uncomment this when running on linux

    # try to bind UDP sock to port 13117
    clientPort = 13117

    # configure ip and ports on REMOTE
    interface="eth1"
    clientIP = get_if_addr(interface)

    # configure ip and ports on LOCAL
    # hostname = socket.gethostname()
    # clientIP = socket.gethostbyname(hostname)

    address = (clientIP, clientPort)
    # print(f"clientIP={clientIP} clientPort={clientPort}")
    try:
        udpSock.bind(address)
    except socket.error as msg:
        pass

    teamName = "Zrubavel"
    print('\nClient started, listening for offer requests...')
    msg, serverAddr = udpSock.recvfrom(1024)
    # print(f"\nserverAddr={serverAddr}") # (ip, port)
    udpSock.close()

    try:
        # decode server's message + check validity
        decodedMsg = struct.unpack('IbH', msg)
        magicCookie = decodedMsg[0]
        ServerTcpPort = decodedMsg[2]
    except Exception as e:
        pass
        msg = msg.decode().split(',')
        magicCookie = int(msg[0])
        ServerTcpPort = int(msg[2])


    if(magicCookie == int(0xabcddcba)):
        tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            #tcpSock.setblocking(False)
            print(f"\nReceived offer from {serverAddr[0]},attempting to connect...")
            tcpSock.connect((serverAddr[0], ServerTcpPort))
            tcpSock.send(teamName.encode())

            mathProblem = tcpSock.recv(1024)
            print(mathProblem.decode())

            # get 1 char from player
            threadGetAnswer = Thread(target=getPlayerAnswer)
            threadGetAnswer.start()
        except ConnectionResetError as e:
            pass
        except Exception as err:
            pass

        # check the stream to see if server sent the game summary (game over)
        results = None
        try:
            results = tcpSock.recv(1024) # server sends game summary
        except ConnectionResetError as err: # if server has runtime exception/network issues the attempts to connect to it throws exception
            pass
        except Exception as e:
            pass

        # game over!
        try:
            if threadGetAnswer.is_alive(): # stop getting player keyboard input
                threadGetAnswer._stop.set()
                #threadGetAnswer.join()
        except Exception as e:
            pass
        print(results.decode())
        tcpSock.close()
        print("Server disconnected, listening for offer requests...")

