import threading, time


def fun():
    print("线程开始")
    print("我是线程%s" % threading.current_thread())
    for i in range(10):
        time.sleep(1)
    print("线程结束")


if __name__ == '__main__':
    t = threading.Thread(target=fun, name="TTY")
    t.start()
    t.join()
    print('我好了')
