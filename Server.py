import socket
import time
import struct
import random
from threading import *
from collections import OrderedDict
from scapy.all import *
import traceback


class player:
    lPlayers = []
    def __init__(self, teamName, index, clientIP, clientPORT, clientSocket):
        self.index = index
        self.teamName = teamName
        self.answer = ""
        self.PORT = clientPORT  # TCP
        self.IP = clientIP
        self.clientSocket = clientSocket

    def closeTcpConn(self):
        self.clientSocket.close()

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
        self.lPlayers = []
        self.summary = None
        #self.dTeamsAnswers = dict()
        self.mathProblem = None
        self.correctAnswer = None
        self.playerAnswer = None # once a char is received from 1 player we can determine the game result
        self.winner = None
        self.playerAnswrCounter = 0
        self.lock = Lock()
        self.gameOver = False

    def incrementCounter(self):
        self.playerAnswrCounter += 1

    def generateMathProblem(self):
        x = random.randint(1, 4)
        y = random.randint(1, 4)
        self.mathProblem = '''Welcome to Quick Maths.\nPlayer 1: {p1}\nPlayer 2: {p2}\n==
Please answer the following question as fast as you can:
How much is {op1} + {op2}?'''.format(op1=x, op2=y, p1=self.lPlayers[0].teamName, p2=self.lPlayers[1].teamName)
        self.correctAnswer = x + y
        return self.mathProblem


    def setSummary(self, i):
        # when some player responded in under than 10 secs
        #if isinstance(self.winner, player):
        try:
            ansRcvd = '''Game over!
    The correct answer was {correctAns}!
                        
    Congratulations to the WINNER: {winner}'''.format(winner=self.winner.teamName, correctAns=self.correctAnswer)

            # when 10 secs passes and none of the players responded
            noAnsRcvd = '''Game over!
            The correct answer was {correctAns}!
            
            It seems you were both equally slow ;)              
            game result: DRAW                       
            '''.format(correctAns=self.correctAnswer)

            if i == 10:
                self.summary = noAnsRcvd
            elif self.playerAnswer and self.winner:
                self.summary = ansRcvd
            else:
                self.summary = noAnsRcvd
        except Exception as err:
            print(err)

    def setWinner(self, answer, AnsweringPlayer):
        try:
            if self.correctAnswer == int(answer):
                self.winner = AnsweringPlayer
            else:
                otherIndex = abs(AnsweringPlayer.index - 1)
                self.winner = self.lPlayers[otherIndex]
        except Exception as err:
            print(err)

    def play(self, index):
        try:
            player = self.lPlayers[index]
            print(f"Hi, I am client {player.teamName}\n")

            # send the welcome message + math problem to player
            try: #  AttributeError: 'NoneType' object has no attribute 'encode'
                player.clientSocket.send(self.mathProblem.encode())
            except Exception as err:
                print(err)
                while self.mathProblem is None:
                    time.sleep(1)
                try:
                    player.clientSocket.send(self.mathProblem.encode())
                except Exception as err:
                    pass

            # recv answer from one of the players
            myans = None
            player.clientSocket.settimeout(2)
            print(f"\nplayer {player.teamName}: game.playerAnswer = {game.playerAnswer}")
            j=0
            while game.playerAnswer is None and not self.gameOver: #if someone already answered, server stops receiving (skip loop)
                print(f"play {player.teamName}: loop number {j}")
                j+=1
                try:
                    myans = player.clientSocket.recv(1024)
                except socket.timeout:
                    continue
                if myans and game.playerAnswer is None and not game.lock.locked():
                    myans = myans.decode()
                    player.answer = myans
                    print(f"func 'clientThread': client_{player.teamName}_ans={myans} => success! recieved char from client over TCP... the method of global vars doesn't work")
                    # todo Test this mutex shenanigans, change to counter method if doesn't work
                    try:
                        game.lock.acquire(timeout=2) # blocking until getting the lock or for up to 2 seconds
                        game.playerAnswer = myans
                        game.setWinner(myans, player)
                    except Exception as err:
                        print(err)
                    finally:
                        try:
                            game.lock.release()
                        except Exception as err:
                            print(err)
        except IOError as msg:
            print("Client thread: Error: ",msg)
            traceback.print_exc()
        except Exception:
            traceback.print_exc()



    def countdown10(self):
        i = 0
        while i < 10 and self.playerAnswer is None:
            print("start count 10sec == " + str(i))
            i += 1
            time.sleep(1)
        self.gameOver = True

        noAnsRcvd = '''Game over!
            The correct answer was {correctAns}!
            
            It seems you were both equally slow ;)              
            game result: DRAW                       
            '''.format(correctAns=self.correctAnswer)
        if i == 10:
            self.summary = noAnsRcvd
        return i


