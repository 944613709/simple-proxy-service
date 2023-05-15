import socket, json

BUFF_LEN = 400  # 最大报文长度
ADDR = ("", 18000)  # 指明服务端地址，IP地址为空表示本机所有IP

# 创建 UDP Socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# 绑定地址
server_socket.bind(ADDR)
#设定超时时间为2秒
server_socket.settimeout(2)
while True:
    try:
        print("进入")
        recvbytes, client_addr = server_socket.recvfrom(BUFF_LEN)
    except socket.timeout:
        print("超时")
        continue

    print(f'来自 {client_addr} 的请求')

    # 接收到的信息是字节，所以要解码，再反序列化
    message = json.loads(recvbytes.decode('utf8'))
    print(message)
    if message['action'] == '获取信息':
        # 可以从数据库的数据源查询 此用户的信息
        username = message['name']

        # 要发送的信息 对象
        message = {
            'action': '返回信息',
            'info': f'{username} 的信息是:xxxxxxxx'
        }
        # 发送出去的信息必须是字节，所以要先序列化，再编码
        sendbytes = json.dumps(message).encode('utf8')
        server_socket.sendto(sendbytes, client_addr)