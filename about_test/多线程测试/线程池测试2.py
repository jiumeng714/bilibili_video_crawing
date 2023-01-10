import multiprocessing


def product(queue, num):
    # 把obj插入队列
    queue.put(num)
    print(f'Product {num}')


def consumer(queue):
    # 从队列中获取obj
    num = queue.get()
    print(f'consumer consumed {num} product')


def main2():
    # 创建队列
    q = multiprocessing.Manager().Queue()

    # 创建进程池
    p = multiprocessing.Pool()

    # 生产商品
    for i in range(5):
        p.apply(func=product, args=(q, i,))

    # 消费生产的商品
    for i in range(5):
        p.apply(func=consumer, args=(q,))

    # 关闭进程池
    p.close()

    # 阻塞进程
    p.join()

    print('主进程结束')

if __name__ == '__main__':

    main2()


