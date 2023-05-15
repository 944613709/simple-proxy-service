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
    'CACHE_SIZE': 65507
}
# 仅可访问白名单
White_url = [
    'cs.hit.edu.cn',  # 可访问，访问快
    'jwts.hit.edu.cn',  # 可访问且可以缓存，但是访问慢
    # 'today.hit.edu.cn',  # 这里默认是https，需要人工加上http，但是显示全字符
    'software.hit.edu.cn',  # 可访问
    'example.com',#可访问且可以缓存，多刷新几次，还挺快
    'www.7k7k.com',  # 可访问但是补全还有关联的子host "i1.7k7kimg.cn"
    'www.7k7kjs.cn',
    # 'info.cern.ch'
]

# 禁止访问的黑名单
Black_url = [
    # 'today.hit.edu.cn'
]

# 过滤用户IP
Blocked_User_IP = [
    '127.0.0.1'
]

# 钓鱼
fishingWeb = {
    #访问快
    'jwts.hit.edu.cn': 'cs.hit.edu.cn'
}

# 缓存目录
cache_dir = './MyCache/'

"""
从请求报文来获得hostname,port
"""


def parseToHostnameAndPort(message):
    message_line = message.split('\r\n')[1].split()

    # 情况1 today.hit.edu.cn:443
    # 情况2 cs.hit.edu.cn  (默认端口80)
    target_host_with_port = message_line[1]

    target_host_line = target_host_with_port.split(':')
    target_host_without_port = target_host_line[0]

    # 情况1 today.hit.edu.cn:443
    if (len(target_host_line) == 2):
        target_port = int(target_host_line[1])
    else:  # 情况2 cs.hit.edu.cn,默认端口80
        target_port = 80

    return target_host_without_port, target_port


