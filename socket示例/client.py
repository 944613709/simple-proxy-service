#  === TCP 客户端程序 client.py ===

from socket import *

IP = '127.0.0.1'
SERVER_PORT = 50000
client_port = 50001
BUFLEN = 1024

# 实例化一个socket对象，指明协议
dataSocket = socket(AF_INET, SOCK_STREAM)
# bind指定了这个socket的IP和port
# 如果不用bind，就是取对应的IP和随机port
dataSocket.bind((IP,client_port))
# 连接服务端socket
dataSocket.connect((IP, SERVER_PORT))
print('连接上')
while True:
    # 从终端读入用户输入的字符串
    toSend = input('>>> ')
    if  toSend =='exit':
        break
    # 发送消息，也要编码为 bytes
    dataSocket.send(toSend.encode())

    # 等待接收服务端的消息
    recved = dataSocket.recv(BUFLEN)
    # 如果返回空bytes，表示对方关闭了连接
    if not recved:
        break
    # 打印读取的信息
    print(recved.decode())

dataSocket.close()