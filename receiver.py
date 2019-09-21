import socket
from constants import *

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, DATA_MAX_SIZE)
udp_socket.bind((UDP_IP, UDP_PORT))

def read_packet(packet):
    result = bytearray(DATA_MAX_SIZE)
    for i in range(0, DATA_MAX_SIZE-1):
        result[i] = packet[7 + i]
    return result

def write_file(data):
    with open("hasil.txt", "wb") as binary_file:
        # Write text or bytes to the file
        binary_file.write("Write text by encoding\n".encode('utf8'))
        num_bytes_written = binary_file.write(data)
        print("Wrote %d bytes." % num_bytes_written)

while True:
    data, addr = udp_socket.recvfrom(DATA_MAX_SIZE + 7)
    write_file(read_packet(data))
    print ("Received: ", read_packet(data))