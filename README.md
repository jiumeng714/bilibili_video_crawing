# bilibili_video_crawing
哔哩哔哩，B站视频和封面原图爬取
主要界面
![image](https://user-images.githubusercontent.com/66453249/213915578-11a9a11f-3db3-4d85-b726-c2cf8a1e3791.png)


现使用时发现还是得有个预览封面的功能，已增添上去。

其中about_test 的文件为测试文件夹，可供思路研究
如果要直接使用，把里面的jm_cmd_B站视频封面爬取.exe文件 + info.json + ffmpeg.exe，
这三个文件拿出来放到一个文件夹里面就可以正常使用


使用时，如果不添加cookie，则下载的视频质量最高只有480P，
添加cookie的方法，打开B站网页，登陆账号，然后F12，点到“网络”，再刷新网页，随便点一条获取到的请求，都有cookie：
![8ca1e6e24159a5427e9961a42e93f77f_74c5e54eae46d197a32370629e692c108a79400e](https://user-images.githubusercontent.com/66453249/211441821-2e0b58ce-8c15-4886-b3b6-068e3a75ebcb.png)
