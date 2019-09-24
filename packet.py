import socket
from constants import *

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

def generate_packet(packet_type, id, sequence, length, data = None):
    data = bytearray(DATA_MAX_SIZE) if data == None else data

    type_id = (packet_type << 4) + id

    packet = bytearray(7 + DATA_MAX_SIZE)

    #Type and ID
    packet[0] = type_id

    #Sequence
    packet[1] = (sequence >> 8) & 255
    packet[2] = sequence & 255

    #Length
    packet[3] = (length >> 8) & 255
    packet[4] = length & 255
    
    #Data
    for i in range(0, len(data)):
        packet[7 + i] = data[i]

    #Checksum
    checksum = generate_checksum(packet)
    packet[5] = checksum[0]
    packet[6] = checksum[1]

    return packet

def is_checksum_valid(packet):
    return generate_checksum(packet) == get_checksum(packet)

def is_fin(packet):
    return get_packet_type(packet) == packet_types[2]

def get_packet_type(packet):
    return packet_types[(int(packet[0]) >> 4) & 15]

def get_packet_id(packet):
    return int(packet[0]) & 15

def get_sequence_id(packet):
    return (int(packet[1]) << 8) + int(packet[2])

def get_checksum(packet):
    return bytearray([packet[5], packet[6]])

def get_length(packet):
    return (int(packet[3]) << 8) + int(packet[4])

def get_payload(packet):
    payload = bytearray(get_length(packet))
    for i in range(0, get_length(packet)):
        payload[i] = packet[7 + i]
    return payload


def create_ack(packet):
    packet_id = get_packet_id(packet)
    sequence_id = get_sequence_id(packet)
    ack_packet = generate_packet(packet_types[1], packet_id, sequence_id, 0)
    return ack_packet

def create_fin_ack(packet):
    packet_id = get_packet_id(packet)
    sequence_id = get_sequence_id(packet)
    ack_packet = generate_packet(packet_types[3], packet_id, sequence_id, 0)
    return ack_packet

def send_packet(packet, ip_address, port):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return udp_socket.sendto(packet, (ip_address, port))

def print_packet_info(packet):
    print('Type: ', get_packet_type(packet))
    print('ID: ', get_packet_id(packet))
    print('Sequence: ', get_sequence_id(packet))
    print('Length: ', get_length(packet))
    print('Checksum: ', get_checksum(packet))