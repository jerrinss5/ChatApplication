# code ref: https://stackoverflow.com/questions/23828264/how-to-make-a-simple-multithreaded-socket-server-in-python-that-remembers-client
# library for socket connection
import socket
# library to get the threads
import threading
# library to get current thread method of threading
from threading import current_thread
# library to get time stamp
from datetime import datetime
import time


class ThreadedServer(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.user_dict = {}
        self.user_sock = {}
        # AF_INET = TCP
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # allowing the socket to be reused
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # binding the socket
        self.sock.bind((self.host, self.port))

    def listen(self):
        # setting the maximum number of clients
        self.sock.listen(6)
        print 'waiting for clients to connect'
        # in loop keep listening for new clients
        while True:
            # accepting the client
            client, address = self.sock.accept()
            # client.settimeout(60)
            # creating a new thread for every client that connects to the server
            threading.Thread(target=self.listen_to_client, args=(client, address)).start()

    def listen_to_client(self, client, address):
        try:
            # getting the current thread details
            print current_thread()
            # setting the receiving size of data from client as 1024
            size = 1024
            # getting user details from the client
            user = client.recv(size)
            # marking the user as active if it is already present
            if user in self.user_dict:
                # getting the value of user for further checks
                value = self.user_dict[user]
                # user is already registered and logged in to the system
                if value == 1:
                    print str(current_thread()) + " " + user + " already logged in. So Stopping this thread"
                    client.send("2")
                    return None
                else:
                    self.user_dict[user] = 1
            else:
                # user is not in the list adding the user and marking it as active
                self.user_dict[user] = 1
            # storing the socket into the dictionary
            self.user_sock[user] = client
            # getting the desired username to be connected to
            connect_to_user = client.recv(size)
            # check if the user is present in the dictionary
            if connect_to_user in self.user_dict:
                # if present get the active status of the user
                is_active = self.user_dict[connect_to_user]
                client.send("1")
            else:
                client.send("0")
                # marking the user as inactive, since there is no one to talk to
                self.user_dict[user] = 0
                return None
            if not is_active == 1:
                client.send("0")
            else:
                # getting the socket object of the destination host
                connect_to_user_socket = self.user_sock[connect_to_user]
                # keep getting message from the client
                while True:
                    try:
                        print str(current_thread()) + " waiting for data"
                        # get the data
                        data = client.recv(size)
                        print str(current_thread()) + " data received from " + str(user) + " : " + str(data)
                        if data:
                            # give the response from host to destination client
                            actual_data = (data.split('/')[3]).split(" HTTP")[0]
                            message_size = len(actual_data)
                            time.sleep(2)
                            # assign the new time stamp
                            date = datetime.now()
                            # append everything to the message body
                            message_body = "\nDate: " + str(date) + "\nContent-Length: " + str(message_size)
                            # actual data which needs to be sent
                            send_data = (data.split('\n')[0]) + message_body
                            # sending the data through the socket
                            connect_to_user_socket.send(send_data)
                        else:
                            print str(current_thread()) + ' ' + str(user) + ' disconnected'
                            # marking the user as inactive
                            self.user_dict[user] = 0
                            # closing the socket for both the host and the client
                            connect_to_user_socket.close()
                            client.close()
                            return None
                    except:
                        print str(current_thread()) + ' ' + str(user) + ' disconnected unexpectedly'
                        # marking the user as inactive
                        self.user_dict[user] = 0
                        # notifying the user about unexpected closure
                        connect_to_user_socket.send("unexpected")
                        # closing the socket for both the host and the client
                        connect_to_user_socket.close()
                        client.close()
                        return False
        except:
            print 'exception handled'


if __name__ == "__main__":
    # getting the port input from the user
    port_num = input("Port: ")
    # calling the listen function of Threaded server class
    ThreadedServer('',port_num).listen()