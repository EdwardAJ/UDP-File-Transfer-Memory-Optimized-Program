import os
import time
import socket
import threading
from math import floor
from packet import *
from constants import *

SENDING_THREADS = {}

def send_file_bytes_of_idx(id, filename, idx):
    with open (filename, 'rb') as file:
        file.seek(DATA_MAX_SIZE * idx, 0)
        file_buffer = file.read(min(DATA_MAX_SIZE, (os.stat(filename).st_size - (DATA_MAX_SIZE * idx))))
        send_packet(generate_packet(packet_types[1], id, idx, len(file_buffer), file_buffer), DESTINATION_IP_ADDRESS, RECEIVER_PORT)

class FileSenderThread(threading.Thread):
    id = None
    filename = None
    is_ready_to_send = True

    def __init__(self, id, filename):
        threading.Thread.__init__(self)
        self.id = id
        self.filename = filename

    def run(self):
        i = 0
        while i <= floor(os.stat(self.filename).st_size / DATA_MAX_SIZE):
            send_file_bytes_of_idx(self.id, self.filename, i)
            self.is_ready_to_send = False
            time.sleep(SENDER_ACK_TIME_LIMIT)
            if self.is_ready_to_send:
                i += 1
        send_packet(generate_packet(packet_types[2], self.id, 0, 0), DESTINATION_IP_ADDRESS, RECEIVER_PORT)
        self.destruction()

    def destruction(self):
        del SENDING_THREADS['SenderThread %s' % self.id]



class AckReceiverThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        print('Starting AckReceiver...')

    def run(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind((SENDER_ACK_SUBNET, SENDER_ACK_PORT))
        while True:
            packet, addr = udp_socket.recvfrom(DATA_MAX_SIZE + 7)
            self.handle_ack_packet(packet)

    def handle_ack_packet(self, packet):
        if (get_packet_type(packet) == packet_types[1]):
            SENDING_THREADS['SenderThread %s' % get_packet_id(packet)].is_ready_to_send = True

def main():
    receiver_thread = AckReceiverThread()
    receiver_thread.start()

    while True:
        filename = input('Filename: ')
        if (filename != 'quit'):
            i = 0
            while i < 16:
                if 'SenderThread %s' % i in SENDING_THREADS:
                    i += 1
                else:
                    break
            
            print('Sending file ' + filename + '...')
            SENDING_THREADS['SenderThread %s' % i] = FileSenderThread(i, filename)
            SENDING_THREADS['SenderThread %s' % i].start()
        else:
            break

main()