import socket
import time
import struct
import random
from threading import Thread
from collections import OrderedDict

import scapy

class player:
    lPlayers = []
    def __init__(self, teamName, index, clientIP, clientPORT):
        self.index = index
        self.teamName = teamName
        self.answer = ""
        self.PORT = clientPORT  # TCP
        self.IP = clientIP

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
        self.lTeamNames = [] # may be redundant...
        self.summary = ""
        self.dTeamsAnswers = dict()
        self.mathProblem = ""
        self.correctAnswer = ""
        self.playerAnswer = "" # once a char is received from 1 player we can determine the game result

# global vars
summary=""
threads = []
teamNames = []
answer = False
clientAns = OrderedDict() #todo Redundant overhead, pls use regular dict
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
            print(f"Hi, I am client number {index}\n", end="\n")
            #send the welcome message + math problem to client
            clientSocket.send(qes.encode())
            #recv answer from client and put it into dictionary [teamname] = answer
            myans = clientSocket.recv(1024) #TODO Make this Non-Blocking otherwise the other client is stuck here and doesn't get the summary
            myans = myans.decode()
            print(f"func 'clientThread': client_{index}_ans={myans} => success! recieved char from client over TCP... the method of global vars doesn't work")
            clientAns[index] = myans
            # todo If (gameObj.playerAnswer) then immediately send summary to BOTH players
            # myans = None
            # while gameObj.playerAnswer == None:
            #   myans = clientSocket.recv(1024)
            #   clientSocket.settimeout(2)
            #   if myans != None:
            #       myans = myans.decode()
            #       gameObj.playerAnswer = myans #todo should put mutex on the resource when writing
            #
            # #else -> other player gave an answer
            #   send gameObj.summary
            global answer
            answer = True
            # lock to not read befor server finish to write
            global lock
            while lock: # released after 2 seconds
                pass
            print("after lock")
            #send to client the summary of the game
            clientSocket.send(summary.encode())
            clientSocket.close()
    except IOError as msg:
        print("Client thread: IOError.",msg)
    finally:
        clientSocket.close()

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
    # send summary to both players


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
            udp_socket.sendto(msg, ('<broadcast>', clientPort))
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
try:
    msg = struct.pack('IbH', 0xabcddcba, 0x2, tcpPort)
except struct.error as err:
    print(err)
    msg = "2882395322," + str(2) + "," + str(tcpPort)
    msg = msg.encode()
tcpSock.listen(2) # 2 is num of UNaccepted connections allowed before server refuses connections

# start the udp thread
udpThreadFunction = udp_start
udpThread = Thread(target=udpThreadFunction, args =[msg, clientPort, udpSocket])
udpThread.start()
print("main thread: started UDP thread, server is now broadcasting offers (udp)")
print(f"Server started, listening on IP address {serverIP}")
# server alawys run and looking for players

while True:
    try:
        (clientSocket, (clientIP, clientPORT)) = tcpSock.accept()
        # clientSocket.settimeout(0.5)
        playerName = clientSocket.recv(1024).decode().strip('\n')
        teamNames.append(playerName) # todo find & replace usages with player.lPlayers[idx].name
        playerIdx = len(threads) # get len before appending new thread
        player.lPlayers.append(player(playerName, playerIdx, clientIP, clientPORT))
        print(f'\nClient {player.lPlayers[playerIdx].teamName}: clientIp={clientIP}, clientPort={clientPORT}')
        runt = clientThread
        newthread = Thread(target=runt , args=[clientSocket,playerIdx])
        threads.append(newthread)
    except socket.timeout:
        print("time out Team not send name")
        clientSocket.close()

    if(len(threads)==2):
        #todo generate random math problem
        qes = (f"Welcome to Quick Math." +'\n'+ "Player 1 : "+teamNames[0] +'\n' + "Player 2 : " + teamNames[1] + '\n' "===" +'\n' "Please answer the following question as fast as you can:" +'\n'+ "How much is 2+2  ?" )
        threads[0].start()
        threads[1].start()
        print("\n Two player threads started")

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





