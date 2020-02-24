import io
import os
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread


def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Type your name and press enter!", "utf-8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client, client_address)).start()


def pubkey_dictionary(name):
    if not os.path.exists("ServerDictionary"):
        os.mkdir("ServerDictionary")
    if os.path.exists("Dictionary"):
        for file in os.listdir("Dictionary"):
            filepath = os.path.join("Dictionary", name)
            filepath = os.path.join(filepath, name + '_public_key.pem')
            if not os.path.isdir(filepath):
                p =os.path.join("ServerDictionary", name + '_public_key.pem')
                pathfile = io.open(filepath, "rb").read()
                f = io.open(p, "wb").write(pathfile)


def handle_client(client, client_address):
    name = client.recv(BUFSIZ).decode("utf-8")
    ip, port = client_address
    welcome = 'Welcome to the group %s' % name
    pubkey_dictionary(name)
    client.send(bytes(welcome, "utf-8"))
    msg = "%s has joined the chat!" % name
    pubkey_dictionary(name)
    broadcast(bytes(msg, "utf-8"))
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ)

        if msg != bytes("*QUIT*", "utf-8"):

            broadcast(msg, name+":::")

        else:
            client.close()
            del clients[client]
            broadcast(bytes("%s has left the chat." % name, "utf-8"))
            break


def broadcast(msg, prefix=""):
    """Broadcasts a message to all the clients."""

    for sock in clients:
        sock.send(bytes(prefix, "utf-8")+msg)


clients = {}
addresses = {}

HOST = 'localhost'
PORT = 6000
BUFSIZ = 8192
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
