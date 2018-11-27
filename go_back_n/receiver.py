import socket
import sys

from utils.conn import receiver_handshake_conn, receiver_leaves_conn
from utils.timeout import timeout_rec

BUF = 1024
MAX_SEQ_NUM = 0

ack_i = 0
current_size = 0
percent = round(0, 2)
downloading_file = None
total_size = 0

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
        raise Exception('Error en handshake')

    timeout_rec(the_socket)

    data, sender = the_socket.recvfrom(BUF)

    if data:
        # Separamos los datos recibidos
        (file_name, total_size, max_num_seq) = data.decode().split("|||")
        MAX_SEQ_NUM = int(max_num_seq)

        # Si recibimos los datos que esperabamos guardamos el archivo

        downloading_file = open("received_" + file_name, "wb")
        # Mostramos el avance
        print(str(current_size) + " / " + str(total_size) + " (current size / total size), " + str(percent) + "%")

        # Enviamos el ack
        the_socket.sendto(str(ack_i).encode(), sender)

    curr_seq = 1

    while True:
        data, sender = the_socket.recvfrom(BUF)
        data = data.decode()
        if data == 'FIN':
            break
        last_byte = len(data) - 1
        n_seq = data[last_byte]
        data = data[0:last_byte]
        if int(n_seq) == curr_seq:
            the_socket.sendto(n_seq.encode(), sender)
            # Escribimos los datos en el archivo que abrimos antes
            downloading_file.write(data.encode())

            # Actualizamos los parámetros
            current_size += len(data)
            percent = round(float(current_size) / float(total_size) * 100, 2)

            # Actualizamos cómo va el envío
            print(str(current_size) + " / " + str(total_size) + " (current size / total size), " + str(percent) + "%")

            curr_seq = (curr_seq + 1) % MAX_SEQ_NUM

        else:
            the_socket.sendto(str(curr_seq).encode(), sender)

    if not receiver_leaves_conn(the_socket, sender, BUF, 3):
        print("No se pudo cerrar la conexión")

    downloading_file.close()
    the_socket.close()