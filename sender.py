import os
import sys
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
# INI KE BAWAH COPAS DARI http://code.activestate.com/recipes/577871-python-progressbar/

class ProgressBar(object):
    """ProgressBar class holds the options of the progress bar.
    The options are:
        start   State from which start the progress. For example, if start is 
                5 and the end is 10, the progress of this state is 50%
        end     State in which the progress has terminated.
        width   --
        fill    String to use for "filled" used to represent the progress
        blank   String to use for "filled" used to represent remaining space.
        format  Format
        incremental
    """
    def __init__(self, start=0, end=10, width=12, fill='=', blank='.', format='[%(fill)s>%(blank)s] %(progress)s%%', incremental=True):
        super(ProgressBar, self).__init__()

        self.start = start
        self.end = end
        self.width = width
        self.fill = fill
        self.blank = blank
        self.format = format
        self.incremental = incremental
        self.step = 100 / float(width) #fix
        self.reset()

    def __add__(self, increment):
        increment = self._get_progress(increment)
        if 100 > self.progress + increment:
            self.progress += increment
        else:
            self.progress = 100
        return self

    def __str__(self):
        progressed = int(self.progress / self.step) #fix
        fill = progressed * self.fill
        blank = (self.width - progressed) * self.blank
        return self.format % {'fill': fill, 'blank': blank, 'progress': int(self.progress)}

    __repr__ = __str__

    def _get_progress(self, increment):
        return float(increment * 100) / self.end

    def reset(self):
        """Resets the current progress to the start point"""
        self.progress = self._get_progress(self.start)
        return self


class AnimatedProgressBar(ProgressBar):
    """Extends ProgressBar to allow you to use it straighforward on a script.
    Accepts an extra keyword argument named `stdout` (by default use sys.stdout)
    and may be any file-object to which send the progress status.
    """
    def __init__(self, *args, **kwargs):
        super(AnimatedProgressBar, self).__init__(*args, **kwargs)
        self.stdout = kwargs.get('stdout', sys.stdout)

    def show_progress(self):
        if hasattr(self.stdout, 'isatty') and self.stdout.isatty():
            self.stdout.write('\r')
        else:
            self.stdout.write('\n')
        self.stdout.write(str(self))
        self.stdout.flush()
