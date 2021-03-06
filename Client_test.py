# library for socket programming
import socket
# library for threading
import threading
# library to get time stamp
from datetime import datetime
# library to get current thread method of threading
from threading import current_thread

class Client:
    def __init__(self):
        # socket parameter to connect over TCP
        self.client_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print self.client_connect
        server_host = '127.0.0.1'
        server_port = 80
        # connect to the server over localhost and port 80
        self.client_connect.connect((server_host, server_port))
        print 'connected to the server'
        # getting the user name from the user
        self.user_name = raw_input("Enter your username: ")
        # send the user name to the server in the PUT format
        self.client_connect.send(self.user_name)

    def get_input(self):
        # getting the message format
        message_start = "GET http://localhost:80/"
        message_end = " HTTP/1.1"

        # getting the hostname from the user
        self.dest_hostname = raw_input("Enter Destination username: ")
        # sending the destination hostname to the server in the PUT format
        self.client_connect.send(self.dest_hostname)
        # receive data from the server
        present = self.client_connect.recv(1024)
        if present == "0":
            print self.dest_hostname+' not available/registered'
            return None
        elif present == "2":
            print self.user_name + " already logged in!"
            return None
        else:
            # creating a separate thread to listen to the data sent by the server
            threading.Thread(target=self.listen_continously, args=()).start()
            # the chat section to get input from the user and send it to the server
            message = raw_input("Enter your message and type exit to quit: ")
            message_size = len(message)
            date = datetime.now()
            while True:
                message_body = "\nDate: " + str(date) + "\nContent-Length: " + str(message_size)
                if message == "exit":
                    self.client_connect.send(message_start + "exit" + message_end + message_body)
                    self.client_connect.close()
                    print 'Stopping input'
                    return None
                else:
                    self.client_connect.send(message_start + message + message_end + message_body)
                message = raw_input(">")
                message_size = len(message)
                date = datetime.now()

    def listen_continously(self):
        print 'Listening: '
        while True:
            try:
                data = self.client_connect.recv(1024)
                if data == "unexpected":
                    print self.dest_hostname + " disconnected unexpectedly."
                if data:
                    req_data = (data.split('/')[3]).split(" HTTP")[0]
                    date = (data.split('\n')[1]).split("Date: ")[1]
                    print "(" + date + "): " + self.dest_hostname + ": " + req_data
                    #print self.dest_hostname + ": " + req_data
                    if req_data == "exit":
                        print self.dest_hostname + ' disconnected'
                        break
                else:
                    self.client_connect.close()
            except:
                print str(current_thread()) + self.dest_hostname + " disconnected unexpectedly"
                #self.client_connect.close()
                return False


if __name__ == "__main__":
    client = Client()
    client.get_input()