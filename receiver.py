import socket
import os
from os import listdir
from os.path import isfile, join
from packet import *
from constants import *

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, DATA_MAX_SIZE)
udp_socket.bind((UDP_IP, UDP_PORT))

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
    print(onlyfiles)
    return onlyfiles


def create_merged_file (id):
    my_path = os.path.abspath(os.path.dirname(__file__))
    complete_path = os.path.join(my_path, str(id))
    print('complete_path: ', complete_path)
    complete_name = os.path.join(complete_path, 'merged')
    print(complete_name)
    file_list_array = get_file_list(id)
    write_file(b'\x00', complete_name)
    file_list_array.sort()
    print(file_list_array)
    f = open(complete_name, "wb")
    for file_name in file_list_array:
        buf = read_file(os.path.join(complete_path, file_name))
        f.write(buf)
        f.seek(0,2)

def write_file(data, filename, length):
    with open(filename, "wb") as binary_file:
        # Write text or bytes to the file
        data_to_write = bytearray(length)
        for i in range(0, length):
                data_to_write[i] = data[i]
        num_bytes_written = binary_file.write(data_to_write)

def write_directory (data, id, length):
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
    write_file(data, complete_name, length)

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


while True:
    data, addr = udp_socket.recvfrom(DATA_MAX_SIZE + 7)
    # Get packet id
    packet_read = read_packet_data(data)
    write_directory(packet_read, get_packet_id(data), get_length(data))
# create_merged_file(0)
# receiver()
# get_file_list(2)


