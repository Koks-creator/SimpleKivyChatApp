import socket
import select

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((IP, PORT))

server_socket.listen()

sockets_list = [server_socket]

clients = {}

print("Starting...")


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)

        if not len(message_header):#sprawdza czy jest wiadomosc
            return False
        message_length = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}
    except:
        return False

while True:
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)#rzecz z ktorej czytamy, rzecz do ktorej zaposujemy, rzecz ktora moze sie zjebac

    for notified_socket in read_sockets:#If the notified socket is our server socket, then this means we just got a new connection, which we want to handle for.
        if notified_socket == server_socket:#czy sie ktos polaczyl
            client_socket, client_adress = server_socket.accept()#So with client_socket, client_address = server_socket.accept() we get that unique client socket and their address

            user = receive_message(client_socket)
            if user is False:#Czyli czy sie rozłączył
                continue

            sockets_list.append(client_socket)

            clients[client_socket] = user
            print(f"Accepted new connection from {client_adress[0]}{client_adress[1]} username: {user['data'].decode('utf-8')}")

        else:

            message = receive_message(notified_socket)

            if message is False:
                print(f"Closed conncetion from {clients[notified_socket]['data'].decode('utf-8')}")
                sockets_list.remove(notified_socket)
                del clients[notified_socket]
                continue

            user = clients[notified_socket]
            print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

            for client_socket in clients:
                if client_socket != notified_socket:
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notified_socket in exception_sockets:
        sockets_list.remove(notified_socket)
        del clients[notified_socket]
#https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/