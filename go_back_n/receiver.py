import socket
import sys

from utils.conn import receiver_handshake_conn

BUF = 1024

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

    ack = 0
    current_size = 0
    percent = round(0, 2)
    can_receive = True

    while True:
        if can_receive:
            data, address = the_socket.recvfrom(BUF)
            data = data.decode()
            # Si no me llegó nada, paramos
            if not data:
                break
            text, seq=data.split("|||")
            seq=int(seq)


