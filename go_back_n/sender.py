# -*- coding: utf-8 -*-
import socket
import sys
import os
import time

inivent = 0
buf = 1024

def recACK(rec_addres, sock):
    global inivent, buf
    data,address=sock.recvfrom(buf)
    inivent=data.decode()+1

if __name__ == '__main__':

    # Parámetros para echar a correr el enviador
    if len(sys.argv) != 4:
        print("python sender.py [IPADDRESS] [PORTNUMBER] [FILENAME]")
        sys.exit()

    # Armamos el socket
    the_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Obtenemos el puerto y la IP
    Server_IP = sys.argv[1]
    Server_Port = int(sys.argv[2])

    # Establecemos parámetros
    #buf = 1024
    address = (Server_IP, Server_Port)
    # seq = 0
    # ack = 0
    window_size = 5

    # Establecer conexion
    SYS = "SYS"
    OK = "OK"

    the_socket.sendto(SYS.encode(), address)
    acksys, addressrec = the_socket.recvfrom(buf)
    if (acksys.decode() == "ACKCON" and addressrec == address):
        the_socket.sendto(OK.encode(), address)
    else:
        raise Exception('Error qlo')

    # Obtenemos los parámetros del archivo a enviar
    file_name = sys.argv[3]
    total_size = os.path.getsize(file_name)
    current_size = 0
    percent = round(0, 2)

    # Abrimos el archivo
    sending_file = open(file_name, "rb")
    data = str(file_name) + "|||" + str(total_size) + "|||" + str(inivent)
    the_socket.sendto(data.encode(), address)
    #hay que ponerle para que reciba el ack si es que esto se mantiene


    blocks = []
    nseq = 0
    file = sending_file
    while True:
        block = file.read(buf)
        if not block:
            break
        blocks.append(block.decode() + "|||" + str(nseq))
        nseq += 1

    # inivent=0
    enviar = 0
    timeout = 5
    while (inivent < nseq):
        while (enviar < inivent + window_size):
            the_socket.sendto(blocks[enviar].encode(), address)
            enviar += 1
        beginning = time.time()
        tempini = inivent
        dif = 0
        while (dif < timeout or tempini != inivent):
            dif = time.time() - beginning
        if dif >= timeout:
            enviar = inivent

    '''sending_file = open(file_name, "rb")


    # 'Codificamos' el header
    data = str(file_name) + "|||" + str(total_size) + "|||" + str(seq)

    # while para enviar datos
    while True:
        # Mandamos los datos donde corresponde
        # the_socket.sendto(data, address)
        the_socket.sendto(data.encode(), address)

        # Actualizamos el número de secuencia
        seq = (seq + 1) % 2

        # Seteamos un timeout (bloqueamos el socket después de 0.5s)
        the_socket.settimeout(0.5)

        # Contador de intentos
        try_counter = 0

        # Vemos que llegue el ACK
        while True:
            try:
                # Si en 10 intentos no funciona, salimos
                if try_counter == 10:
                    print("error")
                    break

                # Obtenemos la respuesta (estamos esperando un ACK)
                ack, address = the_socket.recvfrom(buf)
                ack = ack.decode()

                # Si recibimos lo que esperabamos, actualizamos cómo va el envío
                if str(ack) == str(seq):
                    print(
                        str(current_size) + " / " + str(total_size) + "(current size / total size), " + str(
                            percent) + "%")

                    # y pasamos a actualizar los parametros en (**)
                    break

                # Si no, seguimos esperando el ack
                else:
                    print("ack is not equal to seq")

            except:
                # Si ocurre un error avisamos y aumentamos el contador
                try_counter += 1
                print("timed out")
                the_socket.sendto(data.encode(), address)

        # Si en 10 intentos no funciona, salimos
        if try_counter == 10:
            break

        # (**) Actualizamos los parámetros :
        data = sending_file.read(buf - 1)
        current_size += len(data)
        percent = round(float(current_size) / float(total_size) * 100, 2)

        # Si no hay datos mandamos un string vacío y dejamos de enviar cosas
        if not data:
            the_socket.sendto("".encode(), address)
            break

        # Actualizamos los datos a enviar
        data = data.decode()
        data += str(seq)'''

    # Cerramos conexión y archivo
    the_socket.close()
    sending_file.close()
