import time

SYS = 'SYS'
SYS_ACK = 'SA'
ACK = 'ACK'

FIN = 'FIN'


def sender_handshake_conn(socket, address, buf, n):
    socket.sendto(SYS.encode(), address)
    sys_ack_res, rec_address = socket.recvfrom(buf)
    if sys_ack_res.decode() == SYS_ACK and rec_address == address:
        if n == 3:
            socket.sendto(ACK.encode(), address)
            return True
        elif n == 2:
            return True
        else:
            return False
    else:
        return False


def receiver_handshake_conn(socket, buf, n):
    conn_req, sender_address = socket.recvfrom(buf)
    if conn_req.decode() == SYS:
        socket.sendto(SYS_ACK.encode(), sender_address)
        if n == 3:
            ack, s_ok_address = socket.recvfrom(buf)
            if ack.decode() == ACK and s_ok_address == sender_address:
                return True
            else:
                return False
        elif n == 2:
            return True
        else:
            return False
    else:
        return False


def sender_leaves_conn(socket, address, buf, n):
    socket.sendto(FIN.encode(), address)
    ack_res, rec_address = socket.recvfrom(buf)
    if ack_res.decode() == ACK and rec_address == address:
        fin_res, fin_res_address = socket.recvfrom(buf)
        if fin_res.decode() == FIN and fin_res_address == address:
            if n == 3:
                socket.sendto(ACK.encode(), address)
                time.sleep(2)
                return True
            elif n == 2:
                return True
            else:
                return False
        else:
            return False
    else:
        return False


def receiver_leaves_conn(socket, sender_address, buf, n):
    socket.sendto(ACK.encode(), sender_address)
    time.sleep(2)
    socket.sendto(FIN.encode(), sender_address)
    if n == 3:
        ack, s_ok_address = socket.recvfrom(buf)
        if ack.decode() == ACK and s_ok_address == sender_address:
            return True
        else:
            return False
    elif n == 2:
        return True
    else:
        return False
