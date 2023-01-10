import threading
import time


def thread1_fn():
    for i in range(10):
        time.sleep(0.1)
        print(i)
    print('线程1工作完成')

def thread2_fn():
    print('线程2工作开始')
    print('线程2工作完成')

def main():
    # print(threading.active_count())  # 激活的线程数量
    # print(threading.enumerate())  # 线程信息
    # print(threading.current_thread())  # 当前线程
    jm_thread = threading.Thread(target=thread1_fn, name='T1')
    jm_thread2 = threading.Thread(target=thread2_fn, name='T2')
    jm_thread.start()
    jm_thread2.start()
    jm_thread.join()
    jm_thread2.join()
    print('所有完成了')


if __name__ == '__main__':
    main()