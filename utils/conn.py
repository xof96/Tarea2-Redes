SYS = 'SYS'
SYS_ACK = 'SA'
OK = 'OK'


def sender_handshake_conn(socket, address, buf, n):
    socket.sendto(SYS.encode(), address)
    sys_ack_res, rec_address = socket.recvfrom(buf)
    if sys_ack_res.decode() == SYS_ACK and rec_address == address:
        if n == 3:
            socket.sendto(OK.encode(), address)
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
            ok, s_ok_address = socket.recvfrom()
            if ok.decode() == OK and s_ok_address == sender_address:
                return True
            else:
                return False
        elif n == 2:
            return True
        else:
            return False

    else:
        return False
