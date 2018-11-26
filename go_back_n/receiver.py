import socket
import sys

from utils.conn import receiver_handshake_conn

BUF = 1024
MAX_SEQ_NUM = 0

ack = 0
current_size = 0
percent = round(0, 2)

if __name__ == '__main__':

    # Verificamos que vengan los parámetros.
    if len(sys.argv) != 2:
        print("python receiver.py [PORT_NUMBER]")

    SW_IP = ""
    SW_PORT = int(sys.argv[1])

    # Armamos el socket.
    the_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Asociamos el socket a la dirección y el puerto especificados.
    the_socket.bind((SW_IP, SW_PORT))

    # Establecemos los parámetros.

    if not receiver_handshake_conn(the_socket, BUF, 3):
        raise Exception('Error qlo')

    data, sender = the_socket.recvfrom(BUF)

    if data:
        # Separamos los datos recibidos
        (file_name, total_size, max_num_seq) = data.decode().split("|||")
        MAX_SEQ_NUM = max_num_seq

        # Si recibimos los datos que esperabamos guardamos el archivo

        downloading_file = open("received_" + file_name, "wb")
        # Mostramos el avance
        print(str(current_size) + " / " + str(total_size) + " (current size / total size), " + str(percent) + "%")

        # Enviamos el ack
        the_socket.sendto(str(ack).encode(), sender)

    curr_seq = 0

    while True:
        data, sender = the_socket.recvfrom(BUF)
        print(data.decode())
