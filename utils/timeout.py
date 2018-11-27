import time


def timeout_calc(sock, address):
    Estimated_RTT = 1
    Dev_RTT = 0
    TEST = "TEST"
    TESTEND = "TESTEND"
    for i in range(30):
        init = time.time()
        print(init)
        sock.sendto(TEST.encode(), address)
        data,recadd=sock.recvfrom(1024)
        if(data.decode()!="TESTACK" or address!= recadd):
            return 0
        end = time.time()
        print(end)
        Sample_RTT = end - init
        Dev_RTT = 3 * Dev_RTT / 4 + abs(Sample_RTT - Estimated_RTT) / 4
        Estimated_RTT = 7 * Estimated_RTT / 8 + Sample_RTT / 8
        print("D: ",Dev_RTT)
        print("E: ",Estimated_RTT)
    sock.sendto(TESTEND.encode(), address)
    return Estimated_RTT + 4 * Dev_RTT


def timeout_rec(sock):
    data, address = sock.recvfrom(1024)
    while data.decode() != "TESTEND":
        sock.sendto("TESTACK".encode(), address)
        data, address = sock.recvfrom(1024)