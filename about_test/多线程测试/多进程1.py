from multiprocessing import Process


def main(name):
    print(f'{name}: Hello World')


if __name__ == '__main__':
    # 创建子进程
    p = Process(target=main, args=('LovefishO',))

    # 开始进程
    p.start()

    # 阻塞进程
    p.join()