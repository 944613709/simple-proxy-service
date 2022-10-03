import os
import socket
import threading
import time
from urllib.parse import urlparse

# 代理服务器相关参数
PARAMETERS = {
    'HOST': '127.0.0.1',
    'PORT': 10086,
    'MAX_LISTEN': 50,
    'MAX_LENGTH': 4096,
    'CACHE_SIZE': 20000
}
#仅可访问白名单
White_url = [
    'cs.hit.edu.cn'
]

# 禁止访问的黑名单
Black_url = [
    'today.hit.edu.cn'
]

# 过滤用户IP
Blocked_User_IP = [
    # '127.0.0.1'
]


# 钓鱼
fishingWeb = {
     'jwts.hit.edu.cn': 'cs.hit.edu.cn'
}

# 缓存目录
cache_dir = './MyCache/'


def socket_tcp(dataSocket, address, threadId):
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


    url = urlparse(request_line[1])  # 获得URL

    hostIP = address[0]  # 获得主机IP

    if url.hostname in Black_url:  # 主机名被禁止访问
        print('线程:' + str(threadId) + '-->' + str(url.hostname) + ' is not accessed.')
        dataSocket.close()
        return

    # #只允许白名单内的可以被访问
    # if url.hostname not in White_url:
    #     print('线程:' + str(threadId) + '-->' + str(url.hostname) + ' is not accessed.')
    #     dataSocket.close()
    #     return

    print('线程:' + str(threadId) + '-->' + '真实要访问的地址'+ str(hostNameTrue))
    print('线程:' + str(threadId) + '-->' + 'urlparse为：'+ str(url))
    # print(request_line[1])

    if url.hostname is not None:
        print('线程:' + str(threadId) + '-->' + ' 应该转发访问的url.hostname地址:' + url.hostname, end='   ')
        print('线程:' + str(threadId) + '-->' + '真实发起访问的hostIP:'+ hostIP)

    if url.hostname is None:  # 主机名为空
        print('线程:' + str(threadId) + '-->' + 'url.hostname为空,关闭该连接')
        dataSocket.close()
        return


    if hostIP in Blocked_User_IP:  # 用户IP被过滤
        print('线程:' + str(threadId) + '-->' + '该用户的IP' + str(hostIP) + '已经被代理服务器禁止')
        dataSocket.close()
        return

    #钓鱼情况
    if url.hostname in fishingWeb:  # 主机名为钓鱼网站
        hostName = fishingWeb[url.hostname]  # 新的目标主机名
        print('线程:' + str(threadId) + '-->' + '对' + str(url.hostname) + '进行钓鱼，钓鱼到-> ' + str(hostName))
        
        #更换报文头请求地址
        message = message.replace(request_line[1], 'http://' + hostName + '/')
        message = message.replace(url.hostname, hostName)  

        fishDataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 初始化钓鱼网站的socket
        fishDataSocket.connect((hostName, 80))  # 与钓鱼网站的服务器建立连接
        fishDataSocket.sendall(message.encode())  # 将报文编码发送到钓鱼网站服务器
        
        while True:
            # 从服务器接收数据,转发给客户端
            buff = fishDataSocket.recv(PARAMETERS['MAX_LENGTH'])
            if not buff:
                fishDataSocket.close()
                break
            dataSocket.sendall(buff)
        dataSocket.close()
        fishDataSocket.close()
        return

    #非钓鱼情况
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
        print('线程:' + str(threadId) + '-->' + '响应码为'+data[9:12])
        if data[9:12] == '304':  # 响应码为304，表示网页未变化，从cache中读取网页
            print('线程:' + str(threadId) + '-->' + '响应码304-当前服务器资源未被修改，直接读取代理服务器cache返回')
            with open(path, "rb") as f:
                dataSocket.sendall(f.read())
        else:  # 网页变化，标记为已修改
            modified = True

    if not os.path.exists(path) or modified:  # 如果没有该网页的缓存或者网页已被修改
        # 向服务器发送数据，才能接收到服务器发回来的数据
        print('线程:' + str(threadId) + '-->' + '给真正要访问的地址:' +url.hostname + '发送访问请求')
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((url.hostname, 80))
        server_socket.sendall(message.encode())

        print('线程:' + str(threadId) + '-->' + '发送完毕,代理服务器准备接受来自' +url.hostname + '的数据，随后转发给客户端，并且更新代理服务器cache')
        f = open(path, 'wb')  # 重写缓存
        while True:
            buff = server_socket.recv(PARAMETERS['MAX_LENGTH'])
            if not buff:
                # print(buff)
                # 如果返回空bytes，表示对方关闭了连接
                print('线程:' + str(threadId) + '-->' + '对方服务器发送完毕数据，对方服务器关闭连接')
                f.close()
                server_socket.close()
                break
            f.write(buff)  # 将接收到的数据写入缓存
            dataSocket.sendall(buff)  # 通过代理服务器的dataSocket将接收到的数据转发给客户端
        print('线程:' + str(threadId) + '-->' + '代理服务器转发给客户端数据，转发已完毕')
        print('线程:' + str(threadId) + '-->' + '代理服务器的dataSocket关闭')
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
    threadId = 1
    while True:
        # 在循环中监听9999端口，接收到客户端请求则创建一个新线程处理
        print('等待连接')
        dataSocket, address = listenSocket.accept()
        print('接受来自主机' + str(address)  + '的连接')
        threading.Thread(target=socket_tcp, args=(dataSocket, address, threadId)).start()
        threadId = threadId+1


if __name__ == '__main__':
    main()