def socket_tcp(dataSocket, address, threadId):
    """
    建立TCP连接
    :param dataSocket: socket
    :param address: IP地址和端口号组成的元组
    :return: 无
    """
    # 接受来自客户端的http请求报文
    message = dataSocket.recv(PARAMETERS['MAX_LENGTH'])

    # 如果返回空bytes，请求报文为空，不需要处理
    if len(message) == 0:
        return

    # 读取的字节数据是bytes类型，需要解码为字符串
    message = message.decode('utf-8', 'ignore')  # 对报文进行解码，忽略错误

    # print("message:")
    # print(message)
    # message.split('\r\n')[0]拿到请求头

    # GET http://www.sina.com/ HTTP/1.1
    request_line = message.split('\r\n')[0].split()  # 获得请求行，去掉前后空格\

    target_host_without_port, target_port = parseToHostnameAndPort(message)
    # print('------target_host：------')
    # print(target_host_without_port)
    # print(target_port)
    # print('------target_host：------')

    # message.split('\r\n')[0].split()再以空格切分，request_line[1]拿到url地址
    target_url = request_line[1]
    # 拿到情况1，http://cs.hit.edu.cn/
    # 情况2，today.hit.edu.cn:443

    url = urlparse(request_line[1])  # 获得URLparse划分以辅助对比
    hostIP = address[0]  # 获得原主机IP

    if hostIP in Blocked_User_IP:  # 用户IP被过滤
        print('线程:' + str(threadId) + '---------用户已被禁止访问------------')
        print('线程:' + str(threadId) + '-->' + '该用户的IP' + str(hostIP) + '已经被代理服务器禁止')
        print('线程:' + str(threadId) + '---------用户已被禁止访问------------')
        dataSocket.close()
        return

    if target_host_without_port in Black_url:  # 主机名被禁止访问
        print('线程:' + str(threadId) + '-->' + str(target_host_without_port) + '在黑名单，禁止访问')
        dataSocket.close()
        return

    # 只允许白名单内的可以被访问
    if target_host_without_port not in White_url:
        # print('线程:' + str(threadId) + '-->' + str(target_host_without_port) + '不在白名单，禁止访问')
        dataSocket.close()
        return
    # 黑名单内的不允许访问
    # if target_host_without_port in Black_url:
    #     print('线程:' + str(threadId) + '-->' + str(target_host_without_port) + '黑名单，禁止访问')
    #     dataSocket.close()
    #     return

    print('------target_host：------')
    print("目的host:" + target_host_without_port)
    print("目的port:" + str(target_port))
    print('------target_host：------')
    # print('线程:' + str(threadId) + '-->' + '真实要访问的地址' + str(target_url))
    # print('线程:' + str(threadId) + '-->' + 'urlparse为：' + str(url))
    # print(request_line[1])

    # 钓鱼情况
    if target_host_without_port in fishingWeb:  # 主机名为钓鱼网站
        fishing_host_without_port = fishingWeb[target_host_without_port]
        # http默认80
        fishing_host_port = 80

        print('线程:' + str(threadId) + '---------钓鱼启动------------')
        print('线程:' + str(threadId) + '-->' + '对' + str(target_host_without_port) + '进行钓鱼，钓鱼到-> ' + str(
            fishing_host_without_port))

        print('------------改之前')
        print(message)
        # # 更换报文头请求地址
        # message = message.replace(request_line[1], 'http://' + fishing_host_without_port + '/')
        # 把host全改成钓鱼的
        message = message.replace(target_host_without_port, fishing_host_without_port)
        print('------------改之后')
        print(message)

        fishDataSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 初始化钓鱼网站的socket
        fishDataSocket.connect((fishing_host_without_port, fishing_host_port))  # 与钓鱼网站的服务器建立连接
        fishDataSocket.sendall(message.encode())  # 将报文编码发送到钓鱼网站服务器

        print('线程:' + str(threadId) + '-->' + '正在从钓鱼服务器接收数据并转发,请稍后')
        while True:
            # 从钓鱼目的服务器接收数据,转发给客户端
            buff = fishDataSocket.recv(PARAMETERS['MAX_LENGTH'])
            if not buff:
                fishDataSocket.close()
                break
            dataSocket.sendall(buff)
        print('线程:' + str(threadId) + '-->' + '接收数据完毕')
        dataSocket.close()
        fishDataSocket.close()
        print('线程:' + str(threadId) + '---------钓鱼结束------------')
        return

    #######
    # 非钓鱼情况
    if target_host_without_port is not None:
        print('线程:' + str(threadId) + '---------代理服务器工作开始------------')
        print('线程:' + str(threadId) + '-->' + 'target:目标host:' + target_host_without_port,
              end='   ')
        print('线程:' + str(threadId) + '-->' + 'port:目标端口:' + str(target_port),
              end='   ')
        print('线程:' + str(threadId) + '-->' + 'source:客户端hostIP:' + hostIP)
        print('线程:' + str(threadId) + '-->' + '真实要访问的地址' + str(target_url))
        print('线程:' + str(threadId) + '-->' + 'urlparse为：' + str(url))

    if target_host_without_port is None:  # 主机名为空
        print('线程:' + str(threadId) + '-->' + 'target_host_without_port为空,关闭该连接')
        dataSocket.close()
        return

    # 拿到情况1，http://cs.hit.edu.cn/
    # 情况2，today.hit.edu.cn:443

    filename = target_url.replace(":", '').replace('.', '').replace('/', '').replace('?', '').replace('*', '').replace('<', '').replace('>', '').replace('|', '')
    path = cache_dir + filename + '.txt'  # 组合缓存路径和文件名
    modified = False  # 第一次标记为未修改

    # 不是第一次访问该网页
    if os.path.exists(path):  # 当已经存在该文件，需要判断服务器是否修改过此网页

        # 在path路径下调用系统stat拿到最后修改时间
        modified_time = os.stat(path).st_mtime  # 缓存文件最后修改的时间

        # 把modified-time按报文要求格式化
        headers = str('If-Modified-Since: ' + time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(modified_time)))

        # '\r'
        # 回车，回到当前行的行首，而不会换到下一行，如果接着输出的话，本行以前的内容会被逐一覆盖；
        # '\n'
        # 换行，换到当前位置的下一行，而不会回到行首；

        # message[:-2]去掉最后两行空白的\r\n\r\n
        message = message[:-2] + headers + '\r\n\r\n'  # 把If-Modified-Since字段加入到请求报文中

        # 向服务器发送报文
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((target_host_without_port, target_port))
        server_socket.sendall(message.encode())
        data = server_socket.recv(PARAMETERS['MAX_LENGTH']).decode('utf-8', 'ignore')
        # print(data)
        server_socket.close()

        # data是HTTP/1.1 304 ok
        print('线程:' + str(threadId) + '-->' + '响应码为' + data[9:12])
        if data[9:12] == '304':  # 响应码为304，表示网页未变化，从cache中读取网页
            print('--------------------------------------------')
            print('线程:' + str(threadId) + '-->' + '响应码304-当前服务器资源未被修改，直接读取代理服务器cache返回')
            print('304')
            print('--------------------------------------------')
            print('线程:' + str(threadId) + '---------代理服务器，304读取缓存，工作结束------------')
            # 二进制文件就用二进制方法读取'rb'
            with open(path, "rb") as f:
                # 直接把代理服务器缓存里的目标服务器资源发送给客户端
                dataSocket.sendall(f.read())
        else:  # 网页变化，标记为已修改
            modified = True
            # 使得进行下面的代码段运行

    if not os.path.exists(path) or modified:  # 如果没有该网页的缓存，或者网页已被修改（拿到modified=true)
        # 向服务器发送数据，才能接收到服务器发回来的数据
        print('线程:' + str(threadId) + '-->' + '给真正要访问的地址:' + target_host_without_port + '发送访问请求')
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((target_host_without_port, target_port))
        server_socket.sendall(message.encode())

        print('线程:' + str(
            threadId) + '-->' + '代理服务器准备接受来自' + target_host_without_port + ':' + str(
            target_port) + '的数据，随后转发给客户端，并且更新代理服务器cache')
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
        dataSocket.close()
        print('线程:' + str(threadId) + '---------代理服务器，工作结束------------')


def main():
    print("初始化socket")

    # 实例化一个socket对象
    # 参数 AF_INET 表示该socket网络层使用IP协议
    # 参数 SOCK_STREAM 表示该socket传输层使用TCP协议
    listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 绑定IP地址和端口号
    listenSocket.bind((PARAMETERS['HOST'], PARAMETERS['PORT']))
    # 使socket处于监听状态，等待客户端的连接请求
    # 参数 MAX_LISTEN 表示 最多可以有MAX_LISTEN处于排队等待连接
    # socket的排队个数
    listenSocket.listen(PARAMETERS['MAX_LISTEN'])

    # 创建cache目录
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)

    print('初始化成功')
    # 线程id
    threadId = 1
    while True:
        # 在循环中监听9999端口，接收到客户端请求则创建一个新线程处理
        print('等待连接')
        # datasocket数据socket
        # address--客户端IP地址和端口号
        dataSocket, address = listenSocket.accept()
        print('接受来自主机' + str(address) + '的连接')
        threading.Thread(target=socket_tcp, args=(dataSocket, address, threadId)).start()
        threadId = threadId + 1


if __name__ == '__main__':
    main()
