import os
import sys
import time
import socket
import platform
import threading
from math import floor, ceil
from packet import *
from constants import *

SENDING_THREADS = {}
THREAD_IS_SENDING = []
sender_memory_dict = {}

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

bar_drawer = ProgressBarHandler(25)

def is_still_sending():
    for thread_status in THREAD_IS_SENDING:
        if (thread_status):
            return True
    return False

def read_file (id, filename):
    with open (filename, 'rb') as file:
        # Counter to keep track how much memory has been added.
        current_memory_size = 0
        # While file is not closed yet:
        while (current_memory_size < os.stat(filename).st_size):
            memory_size_per_pass = min(MAX_MEMORY_SIZE, os.stat(filename).st_size - current_memory_size)
            file.seek(current_memory_size, 0)
            file_buffer = file.read(memory_size_per_pass)
            send_file_buffer_to_receiver(id, filename, file_buffer)
            current_memory_size += memory_size_per_pass

def send_file_buffer_to_receiver (id, filename, file_buffer):
    file_buffer_size = len(file_buffer)
    current_size = 0
    packet_idx = 0
    curr_idx = 0
    while (current_size < file_buffer_size):
        packet_data_size = min(file_buffer_size - current_size, DATA_MAX_SIZE)
        packet = bytearray(packet_data_size)
        i = 0
        while (i < packet_data_size):
            packet[i] = file_buffer[curr_idx + i]
            i += 1
        curr_idx += i
        # Insert to sender memory!  
        insert_to_sender_memory(id, packet)
        packet_idx += 1
        current_size += packet_data_size

def insert_to_sender_memory(id, packet):
    try:
        sender_memory_dict[id].append(packet)
    except KeyError:
        sender_memory_dict[id] = [packet]

def send_file_bytes_of_idx(id, filename, idx, file_buffer):
    send_packet(generate_packet(packet_types[1], id, idx + 1, len(file_buffer), file_buffer), DESTINATION_IP_ADDRESS, RECEIVER_PORT)

def get_packet_amount(filename):
    return ceil(os.stat(filename).st_size/DATA_MAX_SIZE)

class FileSenderThread(threading.Thread):
    id = None
    filename = None
    is_ready_to_send = True
    packet_count = 0
    timeout_event = None
    
    def __init__(self, id, filename):
        threading.Thread.__init__(self)
        self.id = id
        self.filename = filename
        self.packet_count = get_packet_amount(self.filename)

    def run(self):
        introduce_packet = create_introduce_packet(self.packet_count, clear_filename(self.filename), self.id)
        send_packet(introduce_packet, DESTINATION_IP_ADDRESS, RECEIVER_PORT)
        self.is_ready_to_send = False
        self.timeout_event = threading.Event()
        self.timeout_event.wait(SENDER_ACK_TIME_LIMIT)

        while not self.is_ready_to_send:
            send_packet(introduce_packet, DESTINATION_IP_ADDRESS, RECEIVER_PORT)
            self.timeout_event = threading.Event()
            self.timeout_event.wait(SENDER_ACK_TIME_LIMIT)
        
        i = 0
        
        read_file(self.id, self.filename)
        self.packet_count = len(sender_memory_dict[self.id])
        while i < self.packet_count:
            send_file_bytes_of_idx(self.id, self.filename, i, sender_memory_dict[self.id][i])
            self.is_ready_to_send = False
            self.timeout_event = threading.Event()
            self.timeout_event.wait(SENDER_ACK_TIME_LIMIT)
            bar_drawer.set_progress(self.id, i / self.packet_count)
            
            if self.is_ready_to_send:
                i += 1
        
        bar_drawer.set_progress(self.id, 1)
        send_packet(generate_packet(packet_types[2], self.id, 0, 0), DESTINATION_IP_ADDRESS, RECEIVER_PORT)
        
        self.destruction()

    def destruction(self):
        sender_memory_dict[self.id].clear()
        del SENDING_THREADS['SenderThread %s' % self.id]


class AckReceiverThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print('Starting AckReceiver...')

    def run(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((SENDER_ACK_SUBNET, SENDER_ACK_PORT))
        while True:
            packet, _ = udp_socket.recvfrom(DATA_MAX_SIZE + 7)
            self.handle_ack_packet(packet)
            if not is_still_sending():
                print('Exiting...')
                break

    def handle_ack_packet(self, packet):
        if (get_packet_type(packet) == packet_types[1]):
            SENDING_THREADS['SenderThread %s' % get_packet_id(packet)].is_ready_to_send = True
            if (SENDING_THREADS['SenderThread %s' % get_packet_id(packet)].timeout_event != None):
                SENDING_THREADS['SenderThread %s' % get_packet_id(packet)].timeout_event.set()
        else:
            print('FINACK')
            THREAD_IS_SENDING[get_packet_id(packet)] = False


def is_destination_address_valid(destination_address):
    destination_address = destination_address.split(':')

    if len(destination_address) != 2:
        return False
    
    try:
        destination_address[1] = int(destination_address[1])
    except:
        return False
    
    if not (destination_address[1] >= 0 and destination_address[1] <= 65535):
        return False

    if destination_address[0] == 'localhost':
        return True

    try:
        socket.inet_aton(destination_address[0])
    except:
        return False
    
    return True

def clear_filename(filename):
    return filename.split(os.path.sep)[-1]

def main():
    if len(sys.argv[1:]) == 0:
        print('Please input file names when running!')
        return

    for filename in sys.argv[1:]:
        if not os.path.exists(filename):
            print('File ' + filename + ' not found!')
            return

    destination_address = input('Destination address: ')
    if not is_destination_address_valid(destination_address):
        print('Please input valid destination address! Example: 192.168.0.1:8080')
        return
    
    destination_address = destination_address.split(':')
    DESTINATION_IP_ADDRESS = destination_address[0]
    RECEIVER_PORT = destination_address[1]

    receiver_thread = AckReceiverThread()
    receiver_thread.start()

    i = 0
    for filename in sys.argv[1:]:
        THREAD_IS_SENDING.append(True)
        SENDING_THREADS['SenderThread %s' % i] = FileSenderThread(i, filename)
        SENDING_THREADS['SenderThread %s' % i].start()
        bar_drawer.add_progress(clear_filename(filename))
        i += 1

    while (is_still_sending()):
        bar_drawer.drawBars()


main()