def udp_start(msg, clientPort,udp_socket):
    '''
    :param msg: udp broadcast msg
    :param ip: my ip
    :param clientPort: client port 13117
    :param udp_socket:  my computer udp socket
    '''
    global nThreadsForUDP
    nThreadsForUDP = 0
    # run main udp thread calling for 2 players stop after get 2 players runing every 1sec and stop after he find 2 players
    while nThreadsForUDP < 2:
        print("sending UDP broadcast every 1sec or until 2 clients join the game", end='\n')
        # Broadcast to everyone (not to a specific IP)
        udp_socket.sendto(msg, ('<broadcast>', clientPort))
        time.sleep(1) # send every 1 sec


# configure ip and ports on REMOTE
# interface="eth1" # test_net = eth2
# serverIP = get_if_addr(interface)

# configure ip and ports on LOCAL
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
tcpSock.listen(5) # 2 is num of UNaccepted connections allowed before server refuses connections

# start the udp thread
#todo Move this to the main service loop - the server sends offers again once game is over
udpThread = Thread(target=udp_start, args =[msg, clientPort, udpSocket])
udpThread.start()
print("\nmain thread: started UDP thread, server is now broadcasting offers (udp)")
print(f"\nServer started, listening on IP address {serverIP}")

# server alawys run and looking for players
game = None
while True:
    if game is None:
        game = Game()

    try:
        (clientSocket, (clientIP, clientPORT)) = tcpSock.accept()
        playerName = clientSocket.recv(1024).decode().strip('\n')
        print("line after clientSocket.recv reached")
        playerIdx = len(game.lThreads) # get len before appending new thread

        game.lPlayers.append(player(playerName, playerIdx, clientIP, clientPORT, clientSocket))
        print(f'\nClient {game.lPlayers[playerIdx].teamName}: clientIp={clientIP}, clientPort={clientPORT}')

        newthread = Thread(target=game.play , args=[playerIdx])
        game.lThreads.append(newthread)
        nThreadsForUDP = len(game.lThreads)
    except socket.timeout:
        print("time out Team not send name")
        try:
            clientSocket.close()
        except Exception as err:
            pass

    if len(game.lThreads) == 2:
        game.generateMathProblem()
        print(f"math problem = {game.mathProblem}")
        game.lThreads[0].start()
        game.lThreads[1].start()
        print("\n Two player threads started")
        timeElapsed = game.countdown10() # sends summary to both players, does NOT close the tcp connections

        game.lThreads[0].join()
        game.lThreads[1].join()

        game.setSummary(timeElapsed)
        # send summary to both players and close the connection
        encodedSummary = game.summary.encode()
        for p in game.lPlayers:
            p.clientSocket.send(encodedSummary)
            print(f"sent summary to client {p.teamName}")
            time.sleep(0.5)
            p.closeTcpConn()
        game = None
        udpThread = Thread(target=udp_start, args =[msg, clientPort, udpSocket])
        udpThread.start()
        print("Game over, sending out offer requests...")








