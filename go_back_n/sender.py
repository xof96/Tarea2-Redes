import socket, threading

rdy = 0


def send_data(data, address, buf, timeout, seq):
    global rdy

    the_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    the_socket.sendto(data.encode(), address)

    the_socket.settimeout(timeout)

    ack, address_rec = the_socket.recvfrom(buf)

    if ack.decode() == seq:
        rdy += 1
