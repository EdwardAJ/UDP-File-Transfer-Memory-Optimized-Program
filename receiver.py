import os
import socket
import platform
import threading
from packet import *
from constants import *
from math import floor, ceil
from os import listdir
from os.path import isfile, join

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((RECEIVER_SUBNET, RECEIVER_PORT))

current_memory = 0
bar_handler = None

memory_dict = {}
filename_dict = {}

class ProgressBarHandler():
    bar_length = None

    progress_name = []
    progresses = []

    def __init__(self, bar_length = 10):
        self.bar_length = bar_length

    def add_progress(self, progress_name):
        self.progress_name.append(progress_name)
        self.progresses.append(0.0)

    def drawBars(self):
        if (platform.system() == 'Linux' or platform.system() == 'Darwin'):
            os.system('clear')
        elif (platform.system() == 'Windows'):
            os.system('cls')

        for i in range(0, len(self.progress_name)):
            self.drawBar(i)

    def drawBar(self, id):
        string_to_print = self.progress_name[id]
        string_to_print += ': ['

        i = 0
        while i < floor(self.progresses[id] * self.bar_length):
            string_to_print += '='
            i += 1

        while i < self.bar_length:
            string_to_print += '-'
            i += 1

        string_to_print += ']'

        print(string_to_print)

    def set_progress(self, id, progress):
        self.progresses[id] = progress

def read_packet_data(packet):
    result = bytearray(DATA_MAX_SIZE)
    for i in range(0, DATA_MAX_SIZE):
        result[i] = packet[7 + i]
    return result

def dump_packet_to_file(packet, filename):
    complete_name = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'downloads', str(filename))
    with open(complete_name, "ab") as file:
        data_to_write = bytearray(get_length(packet))
        for i in range(0, get_length(packet)):
            data_to_write[i] = packet[i + 7]
        file.write(data_to_write)

def get_filename(key):
    return filename_dict[key][1]

def get_dictkey(packet, source_addr):
    return str(source_addr) + str(get_packet_id(packet))

def insert_to_memory(packet, source_addr):
    global current_memory
    try:
        memory_dict[get_dictkey(packet, source_addr)].append(packet)
    except KeyError:
        memory_dict[get_dictkey(packet, source_addr)] = [packet]
    current_memory += get_length(packet)

def dump_memory_to_file():
    for key in memory_dict:
        for packet in memory_dict[key]:
            dump_packet_to_file(packet, get_filename(key))

def free_memory():
    for key in memory_dict:
        memory_dict[key].clear()

def receiver():
    global bar_handler
    global current_memory
    RECEIVER_PORT = input('Port to bind: ')

    if not os.path.exists(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'downloads')):
        os.mkdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'downloads'))
    
    print("Receiving on " + str(RECEIVER_SUBNET) + ":" + str(RECEIVER_PORT))
    i = 0

    bar_handler = ProgressBarHandler(20)
    while True:
        packet, addr = udp_socket.recvfrom(DATA_MAX_SIZE + 7)
        if (is_checksum_valid(packet)):
            packet_payload = read_packet_data(packet)
            if (is_fin(packet)):
                send_packet(create_fin_ack(packet), addr[0], SENDER_ACK_PORT)
                filename_dict[get_dictkey(packet, addr[0])][2] = filename_dict[get_dictkey(packet, addr[0])][1]
                dump_memory_to_file()
                free_memory()
                current_memory = 0
            elif (get_sequence_id(packet) == 0):
                send_packet(create_ack(packet), addr[0], SENDER_ACK_PORT)

                payload = get_payload(packet)
                packet_count = (payload[0] << 8) + payload[1]

                i = 0
                received_filename = ''
                for i in range(0, get_length(packet) - 2):
                    received_filename += chr(payload[2 + i])

                filename = received_filename
                name_i = 0
                while os.path.exists(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'downloads', filename)) or filename in filename_dict.values():
                    name_i += 1
                    filename = received_filename + '(' + str(name_i) + ')'
                
                filename_dict[get_dictkey(packet, addr[0])] = [packet_count, filename, 0]
                bar_handler.add_progress(filename)
            else:
                send_packet(create_ack(packet), addr[0], SENDER_ACK_PORT)
                filename_dict[get_dictkey(packet, addr[0])][2] += 1
                bar_handler.set_progress(bar_handler.progress_name.index(get_filename(get_dictkey(packet, addr[0]))), filename_dict[get_dictkey(packet, addr[0])][2] / filename_dict[get_dictkey(packet, addr[0])][0])
                insert_to_memory(packet, addr[0])
                if current_memory >= MAX_MEMORY_SIZE - (DATA_MAX_SIZE + 7):
                    dump_memory_to_file()
                    free_memory()
                    current_memory = 0
            bar_handler.drawBars()

receiver()