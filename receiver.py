import socket
import os
from constants import *

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, DATA_MAX_SIZE)
udp_socket.bind((UDP_IP, UDP_PORT))

def read_packet_data(packet):
    result = bytearray(DATA_MAX_SIZE)
    for i in range(0, DATA_MAX_SIZE):
        result[i] = packet[7 + i]
    return resultx


def write_file(data, filename):
    with open(filename, "wb") as binary_file:
        # Write text or bytes to the file
        binary_file.write("Write text by encoding\n".encode('utf8'))
        num_bytes_written = binary_file.write(data)
        print("Wrote %d bytes." % num_bytes_written)

def write_directory (data, id):
    my_path = os.path.abspath(os.path.dirname(__file__))
    # Check if directory exists
    if (not os.path.exists(str(id))):
        os.mkdir(str(id))
    complete_path = my_path + '/'+ str(id)
    file_name_int = 1
    complete_name = os.path.join(complete_path, str(file_name_int) + '.txt')
    while os.path.exists(complete_name):
        file_name_int = file_name_int + 1
        complete_name = os.path.join(complete_path, str(file_name_int) + '.txt')
    write_file(data, complete_name)

while True:
    data, addr = udp_socket.recvfrom(DATA_MAX_SIZE + 7)
    # Get packet id
    packet_read = read_packet_data(data)
    write_directory(packet_read, 2)
    # print ("Received: ", read_packet_data(data))
# write_directory(1)