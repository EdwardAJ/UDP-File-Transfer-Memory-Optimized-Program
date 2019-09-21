import socket
from constants import *

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((UDP_IP, UDP_PORT))

def read_packet(packet):
    result = bytearray(DATA_MAX_SIZE)
    for i in range(0, DATA_MAX_SIZE-1):
        result[i] = packet[7 + i]
    return result

while True:
    data, addr = udp_socket.recvfrom(DATA_MAX_SIZE + 7)
    print ("Received: ", read_packet(data))