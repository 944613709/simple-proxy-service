#  === TCP 服务端程序 server.py ， 支持多客户端 ===

# 导入socket 库
from socket import *
from threading import Thread

IP = '127.0.0.1'
PORT = 50000
BUFLEN = 512

# 实例化一个socket对象 用来监听客户端连接请求
ServerSocket = socket(AF_INET, SOCK_DGRAM)

# socket绑定地址和端口
ServerSocket.bind((IP, PORT))



while True:
   # 在循环中，一直接受新的连接请求
   receive_data, client_address = ServerSocket.recvfrom(BUFLEN)
   receive_data = receive_data.decode("utf-8")
   client_address = str(client_address)
   print('收到来自{client_address}的信息')
   print('信息：'+str(receive_data))

