import os
import sys
import socket
import threading
import time

from utils.conn import sender_handshake_conn, sender_leaves_conn
from utils.timeout import timeout_calc

BUF = 1024
TIMEOUT = 1
INTERVAL_TIME = 0.01
MAX_RTM = 5
WINDOWS_SIZE = 5
WINDOWS_BEGINNING = 0
WINDOWS_HAS_MOVED = True
MAX_SEQ_NUM = WINDOWS_SIZE + 1
LEN_PACKETS = 0
FINISHED = False

mutex = threading.Lock()
packets_indexes = []


def receive_ack(a_socket):
    global WINDOWS_BEGINNING, FINISHED, WINDOWS_HAS_MOVED

    while True:
        ack_data, receiver = a_socket.recvfrom(BUF)
        ack = ack_data.decode()
        if ack == '':
            break
        ind = packets_indexes[WINDOWS_BEGINNING:].index(int(ack)) + WINDOWS_BEGINNING
        if ind == LEN_PACKETS - 1:
            mutex.acquire()
            FINISHED = True
            mutex.release()
            break
        else:
            if ind + 1 + WINDOWS_SIZE <= LEN_PACKETS:
                WINDOWS_BEGINNING = ind + 1
                mutex.acquire()
                WINDOWS_HAS_MOVED = True
                mutex.release()
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
        raise Exception('Error en handshake')

    TIMEOUT=timeout_calc(the_socket,address)
    print(TIMEOUT)

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
        raise Exception("Error en envío de header")

    while True:
        data = sending_file.read(BUF - 1)
        if not data:
            break
        data_buf = str(data.decode()) + str(seq_num)
        packets.append(data_buf.encode())
        packets_indexes.append(seq_num)
        seq_num = (seq_num + 1) % MAX_SEQ_NUM

    LEN_PACKETS = len(packets)

    t = threading.Thread(target=receive_ack, args=[the_socket])
    t.start()

    mutex.acquire()
    while not FINISHED:
        mutex.release()
        start_time = 0  # Placeholder

        if d_time >= TIMEOUT:
            seq = WINDOWS_BEGINNING

        while seq < WINDOWS_BEGINNING + WINDOWS_SIZE:
            the_socket.sendto(packets[seq], address)
            time.sleep(INTERVAL_TIME)

            if WINDOWS_HAS_MOVED:
                start_time = time.time()
                mutex.acquire()
                WINDOWS_HAS_MOVED = False
                mutex.release()

            current_size += len(packets[seq]) - 1
            percent = round(float(current_size) / float(total_size) * 100, 2)
            print(str(current_size) + " / " + str(total_size) + "(current size / total size), " + str(percent) + "%")

            # Actualizamos el número de secuencia
            seq += 1

        mutex.acquire()
        while d_time < TIMEOUT and not WINDOWS_HAS_MOVED:
            mutex.release()
            d_time = time.time() - start_time
            mutex.acquire()

    mutex.release()
    t.join()
    if not sender_leaves_conn(the_socket, address, BUF, 3):
        print("No se pudo cerrar la conexión")
    sending_file.close()
    the_socket.close()
