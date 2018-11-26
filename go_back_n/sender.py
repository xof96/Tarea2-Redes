import os
import sys
import socket
import threading
import time

from utils.conn import sender_handshake_conn

BUF = 1024
TIMEOUT = 10
INTERVAL_TIME = 0.01
MAX_RTM = 5
WINDOWS_SIZE = 5
WINDOWS_BEGINNING = 0
MAX_SEQ_NUM = WINDOWS_SIZE + 1
LEN_PACKETS = 0

# mutex = threading.Lock()
packets_indexes = []


def receive_ack(a_socket):
    global WINDOWS_BEGINNING

    while True:
        ack_data, receiver = a_socket.recvfrom(BUF)
        ack = ack_data.decode().split('|||')[0]
        if ack == '':
            break

        ind = packets_indexes[WINDOWS_BEGINNING:].index(int(ack)) + WINDOWS_BEGINNING

        if ind + 1 + WINDOWS_SIZE <= LEN_PACKETS:
            WINDOWS_BEGINNING = ind + 1
    return 0


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
    data = str(file_name) + "|||" + str(total_size) + "|||" + str(MAX_SEQ_NUM)
    the_socket.sendto(data.encode(), address)

    # Armar paquetes
    packets = []
    seq_num = 1
    d_time = 0  # Measures the time

    ack_from_header = the_socket.recvfrom(BUF)[0]
    if ack_from_header.decode() != '0':
        raise Exception("Error Reqlo")

    while True:
        data = sending_file.read(BUF - 1)
        if not data:
            break
        data_buf = str(data.decode()) + str(seq_num)
        packets.append(data_buf.encode())
        packets_indexes.append(seq_num)
        seq_num = (seq_num + 1) % MAX_SEQ_NUM

    LEN_PACKETS = len(packets)

    # print("Voy a lanzar el thread")
    t = threading.Thread(target=receive_ack, args=[the_socket])
    t.start()

    while WINDOWS_BEGINNING + WINDOWS_SIZE <= LEN_PACKETS:
        start_time = 0  # Placeholder
        windows_tale = WINDOWS_BEGINNING

        if d_time >= TIMEOUT:
            seq = WINDOWS_BEGINNING

        while seq < WINDOWS_BEGINNING + WINDOWS_SIZE:
            the_socket.sendto(packets[seq], address)
            # print(WINDOWS_BEGINNING)
            # print("Envié el paquete %s" % seq)
            time.sleep(INTERVAL_TIME)

            if WINDOWS_BEGINNING == windows_tale:
                # Seteamos un timeout (bloqueamos el socket después de 0.5s)
                # the_socket.settimeout(TIMEOUT)
                start_time = time.time()
                # print(start_time)

            current_size += len(packets[seq])
            percent = round(float(current_size) / float(total_size) * 100, 2)
            print(str(current_size) + " / " + str(total_size) + "(current size / total size), " + str(
                    percent) + "%")

            # Actualizamos el número de secuencia
            seq += 1

        d_time = time.time() - start_time
        # print(d_time)

        while d_time < TIMEOUT and WINDOWS_BEGINNING == windows_tale:
            # print(time.time() - start_time)
            # print("WindowsBeginning", WINDOWS_BEGINNING)
            # print("WindowsTale", windows_tale)
            continue
