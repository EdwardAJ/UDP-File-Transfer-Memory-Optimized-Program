import socket
from packet import *
import threading
from constants import *

def split_file (filename, id):
    packets = []
    i = 0
    with open (filename, 'rb') as fin:
        i = 0
        buf = fin.read(DATA_MAX_SIZE)
        i = 0
        while (buf):
            print('Bytes: ', len(buf))
            data = bytearray(DATA_MAX_SIZE)

            for j in range(0, len(buf) - 1 + 1):
                data[j] = buf[j]
            
            packets.append(generate_packet(packet_types[1], id, i, len(buf), data))
            buf = fin.read(DATA_MAX_SIZE)
            i += 1

        print ('Count: ', i)
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
    file_number += 1

# data = bytearray(DATA_MAX_SIZE)
# data[0] = 72
# data[1] = 69 
