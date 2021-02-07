import socket
import select

SRV_PORT = 40000
SRV_IP = "192.168.1.100"
HEADER_LENGTH = 10
# HEADER CONVENTION: XXXXNNNNNN
# XXXX = Info code of the transmitted data
# NNNNNN = Length of the message (prefix with whitespace)

class ServerComm():

    def __init__(self):

        # init socket for server
        self.com = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.com.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.com.bind((socket.gethostname(), SRV_PORT))

        self.conn_clients = dict()
        self.con_sockets = [self.com]

    def add_client(self, address, client_socket):

        self.conn_clients[str(address)] = {"auth": False, "c_socket": client_socket}

    def change_client_state(self, address, n_state):

        if str(address) in self.conn_clients:
            self.conn_clients[str(address)]["auth"] = n_state
            return True
        else:
            return False

    def del_client(self, address):

        if str(address) in self.conn_clients:
            self.conn_clients[str(address)]["c_socket"].close()

        del self.conn_clients[str(address)]

    def receive_message(self, client_socket):
        try:
            mess_header = client_socket.recv(HEADER_LENGTH)
            if not len(mess_header):
                return False
            mess_info = mess_header[0:4].decode("utf-8")
            mess_length = int(mess_header[4:HEADER_LENGTH].decode("utf-8"))
            mess = client_socket.recv(mess_length).decode("utf-8")
            return {"info": mess_info, "m_len": mess_length, "data": mess}
        except:
            return False

    def send_message(self, client_socket, m_info, mess):

        pass

    def start_server(self):

        self.com.listen(5)
        self.isRunning = True

        if self.isRunning:

            clientsocket, addr = self.com.accept()
            print(f'Connection from {addr} has been established')
            self.add_client(addr, clientsocket)

            read_sockets, _, _ = select.select(self.con_sockets, [], self.con_sockets)

            for notified_sockets in read_sockets:
                if notified_sockets == self.com:
                    cl_socket, cl_addr = self.com.accept()

                    self.con_sockets.append(cl_socket)

                    self.conn_clients[notified_sockets] = {"user": cl_addr, "cl_socket": cl_socket}

                    print(f'Accepted new user on server: {cl_addr}')

                else:
                    mess = self.receive_message(notified_sockets)
                    if mess is False:
                        print(f'Closed connection of {notified_sockets}')
                        self.con_sockets.remove(notified_sockets)
                        del self.conn_clients[notified_sockets]
                    print(f'Received message from {notified_sockets}: {mess["data"]}')


class ClientComm():

    def __init__(self):

        self.srv_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_connected = False

    def connect_to_srv(self):

        self.srv_conn.connect((SRV_IP, SRV_PORT))
        self.srv_conn.setblocking(False)
        self.is_connected = True
        return True

    def send_message(self, mess_info: str, mess: str):

        if not mess:
            return False

        if self.is_connected:
            mess_header = (mess_info + f"{len(mess):>{HEADER_LENGTH-4}}").encode("utf-8")
            self.srv_conn.send(mess_header + mess.encode("utf-8"))
            return True
