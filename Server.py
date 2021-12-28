import socket
import time
import struct
import random
from threading import Thread
from collections import OrderedDict

import scapy

class player:
    def __init__(self, teamName):
        self.teamName = teamName
        self.answer = ""
        self.PORT = None  # TCP
        self.IP = None

    def __eq__(self, other):
        if not isinstance(other, player):
            return "other is not an instance of type <player>"
        elif self is other:
            return True
        else:
            return self.PORT == other.PORT and self.IP == other.IP

class Game:
    """"""
    def __init__(self):
        """initial Game params"""
        self.lThreads = []
        self.lTeamNames = []
        self.summary = ""
        self.dTeamsAnswers = dict()

# global vars
summary=""
threads = []
teamNames = []
answer = False
clientAns = OrderedDict() #todo Redundant overhead, pls use regular dict
result = 2
lock = True

def clientThread(clientSocket, index):
    '''
    :param clientSocket:  socket connect to player
    :param index: first or sec player to join game
    this function send to player msg, and get from him msg to the global vars
    :return:
    '''
    try:
        while True:
            print(index, end='\n')
            #send the welcome message + math problem to client
            clientSocket.send(qes.encode())
            #recv answer from client and put it into dictionary [teamname] = answer
#   TODO HERE HABE BUG ITS NOT RECVING
            myans = clientSocket.recv(1024)
            myans = myans.decode()
            print(f"func 'clientThread': client_ans={myans} => success! recieved char from client over TCP... the method of global vars doesn't work")
            clientAns[index] = myans
            global answer
            answer = True
            # look to not read befor server finish to write
            global lock
            while lock:
                pass
            print("after lock")
            #send to client the summary of the game
            clientSocket.send(summary.encode())
            clientSocket.close()
    except IOError:
        print("IOE Error threade")
    finally:clientSocket.close()

def count10():
    i=0
    while (i < 10 and answer == False):
        print("start count 10sec == " + str(i))
        i += 1
        time.sleep(1)
        global  summary
        global lock
        if answer == False:
            summary = "Game Finish With Draw"
        if (i == 2):
            lock = False


def udp_start(msg, clientPort,udp_socket):
    '''
    :param msg: udp broadcast msg
    :param ip: my ip
    :param clientPort: client port 13117
    :param udp_socket:  my computer udp socket
    '''
   # run main udp thread calling for 2 players stop after get 2 players runing every 1sec and stop after he find 2 players
    while(len(threads) < 2):
            print("sending UDP broadcast every 1sec or until 2 clients join the game", end='\n')
            # Broadcast to everyone (not to a specific IP)
            udp_socket.sendto(msg.encode(), ('<broadcast>', clientPort))
            time.sleep(1) # send every 1 sec




# configure ip and ports
hostname = socket.gethostname()
serverIP =  socket.gethostbyname(hostname)
clientPort=13117

# create udp socket
udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
udpSocket.bind((serverIP, 0))
udpPort = udpSocket.getsockname()[1]
print(f"server UDP socket = {udpSocket.getsockname()}", end='\n')

#create tcp socket
tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpSock.bind((serverIP, 0))
tcpPort = tcpSock.getsockname()[1]
print(f"server TCP socket = {tcpSock.getsockname()}", end='\n')
msg = "offer,"+str(tcpPort) #todo change this to the correct msg udp format from assignment instructions
#msg = struct.pack('Ibh', 0xabcddcba, 0x2, myPortTcp)

tcpSock.listen(2)

# start the udp thread
udpThreadFunction = udp_start
udpThread = Thread(target=udpThreadFunction, args =[msg, clientPort, udpSocket])
udpThread.start()
print("main thread: started UDP thread, server is now broadcasting offers (udp)")
print(f"Server started, listening on IP address {serverIP}")
# server alawys run and looking for players
while True:
    try:
        (clientSocket, (clientIP, port)) = tcpSock.accept()
        print(f'(clientSocket={clientSocket}, (clientIp={clientIP},clientPort={port}))')
        # clientSocket.settimeout(0.5)
        teamName = clientSocket.recv(1024).decode().strip('\n')
        teamNames.append(teamName)
        runt = clientThread
        newthread = Thread(target=runt , args=[clientSocket,len(threads)])
        threads.append(newthread)
    except socket.timeout:
        print("time out Team not send name")
        clientSocket.close()

    if(len(threads)==2):
        #todo generate random math problem
        qes = (f"Welcome to Quick Math." +'\n'+ "Player 1 : "+teamNames[0] +'\n' + "Player 2 : " + teamNames[1] + '\n' "===" +'\n' "Please answer the following question as fast as you can:" +'\n'+ "How much is 2+2  ?" )
        threads[0].start()
        threads[1].start()
        print("here")

        i = 0
#TODO ITS NEED TO BE i= 10, I CHANGED IT TO 3 TO MAKE TEST EASIER
        count10()
        if(answer == True):
            key = list(clientAns.keys())[0]
            otherTeam = teamNames[1]  if teamNames[0] == key else teamNames[0]
            summary = "Game Over" + '\n' "The corrent answer was 4!" '\n' + "Congratulations to the winner: "+ key if(clientAns[key] == 4) else "Game Over" + '\n' "The corrent answer was 4!" '\n' + "Congratulations to the winner: "+otherTeam
        lock = False
        threads[0].join()
        threads[1].join()
        threads.clear()
        answer = False





