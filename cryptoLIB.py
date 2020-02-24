from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os
import os.path
import io
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from base64 import b64encode, b64decode


def save_file(your_data):
    f = open("signature.sig", 'w+').write(your_data)


def file_as_bytes(file):
    if os.path.exists(file) and not os.path.isdir(file):
        filer = io.open(file, 'rb')
        with filer:
            return filer.read()


def file_read(file):
    if os.path.exists(file) and not os.path.isdir(file):
        filer = io.open(file, 'r')
        with filer:
            return filer.read()


def sign_message(message, name):
    try:
        m = message
        h = SHA256.new(m)
        path = os.path.join("Dictionary", name)
        path = os.path.join(path, name + '_private_key.pem')
        key = RSA.import_key(open(path).read())
        signature = pkcs1_15.new(key).sign(h)
        return signature
    except FileNotFoundError as fnf:
        print(fnf)


def verify_signature(signature, name, message):
    try:
        path = os.path.join("ServerDictionary")
        path = os.path.join(path, name + '_public_key.pem')
        key = RSA.import_key(open(path).read())
        hn = SHA256.new(message)
        verifier = pkcs1_15.new(key)
        verifier.verify(hn, signature)
        out = name
        return out
    except Exception as ex:
        print(ex)


def read_folder_main_db():
    pubkey_list = []
    if os.path.exists("ServerDictionary"):
        for file in os.listdir("ServerDictionary"):
            filepath = os.path.join("ServerDictionary", file)
            if not os.path.isdir(filepath):
                pubkey_list.append(filepath)

    return pubkey_list


def encrypt(message):
    encryptedList = []
    message = message.encode()
    for recipient_name in read_folder_main_db():
        try:
            path = recipient_name
            key = RSA.import_key(open(path).read())
            cipher = PKCS1_OAEP.new(key)
            ciphertext = b""
            offset = 0
            chunk_size = 128

            while offset < len(message):
                chunk = message[offset:offset + chunk_size]

                if len(chunk) % chunk_size != 0:
                    chunk += b" " * (chunk_size - len(chunk))

                ciphertext += cipher.encrypt(chunk)
                offset += chunk_size
            encryptedList.append(ciphertext)
        except Exception as ex:
            print(ex)
    return encryptedList


def decrypt(message, my_name):
    try:
        path = os.path.join("Dictionary", my_name)
        path = os.path.join(path, my_name + '_private_key.pem')
        key = RSA.import_key(open(path).read())
        cipher = PKCS1_OAEP.new(key)

        chunk_size = 256
        offset = 0
        plaintext = b""

        while offset < len(message):
            plaintext += cipher.decrypt(message[offset:offset + chunk_size])
            offset += chunk_size

        return plaintext
    except Exception as ex:
        print(ex)


