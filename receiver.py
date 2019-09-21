import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 8080

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((UDP_IP, UDP_PORT))

def read_packet(packet):
    result = bytearray(5)
    for i in range(0, 5):
        result[i] = packet[7 + i]
    return result

while True:
    data, addr = udp_socket.recvfrom(1024)
    print ("Received: ", read_packet(data))