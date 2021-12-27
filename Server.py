import socket
import time
import struct
import random
from threading import Thread

import scapy


class MyThread(Thread):

    def __init__(self, ip, clientPort,clientSocket,index):
        Thread.__init__(self)
        self.ip = ip
        self.clientPort = clientPort
        self.stop = True
        self.clientSocket = clientSocket
        self.index = index+1


    def run(self):
        try:
            while self.stop:
                print(self.index)
                clientSocket.send(qes.encode())
                myans = clientSocket.recv(1024).decode()
                clientAns[self.index] = myans
                global answer
                answer = True
                while lock:
                    pass
                clientSocket.send(summary.encode())
                clientSocket.close()
        except IOError:
            print("IOE Error threade")
        finally:clientSocket.close()





summary=""
hostname = socket.gethostname()
ip =  socket.gethostbyname(hostname)
clientPort=13117
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((ip, 0))
myPort = udp_socket.getsockname()[1]
tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind((ip,0))
myPortTcp = tcpsock.getsockname()[1]

threads = []
tcpsock.listen(2)
print(f'Server started, listening on IP address {ip}')
msg = "offer,"+str(myPortTcp)
teamNames = []
answer = False
clientAns = {}
result = 2
def udp_start(msg,ip, clientPort,udp_socket):
    while(len(threads)<2):
            print("runing")
            udp_socket.sendto(msg.encode(), (ip, clientPort))
            time.sleep(1)


udtThreadFunction = udp_start
udtthread = Thread(target=udtThreadFunction, args =[msg,ip,clientPort,udp_socket])
udtthread.start()
print("ssss")
while True:
    (clientSocket, (ip,port)) = tcpsock.accept()
    teamName = clientSocket.recv(1024).decode().strip('\n')
    teamNames.append(teamName)
    newthread = MyThread(ip, port, clientSocket, len(threads))
    threads.append(newthread)

    if(len(threads)==2):
        lock = True
        qes = (f"Welcome to Quick Math." +'\n'+ "Player 1 : "+teamNames[0] +'\n' + "Player 2 : " + teamNames[1] + '\n' "===" +'\n' "Please answer the following question as fast as you can:" +'\n'+ "How much is 2+2  ?" )
        threads[0].start()
        threads[1].start()
        qes = (f"Welcome to Quick Math." +'\n'+ "Player 1 : "+teamNames[0] +'\n' + "Player 2 : " + teamNames[1] + '\n' "===" +'\n' "Please answer the following question as fast as you can:" +'\n'+ "How much is 2+2  ?" )
        i = 0
        while(i<10 and answer == False):
            i+=1
            time.sleep(1)
            if answer == False:
                summary = "Game Finish With Draw"

        if(answer == True):
            if(clientAns[teamNames[0]] != clientAns[teamNames[1]] and clientAns[teamNames[0]] == result):
                summary = "Game Over" + '\n' "The corrent answer was 4!" '\n' + "Congratulations to the winner: "+ teamNames[0]
            if(clientAns[teamNames[0]] != clientAns[teamNames[1]] and clientAns[teamNames[1]] == result):
                summary = "Game Over" + '\n' "The corrent answer was 4!" '\n' + "Congratulations to the winner: "+ teamNames[1]
            elif (clientAns[teamNames[0]] == clientAns[teamNames[1]] and clientAns[teamNames[1]] != result):
                summary = "Game Finish With Draw"
            elif (clientAns[teamNames[0]] == clientAns[teamNames[1]] and clientAns[teamNames[1]] == result):
                summary = "Game Finish With Draw"
            lock = False
        threads.clear()
        answer = False





