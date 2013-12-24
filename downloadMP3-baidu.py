#!/usr/bin/env python2
#coding:utf8
"""
Usage: downloadMP3-baidu.py <song list file> <cookie file> 

#######
song list file 默认读取 ./download.txt
cookie file 默认读取 ./cookie.txt

#######
cookie file 格式： 登陆百度音乐后，把 cookie 直接复制到文件里保存即可

#######
没有 cookie 也可正常下载，但只能下载较低码率的音频
"""
import sys,os,time
import re
import urllib, urllib2
import cookielib, Cookie
import HTMLParser

search_url = 'http://music.baidu.com/search'

class GetDownLoadInfoError(ValueError): pass

def setup_opener(cookie=None, user=None, passwd=None):
    cj = cookielib.CookieJar()
    if cookie:
        sck = Cookie.SimpleCookie(cookie)
        for name in sck:
            ck = cookielib.Cookie(version=0, name=name, value=sck[name].value, port=None, 
                    port_specified=False, domain='.baidu.com', domain_specified=False, 
                    domain_initial_dot=False, path='/', path_specified=True, 
                    secure=False, expires=None, discard=True, comment=None, 
                    comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
            cj.set_cookie(ck)
    elif user and passwd:
        raise  # 未实现
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    
def myurlopen(url, data=None, headers=None):
    if headers is None:
        headers = {}
    if data:
        req = urllib2.Request(url, urllib.urlencode(data), headers=headers)
    else:
        req = urllib2.Request(url, headers=headers)
    return urllib2.urlopen(req)


def download_schedule(blocknum, bs , total_size):
    download_size = blocknum * bs
    if total_size < 0:
        total_size = 0
    if download_size > total_size and total_size != 0:
        download_size = total_size
    if total_size > 1024*1024:
        sys.stdout.write('\r%0.2f/%0.2f M' % (download_size/1024.0/1024, total_size/1024.0/1024) )
    elif total_size > 1024:
        sys.stdout.write('\r%0.2f/%0.2f K' % (download_size/1024.0, total_size/1024.0) )
    else:
        sys.stdout.write('\r%0.2f/%0.2f B' % (download_size, total_size) )
    
def download_file(url, filename, outdir='./', show_process=True):
    infp = myurlopen(url)
    if not os.path.isdir(outdir): os.mkdir(outdir)
    outfile = os.path.join(outdir, filename)
    if os.path.exists(outfile):
        print >>sys.stderr, "File exists: %s" % outfile
        return 
    download_temp = outfile + '.download'
    print " "*20, "Downloading", filename, 
    save_filename, headers = urllib.urlretrieve( url, filename=download_temp, reporthook=download_schedule)
    print "" # 打印换行
    if os.path.getsize(save_filename) == 0:
        print >>sys.stderr, "download error:", filename
        return False
    else:
        os.rename(download_temp, outfile)
        return True

def get_download_info(song_id):
    url_format = "http://music.baidu.com/song/%s/download?__o=%%2Fsong%%%s"
    down_page_url = url_format % (song_id, song_id)
    respon = myurlopen(down_page_url)
    down_page_html = respon.read()
    m = re.findall(r'<a\s[^>]*href="([^"]+)"\s[^>]*\sid="(\d{3})"', down_page_html)
    max_rate = 0
    download_url = None
    for href, id in m:
        href = HTMLParser.HTMLParser().unescape(href)
        if not re.match(r'(http|ftp)://', href):
            if href.find("song_id=") < 0:
                continue
            href = "http://music.baidu.com/"+href
        rate = int(id)
        if rate > max_rate:
            max_rate = rate
            download_url = href
    if download_url is None:
        raise GetDownLoadInfoError, "Can not get the download url"
    
    m = re.search(r'<a\s[^>]*class="song-link-hook"\s[^>]*>([^<]+)</a>', down_page_html)
    if m: title = m.group(1)
    else: title = None
    
    m = re.search(r'<span\s[^>]*class="author_list"[^>]*\stitle="([^"]+)"', down_page_html)
    if m: author = m.group(1)
    else: author = None
   
    if title and author:
        filename = "%s-%s" % (title, author)
    elif title:
        filename = "%s" % (title)
    else:
        filename = None
    
    filename = filename.decode('utf8')
    return download_url, filename, max_rate

def get_song_id(key_word):
    fp = myurlopen(search_url, {'key':key_word})
    m = re.search(r'href="/song/([\d]+)', fp.read())
    if not m: raise GetDownLoadInfoError,  "Can not get the song id"
    song_id = m.group(1)
    return song_id

def download_by_keywork(key_word):
    song_id = get_song_id(key_word)
    download_url, filename, rate =  get_download_info(song_id)
    print download_url, filename, u"码率:"+str(rate)
    download_file(download_url, filename+".mp3")
    
def main():
    if len(sys.argv) < 2:
        listfile = "./download.txt"
    else:
        listfile = sys.argv[1]
    if len(sys.argv) < 3:
        cookie_file = "./cookie.txt"
    else:
        cookie_file = sys.argv[2]
    if not os.path.exists(cookie_file):
        open(cookie_file, 'wb').close() # 创建文件
        cookie_str = ''
    else:
        cookie_str = open(cookie_file).read().strip()
    if not cookie_str:
        print >> sys.stderr, u"Warnging: 将登陆后的 cookie 写入 %s 可以下载高码率的资源" % (cookie_file)
    setup_opener(cookie=cookie_str)
    fail_list = []
    for line in open(listfile):
        line = line.strip()
        if len(line) ==0:
            continue
        try:
            key_word = line.decode(sys.stdin.encoding).encode('utf8')
            print "\nSearching ", line
            download_by_keywork(key_word)
        except Exception, e:
            #import traceback
            #traceback.print_exc()
            fail_list.append(line)
            print e
            print line, "download fail"
    print u"\n%s\n失败列表:\n%s\n" % ("#"*60,"\n".join(fail_list))
    
def test():
    #setup_opener(cookie=g_cookie_str)
    #download_url, filename, rate = get_download_info(87603531)
    #print download_url, filename.decode('utf8'), rate
    #download_file(url, '1.mp3', 'D:/')
    download_file('http://www.baidu.com/', 'baidu.html')
    pass

if __name__ == '__main__':
    try:
        #test()
        main()
    except Exception, e:
        import traceback
        traceback.print_exc()
        print e
    finally:
        if os.name == 'nt':
            os.system("pause")
