import socket
from packet import *
import sys
import time
import threading
from constants import *

jumlahPart = 0

def split_file (filename, id):
    global jumlahPart
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
        jumlahPart = i
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
        packets = split_file(filename,idFile)
        for packet in packets:
            print('Sending...')
            send_packet(packet, UDP_IP, UDP_PORT)
        # test print nomor thread
        print(file_number+1)
        threadLock.release()

threadLock = threading.Lock()


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


if __name__ == '__main__':
   
    file_number = 0
    while True:
        p = AnimatedProgressBar(end=100, width=80)
        input_name = input()
        if (input_name != ''):
            while True:
                globals()['thread%s' % (file_number+1)] = MyThread(file_number, "Thread-"+str(file_number+1), file_number)
                globals()['thread%s' % (file_number+1)].run(file_number,input_name)
                file_number += 1
                p + 100/jumlahPart
                p.show_progress()
                time.sleep(0.1)
                if p.progress == 100:
                    break
            print()
            