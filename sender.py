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
    print('type: ', packet[0])

    #Sequence
    packet[1] = (sequence >> 8) & 255
    packet[2] = sequence & 255

    #Length
    packet[3] = (length >> 8) & 255
    packet[4] = length & 255
    
    #Data
    for i in range(0, DATA_MAX_SIZE - 1 + 1):
        packet[7 + i] = data[i]

    #Checksum
    checksum = generate_checksum(packet)
    # print(checksum)
    packet[5] = checksum[0]
    packet[6] = checksum[1]

    return packet

def generate_checksum(packet):
    pepega = bytearray(DATA_MAX_SIZE + 5 + ((DATA_MAX_SIZE + 5) % 2))
    for i in range(0, 4 + 1):
        pepega[i] = packet[i]
    for i in range(0, DATA_MAX_SIZE):
        pepega[5 + i] = packet[7 + i]

    checksum = bytearray(2)
    for i in range(0, int(len(pepega)/2)):
        checksum[0] = checksum[0] ^ pepega[i * 2]
        checksum[1] = checksum[1] ^ pepega[i * 2 + 1]
    
    return checksum

def split_file (filename, id):
    packets = []
    i = 0
    with open (filename, 'rb') as fin:
        buf = fin.read(DATA_MAX_SIZE)
        while (buf):
            # print(len(buf))
            data = bytearray(DATA_MAX_SIZE)

            for j in range(0, len(buf) - 1 + 1):
                data[j] = buf[j]
            
            packets.append(generate_packet(packet_types[1], id, i, len(buf), data))
            buf = fin.read(DATA_MAX_SIZE)
            i += 1

        # print ('COUNT: ', i)
    return packets

aas = split_file('edward 3x4 hitam putih.jpg', 3)
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.sendto(aas[0], (UDP_IP, UDP_PORT))
# for aa inprint(packet_read[0]) aas:
#     udp_socket.sendto(aa[0:8], (UDP_IP, UDP_PORT))
#     print(aa[0:8])
