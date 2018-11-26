import os
import sys
import socket
import threading
import time

from utils.conn import sender_handshake_conn

BUF = 1024
TIMEOUT = 0.5
MAX_RTM = 5
WINDOWS_SIZE = 5
SEQ_LIMIT = WINDOWS_SIZE + 1


def receive_ack(a_socket):
    return a_socket


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

    # Parámetros
    seq = 0

    # Obtenemos los parámetros del archivo a enviar
    file_name = sys.argv[3]
    total_size = os.path.getsize(file_name)
    current_size = 0
    percent = round(0, 2)

    # Abrimos el archivo
    sending_file = open(file_name, "rb")

    # 'Codificamos' el header
    data = str(file_name) + "|||" + str(total_size) + "|||" + str(seq)

    while True:
        n_packet = 0

        while n_packet < WINDOWS_SIZE:
            the_socket.sendto(data.encode(), address)
            time.sleep(0.01)

            if seq == 0:
                # Seteamos un timeout (bloqueamos el socket después de 0.5s)
                the_socket.settimeout(TIMEOUT)

            # Actualizamos el número de secuencia
            seq = (seq + 1)

            # (**) Actualizamos los parámetros :
            data = sending_file.read(BUF - 1)
            current_size += len(data)
            percent = round(float(current_size) / float(total_size) * 100, 2)

            # Si no hay datos mandamos un string vacío y dejamos de enviar cosas
            if not data:
                the_socket.sendto("".encode(), address)
                break

            # Actualizamos los datos a enviar
            data = data.decode()
            data += str(seq)
            n_packet += 1

        threading.Thread(receive_ack, args=the_socket)

