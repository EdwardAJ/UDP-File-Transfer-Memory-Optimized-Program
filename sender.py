import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 8080
MESSAGE = "Hello World!"

package_types = [
    0, #DATA
    1, #ACK
    2, #FIN
    3, #FIN-ACK
]

def generate_packet():
    id = 0
    type_id_int = package_types[0] * (2^4) + id
    sequence_number = bytearray(2)
    length = bytearray(2)
    checksum = bytearray(2) 

    data = bytearray(35536)
    data[0] = 72
    data[1] = 69
    data[2] = 72
    data[3] = 69

    packet = bytearray(7 + len(data))
    packet[0] = type_id_int
    packet[1] = sequence_number[0]
    packet[2] = sequence_number[1]
    packet[3] = length[0]
    packet[4] = length[1]
    packet[5] = checksum[0]
    packet[6] = checksum[1]
    
    for i in range(0, len(data)-1):
        packet[7+ i] = data[i]
    
    return packet

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.sendto(generate_packet(), (UDP_IP, UDP_PORT))