import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 8080

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65550)
udp_socket.bind((UDP_IP, UDP_PORT))

def read_packet(packet):
    result = bytearray(35536)
    i = 0
    while (packet[7+i] != 0x00):
        result[i] = packet[7+i]
        i = i+1
    # for i in range(0, 35535):
    #     result[i] = packet[7 + i]
    return result

while True:
    data, addr = udp_socket.recvfrom(1024)
    print ("Received: ", read_packet(data))