import socket
import threading
from constants import *

packet_types = [
    0, #DATA
    1, #ACK
    2, #FIN
    3, #FIN-ACK
]

def generate_packet(packet_type, id, sequence, length, data):
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
    for i in range(0, DATA_MAX_SIZE - 1 + 1):
        packet[7 + i] = data[i]

    #Checksum
    checksum = generate_checksum(packet)
    print(checksum)
    packet[5] = checksum[0]
    packet[6] = checksum[1]

    return packet

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

def split_file (filename, id):
    packets = []
    with open (filename, 'rb') as fin:
        buf = fin.read(DATA_MAX_SIZE)
        i = 0
        while (buf):
            print(len(buf))
            data = bytearray(DATA_MAX_SIZE)

            for j in range(0, len(buf) - 1 + 1):
                data[j] = buf[j]
            
            packets.append(generate_packet(packet_types[0], id, i, len(buf), data))
            buf = fin.read(DATA_MAX_SIZE)
            i += 1

        print ('COUNT: ', i)
    return packets

# aas = split_file('edward 3x4 hitam putih.jpg', 1)
# for aa in aas:
#     print(aa[0:8])

class MyThread():
    # ini copas dari https://www.tutorialspoint.com/python/python_multithreading.htm
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self,idFile,filename):
        threadLock.acquire()
        split_file(filename,idFile)
        print(file_number+1)
        threadLock.release()

threadLock = threading.Lock()

# bacain nama-nama filenya dulu
list_of_filename = []
while (len(list_of_filename) < 4):
    input_name = input()
    if (input_name == ''):
        break
    list_of_filename.append(input_name)

# main program, jalanin multithreading
file_number = 0
while(file_number < len(list_of_filename)):
    # globals()['thread%s' % file_number] --->>> adalah nama variabel, jadi thread1 thread2 dst
    globals()['thread%s' % (file_number+1)] = MyThread(file_number, "Thread-"+str(file_number+1), file_number)
    globals()['thread%s' % (file_number+1)].run(file_number,list_of_filename[file_number])
    globals()['thread%s' % (file_number+1)].join()
    file_number += 1

# udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# data = bytearray(DATA_MAX_SIZE)
# data[0] = 72
# data[1] = 69
# udp_socket.sendto(generate_packet(packet_types[0], 0, 0, 4, data), (UDP_IP, UDP_PORT))
