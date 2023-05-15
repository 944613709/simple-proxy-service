#  === TCP 客户端程序 client.py ===

from socket import *

IP = '127.0.0.1'
SERVER_PORT = 50000
client_port = 50001
BUFLEN = 1024

# 实例化一个socket对象，指明协议
dataSocket = socket(AF_INET, SOCK_DGRAM)
# bind指定了这个socket的IP和port
# 如果不用bind，就是取对应的IP和随机port
dataSocket.bind((IP,client_port))
print('连接上')
while True:
    # 从终端读入用户输入的字符串
    #toSend = input('>>> ')
    toSend = "123"
    toSend2 = "456"
    if  toSend =='exit':
        break
    # 发送消息，也要编码为 bytes
    dataSocket.sendto(toSend.encode(),(IP,SERVER_PORT))
    dataSocket.sendto(toSend2.encode(),(IP,SERVER_PORT))

    # 等待接收服务端的消息
    recved = dataSocket.recv(BUFLEN)
    # 如果返回空bytes，表示对方关闭了连接
    if not recved:
        break
    # 打印读取的信息
    print(recved.decode())

dataSocket.close()