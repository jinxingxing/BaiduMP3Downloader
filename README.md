baiduMp3Download
================

根据关键字自动搜索百度音乐下载mp3，添加cookie后可下载320kps的mp3文件    

Usage: downloadMP3-baidu.py {song list file} [cookie file]


song list file 默认读取 ./download.txt    
cookie file 默认读取 ./cookie.txt


song list file 格式: 一行一首歌名即可， 多个关键字（歌手等）以空格分隔    
cookie file 格式： 登陆百度音乐后把 cookie 直接复制到文件里保存即可    


没有 cookie 也可正常下载，但只能下载较低码率的音频
