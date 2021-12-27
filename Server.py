import socket
import time
import struct
import random
from threading import Thread
from collections import OrderedDict

import scapy

def run(clientSocket,index):
    '''
    :param clientSocket:  socket connect to player
    :param index: first or sec player to join game
    this function send to player msg, and get from him msg to the global vars
    :return:
    '''
    try:
        while True:
            print(index)
            #send the team name to server
            clientSocket.send(qes.encode())
            #recv answer from client and put it into dictionary [teamname] = answer
            myans = clientSocket.recv(1024).decode()
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




# configur of ip and ports
hostname = socket.gethostname()
ip =  socket.gethostbyname(hostname)
clientPort=13117
            # create udp socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((ip, 0))
myPort = udp_socket.getsockname()[1]
            #create tcp socket
tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind((ip,0))
myPortTcp = tcpsock.getsockname()[1]

# global vars

summary=""
threads = []
tcpsock.listen(2)
print(f'Server started, listening on IP address {ip}')
msg = "offer,"+str(myPortTcp)
teamNames = []
answer = False
clientAns = OrderedDict()
result = 2
lock = True


def udp_start(msg,ip, clientPort,udp_socket):
    '''
    :param msg: udp broadcast msg
    :param ip: my ip
    :param clientPort: client port 13117
    :param udp_socket:  my computer udp socket
    '''
   # run main udp thread calling for 2 players stop after get 2 players runing every 1sec and stop after he find 2 players
    while(len(threads)<2):
            print("runing")
            udp_socket.sendto(msg.encode(), (ip, clientPort))
            time.sleep(1)

                # start the udp trade
udtThreadFunction = udp_start
udtthread = Thread(target=udtThreadFunction, args =[msg,ip,clientPort,udp_socket])
udtthread.start()
print("ssss")

# server alawys run and looking for players
while True:
    (clientSocket, (ip,port)) = tcpsock.accept()
    teamName = clientSocket.recv(1024).decode().strip('\n')
    teamNames.append(teamName)
    runt = run
    newthread = Thread(target=runt , args=[clientSocket,len(threads)])
    threads.append(newthread)
    if(len(threads)==2):
        qes = (f"Welcome to Quick Math." +'\n'+ "Player 1 : "+teamNames[0] +'\n' + "Player 2 : " + teamNames[1] + '\n' "===" +'\n' "Please answer the following question as fast as you can:" +'\n'+ "How much is 2+2  ?" )
        threads[0].start()
        threads[1].start()
        print("here")

        qes = (f"Welcome to Quick Math." +'\n'+ "Player 1 : "+teamNames[0] +'\n' + "Player 2 : " + teamNames[1] + '\n' "===" +'\n' "Please answer the following question as fast as you can:" +'\n'+ "How much is 2+2  ?" )
        i = 0
#TODO ITS NEED TO BE i= 10, I CHANGED IT TO 3 TO MAKE TEST EASIER
        while(i<3 and answer == False):
            print("start count 10sec == "+str(i))
            i+=1
            time.sleep(1)
            if answer == False:
                summary = "Game Finish With Draw"
            if(i == 2):
                lock = False

        if(answer == True):
            key = list(clientAns.keys())[0]
            otherTeam = teamNames[1]  if teamNames[0] == key else teamNames[0]
            summary = "Game Over" + '\n' "The corrent answer was 4!" '\n' + "Congratulations to the winner: "+ key if(clientAns[key] == 4) else "Game Over" + '\n' "The corrent answer was 4!" '\n' + "Congratulations to the winner: "+otherTeam


        lock = False
        time.sleep(1)
        threads.clear()
        answer = False





