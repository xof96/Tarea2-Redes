import os
import sys
import socket

from utils.conn import sender_handshake_conn

BUF = 1024
MAX_RTM = 5

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
