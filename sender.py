import socket
from packet import *
from constants import *

def split_file (filename, id):
    packets = []
    i = 0
    with open (filename, 'rb') as fin:
        i = 0
        buf = fin.read(DATA_MAX_SIZE)
        while (buf):
            print('Bytes: ', len(buf))
            data = bytearray(DATA_MAX_SIZE)

            for j in range(0, len(buf) - 1 + 1):
                data[j] = buf[j]
            
            packets.append(generate_packet(packet_types[1], id, i, len(buf), data))
            buf = fin.read(DATA_MAX_SIZE)
            i += 1

        print ('Count: ', i)
    return packets

aas = split_file('edward 3x4 hitam putih.jpg', 1)
for aa in aas:
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.sendto(aa, (UDP_IP, UDP_PORT))

# data = bytearray(DATA_MAX_SIZE)
# data[0] = 72
# data[1] = 69 
