#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2
import ast
import re
import os

file = open('books.json', 'r')
text = file.read()
# converting string to dictionary
posts = ast.literal_eval(text)


# downloading file with status bar
def download(url, file_name):
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders(u"Content-Length")[0])
    print u"Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()

# query is simple filter for text of post, queryMatch is RegEx filter for text of post, queryMatchNot is Regex antifilter
folders = [
    {u"title": u"Алгоритмы_и_структуры_данных", u"query": "", u"queryMatch": "(Алгоритм|структуры данных)", u"queryMatchNot": ""},
    {u"title": u"Дискретная_математика", u"query": "", u"queryMatch": "(Дискрет|[ ]Граф(ах|ы| |ов))", u"queryMatchNot": ""},
    {u"title": u"Информационная_безопасность", u"query": "", u"queryMatch": "([ ]крипто|защищ|безопасност|хакинг)", u"queryMatchNot": ""},
    {u"title": u"C++", u"query": "", u"queryMatch": "(С\\+\\+|C\\+\\+|С\\+\\+11|C\\+\\+11|cpp|cpp11)", u"queryMatchNot": "(Node|на языке Java|языка программирования Java|\.NET)"},
    {u"title": u"C", u"query": "", u"queryMatch": "([ ]Си[ \/]|язык С[\+]|язык программирования C[^\+\#]|#си|#c[ ]|#с[ ]|Программирование на Си|язык программирования С[^\+#])", u"queryMatchNot": ""},
    {u"title": u"Java", u"query": u"Java", u"queryMatch": "", u"queryMatchNot": ""},
    {u"title": u"Python", u"query": u"Python", u"queryMatch": "", u"queryMatchNot": ""},
    {u"title": u"PHP", u"query": "", u"queryMatch": "(PHP|РНР)", u"queryMatchNot": ""},
    {u"title": u"Ruby_&_Ruby_On_Rails", u"query": u"Ruby", u"queryMatch": "", u"queryMatchNot": ""},
    {u"title": u"JavaScript", u"query": "", u"queryMatch": "(JavaScript|js)", u"queryMatchNot": "([ ]1С|OC Windows Server|jsp)"},
    {u"title": u"Разработка_для_Android", u"query": "", u"queryMatch": "(Android|Андройд|Андроид)", u"queryMatchNot": ""},
    {u"title": u"Разработка_для_Apple", u"query": "", u"queryMatch": "(Swift|Objective-C|iOS)", u"queryMatchNot": u"Spider"},
    {u"title": u"Другое", u"query": "", u"queryMatch": "", u"queryMatchNot": ""}
];

# creating folders
try:
    for folder in folders:
        os.mkdir(folder['title'])
except:
    pass

cur_dir = os.getcwd()

for post in posts:
    post.setdefault('attachments', 0)
    attchs = post['attachments']

    isbook = False
    found_folder = False
    changed_dir = False

    if attchs != 0:
        for attch in attchs:
            if attch['type'] == 'doc':
                isbook = True
                break
        if isbook:
            for folder in folders:
                if folder['query'] != "":
                    if re.search('(^|[ \(\)\.\,\!\?"])' + folder['query'] + '([ \(\)\,\!\?"]|$)', post['text']):
                        os.chdir(folder['title'])
                        cur_dir = os.getcwd()
                        found_folder = True
                elif folder['queryMatch'] != "":
                    if re.search(folder['queryMatch'], post['text']) and not re.search(folder['queryMatchNot'], post['text']):
                        os.chdir(folder['title'])
                        cur_dir = os.getcwd()
                        found_folder = True
                if found_folder:
                    break

            if not found_folder:
                os.chdir(u"Другое")
                cur_dir = os.getcwd()


            print os.getcwd()

            text = re.split('<br>', post['text'])
            folder_name = text[0]
            del text[0]
            readme = '\n'.join(text)  # generating text for readme files

            try:
                try:
                    os.mkdir(folder_name)
                except:
                    pass

                os.chdir(folder_name)
                changed_dir = True

                cur_dir = os.getcwd()

                for attch in attchs:
                    if attch['type'] == 'doc':
                        # downloading book
                        download(attch['doc']['url'], attch['doc']['title'])
                    elif attch['type'] == 'photo':
                        # downloading  preview image
                        download(attch['photo']['src_big'], 'preview.jpg')
                    elif attch['type'] == 'link':
                        # adding link
                        readme = readme, '\n Ccылка: ', attch['link']['title'], ' ', attch['link']['url']
                    textfile = open('readme.txt', 'w')
                    textfile.write(readme)
                os.chdir('..')
                cur_dir = os.getcwd()
                os.chdir('..')
                cur_dir = os.getcwd()

            except:
                os.chdir('..')
                if changed_dir:
                    os.chdir('..')