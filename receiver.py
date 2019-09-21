import socket
from packet import *
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

def receiver():
    i = 0
    while True:
        packet, addr = udp_socket.recvfrom(DATA_MAX_SIZE + 7)
        if (is_checksum_valid(packet)):
            i += 1
            if (is_fin(packet)):
                create_fin_ack(packet)
                #send_packet(create_fin_ack(packet))
            else:
                create_ack(packet)
                #send_packet(create_ack(packet))
        print ("Received: ", i)

receiver()