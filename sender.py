import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 8080
MESSAGE = "Hello World!"

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.sendto(bytes(MESSAGE, "utf-8"), (UDP_IP, UDP_PORT))