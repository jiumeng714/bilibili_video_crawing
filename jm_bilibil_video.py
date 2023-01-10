"""
爬取B站网页主py文件，2023.01.08
"""
import os.path
import tkinter as tk
import tkinter.ttk as ttk
import json
import tkinter.filedialog as filelog
import tkinter.messagebox
import getVideo as gv  # 获取视频
import getVideoPicture as gp  # 获取视频原图
from tkinter import scrolledtext
import CookieOperation as cookieOP  # 将cookie字符串转字典


global_dict = {}


if __name__ == '__main__':
    existFileResult = os.path.isfile('info.json')
    if not existFileResult:  # 如果不存在这个配置信息文件时，进行创建
        file = open('info.json', 'x')
        new_dict = {'output': '', 'cookie': {'SESSDATA': ''}}
        json.dump(new_dict, file)
        file.close()
    root = tk.Tk()
    root.title("jiumeng_B站视频爬取")
    root.geometry('800x500+250+150')
    root.minsize(800, 500)
    text = scrolledtext.ScrolledText(root, font=('consolas bold', 10), fg='#1d1d1d')
    text.place(relx=0.05, relheight=0.38, relwidth=0.9, rely=0.02)
    label1 = tk.Label(root, text='视频URL: ')
    label1.place(relx=0.01, relheight=0.05, relwidth=0.2, rely=0.42)
    text1 = tk.Text(root, font='consolas 10 bold', fg='#1d1d1d')
    text1.place(relx=0.22, relheight=0.1, relwidth=0.73, rely=0.42)
    label2 = tk.Label(root, text='集数： ')
    label2.place(relx=0.01, relheight=0.05, relwidth=0.2, rely=0.53)
    text2_1 = tk.Text(root, font='consolas 10 bold', fg='#1d1d1d')
    text2_1.place(relx=0.22, relheight=0.05, relwidth=0.2, rely=0.53)

    # 输出目录
    label3 = tk.Label(root, text='目前输出目录：')
    label3.place(relx=0.01, relheight=0.05, relwidth=0.2, rely=0.61)
    text3 = tk.Text(root, font='consolas 10 bold', fg='#1d1d1d')
    text3.place(relx=0.22, relheight=0.05, relwidth=0.52, rely=0.61)

    # 添加text到全局字典中
    global_dict['text'] = text

    # 提供窗口修改输出目录：
    def btn1_fn():
        pathName = filelog.askdirectory()
        if pathName != '':  # 用户选择了路径
            # 输出目录修改成用户所选路径
            file1 = open('info.json', 'r')
            result = json.load(file1)
            file1.close()
            file1 = open('info.json', 'w')
            result['output'] = pathName
            json.dump(result, file1)  # 永久存储该记录
            text3.delete('1.0', 'end')
            text3.insert('end', pathName)  # 重新写入对应的输出目录信息
            file1.close()


    btn1 = ttk.Button(root, text='修改输出目录', style='ZHL.TButton', command=btn1_fn)
    btn1.place(relx=0.75, rely=0.60, relwidth=0.2, relheight=0.07)

    # 最终的输出视频url按钮
    def btn2_fn():
        url = text1.get('1.0', 'end').strip()
        beginSet = text2_1.get('1.0', 'end').strip()
        work_contents = text3.get('1.0', 'end').strip()

        if url == '' or beginSet == ''  or work_contents == '':
            tk.messagebox.showinfo('error', '视频URL、集数、输出目录不能为空！')
        elif str.isdecimal(beginSet) is not True :
            tk.messagebox.showinfo('error', '集数只能输入数字')
        else:
            beginSet = int(beginSet)
            text.insert('end', '准备完毕，接下来进行多线程下载\n', 'jiumeng')
            text.tag_config('jiumeng', foreground='green')

            def fn(n):
                # 关键的核心的实现音视频爬取下载并合并函数。
                gv.main(url, work_contents, global_dict, n)

            try:
                # t = threading.Thread(target=fn, args=(beginSet,))
                # t.start()
                # t.join()
                fn(beginSet)
            except Exception as e:
                print(e)
                tk.messagebox.showinfo('error', str(e))


    # 添加cookie
    def btn3_fn():
        def child_btn_fn():
            new_cookie = child_text.get('1.0', 'end')

            file2 = open('info.json', 'r')
            result = json.load(file2)
            file2.close()
            file2 = open('info.json', 'w')
            new_cookie = new_cookie.replace('\n', '')
            if new_cookie == '':
                new_cookie = 'SESSDATA=12345678;'  # 无效的用户信息，仅防止报错
            new_cookie = cookieOP.getCookieDict(new_cookie)
            result['cookie'] = new_cookie
            json.dump(result, file2)
            file2.close()
            child_window.destroy()
            tk.messagebox.showinfo('success', '保存cookie成功！')

        btn3.focus_set()  # 其他组件不再拥有焦点，聚焦btn3
        # 创建子窗口
        child_window = tk.Toplevel(root)
        child_window.title('输入Cookie')
        child_window.geometry('800x500+250+150')
        child_text = scrolledtext.ScrolledText(child_window, font=('微软雅黑', 10))
        child_text.place(relx=0.05, relheight=0.6, relwidth=0.9, rely=0.05)
        child_btn = ttk.Button(child_window, text='保存Cookie', command=child_btn_fn)
        child_btn.place(relx=0.35, relheight=0.1, relwidth=0.3, rely=0.7)

    # 保存封面
    def btn4_fn():
        url = text1.get('1.0', 'end').strip()
        if url == '':
            tk.messagebox.showinfo('error', '视频URL还没输入！')
        else:
            newBV = gv.getBVbyUrl(url)
            defaultFileName = gp.getDefaultFileName(newBV)
            fileName = filelog.asksaveasfilename(title='请输入要保存的图片名字！', initialfile=defaultFileName)
            if fileName != '':
                gp.getPictureMain(newBV, global_dict, fileName)
                tk.messagebox.showinfo('success', '保存图片成功！')


    btn2 = ttk.Button(root, text='爬取视频', style='ZHL.TButton', command=btn2_fn)
    btn2.place(relx=0.35, rely=0.7, relwidth=0.3, relheight=0.1)

    btn3 = ttk.Button(root, text='添加Cookie', style='ZHL.TButton', command=btn3_fn)
    btn3.place(relx=0.05, rely=0.8, relwidth=0.2, relheight=0.06)

    btn4 = ttk.Button(root, text='保存封面', style='ZHL.TButton', command=btn4_fn)
    btn4.place(relx=0.05, rely=0.89, relwidth=0.2, relheight=0.06)

    def myDefault():
        text.insert('end', '输出结果台：\n注意！如果不加入B站cookie，则最高画质只有480p！\n')
        text2_1.insert('end', 1)
        # 获取输出路径信息
        file3 = open('info.json', 'r')
        myInfo = json.load(file3)
        text3.insert('end', myInfo['output'])
        file3.close()

    myDefault()  # 注入默认的数据
    root.mainloop()
