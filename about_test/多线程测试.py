import time
import threading

def printNumber(n: int) -> None:
    while True:
        print(n)
        time.sleep(n)

for i in range(1, 3):
    t = threading.Thread(target=printNumber, args=(i, ))
    t.start()