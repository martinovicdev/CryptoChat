import io
import os
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter
from Crypto.PublicKey import RSA
import random
import cryptoLIB as krip
from base64 import b64encode, b64decode

RANDOM_NUMBER = 0
SAVE_PRIVATE_PUBLIC_KEY = 0
USERNAME = ""
RECIEVE = 0


def generate_rsa(name, bits=2048):
    global RANDOM_NUMBER
    RANDOM_NUMBER = random.randint(100, 999)
    new_key = RSA.generate(bits)
    public_key = new_key.publickey().exportKey("PEM")
    private_key = new_key.exportKey("PEM")

    if not os.path.exists("Dictionary"):
        os.mkdir("Dictionary")

    path = os.path.join("Dictionary/"+name+str(RANDOM_NUMBER))
    if not os.path.exists(path):
        os.mkdir(path)

    pathpub = os.path.join(path, name+str(RANDOM_NUMBER)+"_public_key.pem")
    pathpriv = os.path.join(path, name+str(RANDOM_NUMBER)+"_private_key.pem")
    public = io.open(pathpub, 'wb').write(public_key)
    private = io.open(pathpriv, 'wb').write(private_key)
    return name+str(RANDOM_NUMBER)


def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf-8")

            user_message = msg.split(":::")

            username = ""
            chat_start = False

            if len(user_message) > 1:
                username = user_message[0]
                message = user_message[1]
                poruke = message
                chat_start = True

                poruke = b64decode(poruke)

                message = poruke[256:]
                signature = poruke[0:256]

                username = krip.verify_signature(signature, username, message)
                msg = krip.decrypt(message, USERNAME)

                username = username + ": "

            if msg != None and chat_start:
                msg_list.insert(tkinter.END, username+str(msg)[2:])
                msg_list.yview("end")
            elif msg != None:
                msg_list.insert(tkinter.END, username + str(msg))
                msg_list.yview("end")

        except OSError:
            break


def send(event=None):
    msg = ""
    if my_msg.get() == "":
        pass
    else:
        global SAVE_PRIVATE_PUBLIC_KEY
        global USERNAME
        if SAVE_PRIVATE_PUBLIC_KEY == 0:
            SAVE_PRIVATE_PUBLIC_KEY = 1
            username = ''.join(my_msg.get().split())
            codename = generate_rsa(username)
            USERNAME = codename
            msg = codename
            my_msg.set("")
            client_socket.send(bytes(msg, "utf-8"))
        else:
            msg = my_msg.get()
            if msg == "*QUIT*":
                client_socket.send(bytes(msg, "utf-8"))
                client_socket.close()
                top.quit()
            else:
                msg = krip.encrypt(msg)
                my_msg.set("")
                for poruka in msg:
                    signature = krip.sign_message(poruka, USERNAME)
                    client_socket.send(b64encode(signature+poruka))


def on_closing(event=None):
    my_msg.set("*QUIT*")
    send()


top = tkinter.Tk()
top.title("RSA CHAT")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()
my_msg.set("")
scrollbar = tkinter.Scrollbar(messages_frame)
my_color= '#%02x%02x%02x' % (30, 30, 30)
font = '#%02x%02x%02x' % (0, 255, 102)
msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set,background =my_color,foreground=font)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()

messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send, bg="green", fg="white")
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)


HOST = "localhost"
PORT = 6000
if not PORT:
    PORT = 6000
else:
    PORT = int(PORT)

BUFSIZ = 8192
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
try:
    tkinter.mainloop()
except:
    pass
