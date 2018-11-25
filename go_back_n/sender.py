import os
import sys
import socket, threading
import time

from utils.conn import sender_handshake_conn

BUF = 1024
WINDOW_SIZE = 5
TIMEOUT = 500
WINDOW_BEGINNING = 0


def recACK(rec_address, sock):
    global  WINDOW_BEGINNING
    while True:
        data, address = sock.recvfrom(BUF)
        ACK, seq = data.decode().split("|||")
        WINDOW_BEGINNING = int(seq)


if __name__ == '__main__':

    # Verificamos que vengan los parámetros.
    if len(sys.argv) != 4:
        print("python sender.py [IP_ADDRESS] [PORT_NUMBER] [FILE_NAME]")
        sys.exit(0)

    # Armamos el socket
    the_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Obtenemos el puerto y la IP
    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])

    # Se arma la dirección
    address = (server_ip, server_port)

    if not sender_handshake_conn(the_socket, address, BUF, 3):
        raise Exception('Error qlo')

    # Obtenemos los parámetros del archivo a enviar
    file_name = sys.argv[3]
    total_size = os.path.getsize(file_name)
    current_size = 0
    percent = round(0, 2)

    # Abrimos el archivo y enviamos encabezado
    sending_file = open(file_name, "rb")
    data = str(file_name) + "|||" + str(total_size)
    the_socket.sendto(data.encode(), address)
    # ponerle ack al receiver

    # Se arman los paquetes a enviar
    blocks = []
    nseq = 0
    while True:
        block = sending_file.read(BUF)
        if not block:
            break
        blocks.append(block + "|||" + str(nseq))
        nseq += 1

    ### En esta linea debe iniciarse el thread que escucha al culiao ###
    # Se envian paquetes
    enviar = 0
    while (WINDOW_BEGINNING < nseq):
        while (enviar < WINDOW_BEGINNING + WINDOW_SIZE):
            the_socket.sendto(blocks[enviar].encode(), address)
            enviar += 1
        timeout_beginning = time.time()
        actual_beginning = WINDOW_BEGINNING
        dif = 0
        while (dif < TIMEOUT or actual_beginning != WINDOW_BEGINNING):
            dif = time.time() - timeout_beginning
        if dif >= TIMEOUT:
            enviar = WINDOW_BEGINNING
