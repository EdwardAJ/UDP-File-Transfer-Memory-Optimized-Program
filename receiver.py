import os
import socket
import threading
from packet import *
from constants import *
from os import listdir
from os.path import isfile, join

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((RECEIVER_SUBNET, RECEIVER_PORT))

def read_packet_data(packet):
    result = bytearray(DATA_MAX_SIZE)
    for i in range(0, DATA_MAX_SIZE):
        result[i] = packet[7 + i]
    return result

def read_file (filename):
    with open (filename, 'rb') as fin:
        return fin.read()

def get_file_list (id):
    my_path = os.path.abspath(os.path.dirname(__file__))
    complete_path = os.path.join(my_path, str(id))
    onlyfiles = [f for f in listdir(complete_path) if isfile(join(complete_path, f))]
    return onlyfiles


def create_merged_file (id):
    print('Merging folder ' + str(id) + '...')
    my_path = os.path.abspath(os.path.dirname(__file__))
    complete_path = os.path.join(my_path, str(id))
    complete_name = os.path.join(complete_path, 'merged')
    
    file_list_array = get_file_list(id)
    write_file(b'\x00', complete_name)
    file_list_array.sort()
    f = open(complete_name, "wb")
    for file_name in file_list_array:
        buf = read_file(os.path.join(complete_path, file_name))
        f.write(buf)
        f.seek(0,2)

def write_file(data, filename):
    with open(filename, "wb") as binary_file:
        # Write text or bytes to the file
        num_bytes_written = binary_file.write(data)

def write_directory (data, id):
    my_path = os.path.abspath(os.path.dirname(__file__))
    # Check if directory exists
    if (not os.path.exists(str(id))):
        os.mkdir(str(id))
    complete_path = os.path.join(my_path, str(id))
    file_name_int = 1
    complete_name = os.path.join(complete_path, str(file_name_int))
    while os.path.exists(complete_name):
        file_name_int = file_name_int + 1
        complete_name = os.path.join(complete_path, str(file_name_int))
    write_file(data, complete_name)

def receiver():
    print("Receiving on " + str(RECEIVER_SUBNET) + ":" + str(RECEIVER_PORT))
    i = 0
    while True:
        packet, addr = udp_socket.recvfrom(DATA_MAX_SIZE + 7)
        if (is_checksum_valid(packet)):
            packet_payload = read_packet_data(packet)
            write_directory(packet_payload, get_packet_id(packet))
            if (is_fin(packet)):
                send_packet(create_fin_ack(packet), addr[0], SENDER_ACK_PORT)
                threading.Thread(target=create_merged_file, args=(get_packet_id(packet),)).start()
            else:
                send_packet(create_ack(packet), addr[0], SENDER_ACK_PORT)


receiver()