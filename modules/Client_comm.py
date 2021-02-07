import socket

SRV_IP = "192.168.1.100"
SRV_PORT = 40000


class ClientComm():

    def __init__(self):

        # set server socket to listen and talk to clients
        self.com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.com.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.conn_established = False

    def conn_to_server(self):

        self.com.connect((SRV_IP, SRV_PORT))

        welc_msg = self.com.recv(8).decode("utf-8")

        if welc_msg == "AUTH  OK":
            self.conn_established = True

    def send_to_server(self, mess):

        if self.conn_established:

            self.com.send(f'DATA{len(mess):<4}' + mess)
        else:
            print("Data was tried to send, but connection is not established")