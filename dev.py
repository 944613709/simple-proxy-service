import os
import socket
import threading
import time
from urllib.parse import urlparse

# 代理服务器相关参数
PARAMETERS = {
    'HOST': '127.0.0.1',
    'PORT': 9999,
    'MAX_LISTEN': 50,
    'MAX_LENGTH': 4096,
    'CACHE_SIZE': 1000
}

# 禁止访问的url
No_Access_url = [
    # 'today.hit.edu.cn'
]

# 是否过滤用户IP
Blocked_User = False
# Blocked_User = True

# 钓鱼网站
fishing = {
    # 'today.hit.edu.cn': 'cs.hit.edu.cn'
}

# 缓存目录
cache_dir = './cache/'


def tcp_link(dataSocket, address):
    """
    建立TCP连接
    :param dataSocket: socket
    :param address: IP地址和端口号组成的元组
    :return: 无
    """
    # 接受来自客户端的http请求报文
    message = dataSocket.recv(PARAMETERS['MAX_LENGTH'])
    if len(message) == 0:
        return
    message = message.decode('utf-8', 'ignore')  # 对报文进行解码，忽略错误

    request_line = message.split('\r\n')[0].split()  # 获得请求行，去掉前后空格\

    hostNameTrue = request_line[1]
    print('真实要访问的地址'+ str(hostNameTrue))

    url = urlparse(request_line[1])  # 获得URL
    print('urlparse为：'+ str(url))
    hostIP = address[0]  # 获得主机IP

    # print(request_line[1])
    if url.hostname is not None:
        print('应该转发访问的url.hostname地址:' + url.hostname, end='   ')
        print('真实发起访问的hostIP:'+ hostIP)
    if url.hostname is None:  # 主机名为空
        print('url.hostname为空,关闭该连接')
        dataSocket.close()
        return
    if url.hostname in No_Access_url:  # 主机名被禁止访问
        print(str(url.hostname) + ' is not accessed.')
        dataSocket.close()
        return
    if Blocked_User:  # 用户IP被过滤
        print('the user ' + str(hostIP) + ' is forbidden.')
        dataSocket.close()
        return
    if url.hostname in fishing:  # 主机名为钓鱼网站
        print('fishing from ' + str(url.hostname) + ' to ' + str(fishing[url.hostname]))
        new_hostname = fishing[url.hostname]  # 新的目标主机名
        message = message.replace(request_line[1], 'http://' + new_hostname + '/')
        message = message.replace(url.hostname, new_hostname)  # 将报文重构
        # print(message)
        fish_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 初始化钓鱼网站的socket
        fish_socket.connect((new_hostname, 80))  # 与钓鱼网站的服务器建立连接
        fish_socket.sendall(message.encode())  # 将报文编码发送到钓鱼网站服务器
        while True:
            # 从服务器接收数据,转发给客户端
            buff = fish_socket.recv(PARAMETERS['MAX_LENGTH'])
            if not buff:
                fish_socket.close()
                break
            dataSocket.sendall(buff)
        dataSocket.close()
        fish_socket.close()
        return

    path = cache_dir + url.hostname  # 缓存路径和文件名
    modified = False  # 第一次标记为未修改
    if os.path.exists(path):  # 当已经存在该文件，需要判断服务器是否修改过此网页
        modified_time = os.stat(path).st_mtime  # 缓存文件最后修改的时间
        headers = str('If-Modified-Since: ' + time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(modified_time)))
        # 把modified-time按报文要求格式化
        message = message[:-2] + headers + '\r\n\r\n'  # 把If-Modified-Since字段加入到请求报文中
        # 向服务器发送报文
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((url.hostname, 80))
        server_socket.sendall(message.encode())
        data = server_socket.recv(PARAMETERS['MAX_LENGTH']).decode('utf-8', 'ignore')
        # print(data)
        server_socket.close()
        if data[9:12] == '304':  # 响应码为304，表示网页未变化，从cache中读取网页
            print('the web is not modified, read from cache.')
            with open(path, "rb") as f:
                dataSocket.sendall(f.read())
        else:  # 网页变化，标记为已修改
            modified = True

    if not os.path.exists(path) or modified:  # 如果没有该网页的缓存或者网页已被修改
        # 向服务器发送数据，才能接收到服务器发回来的数据
        print('给真正要访问的地址:' +url.hostname + '发送访问请求')
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((url.hostname, 80))
        server_socket.sendall(message.encode())

        print('发送完毕,代理服务器准备接受来自' +url.hostname + '的数据，随后转发给客户端，并且更新代理服务器cache')
        f = open(path, 'wb')  # 重写缓存
        while True:
            buff = server_socket.recv(PARAMETERS['MAX_LENGTH'])
            if not buff:
                # print(buff)
                # 如果返回空bytes，表示对方关闭了连接
                print('对方服务器发送完毕数据，对方服务器关闭连接')
                f.close()
                server_socket.close()
                break
            f.write(buff)  # 将接收到的数据写入缓存
            dataSocket.sendall(buff)  # 通过代理服务器的dataSocket将接收到的数据转发给客户端
        print('代理服务器转发给客户端数据，转发已完毕')
        print('代理服务器的dataSocket关闭')
        dataSocket.close()


def main():
    print('Initialize...')
    # 初始化socket
    listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定IP地址和端口号
    listenSocket.bind((PARAMETERS['HOST'], PARAMETERS['PORT']))
    # socket的排队个数
    listenSocket.listen(PARAMETERS['MAX_LISTEN'])
    # 创建cache目录
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    print('初始化成功')
    while True:
        # 在循环中监听9999端口，接收到客户端请求则创建一个新线程处理
        print('等待连接')
        dataSocket, address = listenSocket.accept()
        print('接受来自主机' + str(address)  + '的连接')
        threading.Thread(target=tcp_link, args=(dataSocket, address)).start()


if __name__ == '__main__':
    main()
