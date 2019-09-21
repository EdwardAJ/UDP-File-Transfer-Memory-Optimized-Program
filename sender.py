import socket
from constants import *

packet_types = [
    0, #DATA
    1, #ACK
    2, #FIN
    3, #FIN-ACK
]

def generate_packet(packet_type, id, sequence, length, data):
    type_id = (packet_type << 4) + id

    packet = bytearray(7 + DATA_MAX_SIZE)

    #Type and ID
    packet[0] = type_id

    #Sequence
    packet[1] = (sequence >> 4) & 15
    packet[2] = sequence & 15

    #Length
    packet[3] = (length >> 4) & 15
    packet[4] = length & 15
    
    #Data
    for i in range(0, DATA_MAX_SIZE - 1 + 1):
        packet[7 + i] = data[i]

    #Checksum
    checksum = generate_checksum(packet)
    print(checksum)
    packet[5] = checksum[0]
    packet[6] = checksum[1]

    return packet

def generate_checksum(packet):
    pepega = bytearray(DATA_MAX_SIZE + 5 + ((DATA_MAX_SIZE + 5) % 2))
    for i in range(0, 4 + 1):
        pepega[i] = packet[i]
    for i in range(0, DATA_MAX_SIZE - 1 + 1):
        pepega[5 + i] = packet[7 + i]

    checksum = bytearray(2)
    for i in range(0, int(len(pepega)/2) - 1 + 1):
        checksum[0] = checksum[0] ^ pepega[i * 2]
        checksum[1] = checksum[1] ^ pepega[i * 2 + 1]
    
    return checksum

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

data = bytearray(DATA_MAX_SIZE)
data[0] = 72
data[1] = 69

udp_socket.sendto(generate_packet(packet_types[0], 0, 0, 4, data), (UDP_IP, UDP_PORT))
