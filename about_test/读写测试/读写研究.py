import json


def text1():
    file = open('test.json', 'w')
    myDict = {'output': 'jiumeng'}
    json.dump(myDict, file)
    # myDict2 = {'index': 'zhl'}
    # json.dump(myDict2, file)
    file.close()


def text2():
    file = open('test.json', 'r')
    result = json.load(file)
    print(result)

# 读写测试
def text3():
    file = open('test.json', 'r')
    result = json.load(file)
    print(result)
    print(type(result))
    file.close()
    file = open('test.json', 'w')
    result['text'] = 'jiumeng2'
    json.dump(result, file)
    file.close()


# 创建文件测试
def text4():
    file = open('new.json', 'x')
    file.close()

if __name__ == '__main__':
    # text1()
    # text2()
    text3()
    # text4()