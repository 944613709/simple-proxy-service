import socket,json

BUFF_LEN     = 400                   # 最大报文长度
SERVER_ADDR  = ("127.0.0.1", 18000)  # 指明服务端地址

# 创建 UDP Socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 设置socket超时时间，单位：秒
client_socket.settimeout(2)

# 要发送的信息 对象
message = {
    'action' : '获取信息',
    'name' : '白月黑羽'
}
# 发送出去的信息必须是字节，所以要先序列化，再编码
sendbytes = json.dumps(message).encode('utf8')
client_socket.sendto(sendbytes, SERVER_ADDR)
try:
    recvbytes, server = client_socket.recvfrom(BUFF_LEN)
    # 接收到的信息是字节，所以要解码，再反序列化
    message = json.loads(recvbytes.decode('utf8'))
    print(message)
except socket.timeout:
    print('接收消息超时')