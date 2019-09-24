import os
import socket
import threading
from packet import *
from constants import *
from os import listdir
from os.path import isfile, join

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((RECEIVER_SUBNET, RECEIVER_PORT))

memory_dict = {
    0: [],
    1: [],
    2: [],
    3: [],
    4: [],
    5: [],
    6: [],
    7: [],
    8: [],
    9: [],
    10: [],
    11: [],
    12: [],
    13: [],
    14: [],
    15: [],
}

def read_packet_data(packet):
    result = bytearray(DATA_MAX_SIZE)
    for i in range(0, DATA_MAX_SIZE):
        result[i] = packet[7 + i]
    return result

def dump_packet_to_file(packet):
    complete_name = os.path.join(os.path.abspath(os.path.dirname(__file__)), str(get_packet_id(packet)))
    with open(complete_name, "ab") as file:
        data_to_write = bytearray(get_length(packet))
        for i in range(0, get_length(packet)):
            data_to_write[i] = packet[i + 7]
        file.write(data_to_write)

def insert_to_memory(packet):
    memory_dict[get_packet_id(packet)].append(packet)

def dump_memory_to_file():
    print('Dumping')
    for key in memory_dict:
        for packet in memory_dict[key]:
            dump_packet_to_file(packet)

def free_memory():
    for key in memory_dict:
        memory_dict[key].clear()

def receiver():
    print("Receiving on " + str(RECEIVER_SUBNET) + ":" + str(RECEIVER_PORT))
    i = 0
    current_memory = 0
    while True:
        packet, addr = udp_socket.recvfrom(DATA_MAX_SIZE + 7)
        if (is_checksum_valid(packet)):
            packet_payload = read_packet_data(packet)
            if (is_fin(packet)):
                send_packet(create_fin_ack(packet), addr[0], SENDER_ACK_PORT)
                dump_memory_to_file()
                free_memory()
                current_memory = 0
            else:
                send_packet(create_ack(packet), addr[0], SENDER_ACK_PORT)
                if (current_memory < MAX_MEMORY_SIZE - (DATA_MAX_SIZE + 7)):
                    insert_to_memory(packet)
                else:
                    dump_memory_to_file()
                    free_memory()
                    current_memory = 0


receiver()