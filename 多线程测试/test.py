print('主线程执行代码') 

# 从 threading 库中导入Thread类
from threading import Thread
from time import sleep

# 定义一个函数，作为新线程执行的入口函数
def threadFunc(arg1,arg2):
    print('子线程 开始')
    print(f'线程函数参数是：{arg1}, {arg2}')
    sleep(5)
    print('子线程 结束')


# 创建 Thread 类的实例对象
thread = Thread(
    # target 参数 指定 新线程要执行的函数
    # 注意，这里指定的函数对象只能写一个名字，不能后面加括号，
    # 如果加括号就是直接在当前线程调用执行，而不是在新线程中执行了
    target=threadFunc, 

    # 如果 新线程函数需要参数，在 args里面填入参数
    # 注意参数是元组， 如果只有一个参数，后面要有逗号，像这样 args=('参数1',)
    args=('参数1', '参数2')
)

# 执行start 方法，就会创建新线程，
# 并且新线程会去执行入口函数里面的代码。
# 这时候 这个进程 有两个线程了。
thread.start()

# 主线程的代码执行 子线程对象的join方法，
# 就会等待子线程结束，才继续执行下面的代码
thread.join()
print('主线程结束')

