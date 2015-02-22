#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request, urllib.error, urllib.parse
import re
import os
import json

# TODO with statement
# ???
file = open('books.json', 'r', encoding='utf-8')
text = file.read()
# converting string to dictionary
# TODO replace eval with json parser
posts = eval(text)


# TODO with statement
# ???
# downloading file with status bar
def download(url, file_name):
    u = urllib.request.urlopen(url)
    f = open(file_name, 'wb')
    buffer = u.read()
    f.write(buffer)
    print(file_name + ' was downloaded')

    f.close()

# DONE move to separate file or DB
# query is simple filter for text of post, queryMatch is RegEx filter for text of post, queryMatchNot is Regex antifilter
folders_text = open('folders.json','r').read();
folders = eval(folders_text)

# creating folders
# DONE creating separate folder
# raising exception if folder are already created
try:
    folder_name = 'downloads'
    os.mkdir(folder_name)
    os.chdir(folder_name)
    for folder in folders:
        os.mkdir(folder['title'])
except OSError:
    pass

cur_dir = os.getcwd()

# TODO REFACTOR TO FUCKOUT
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
                    if len(re.split('(^|[ \(\)\.\,\!\?"])' + folder['query'] + '([ \(\)\,\!\?"]|$)', post['text'])) != 1:
                        os.chdir(folder['title'])
                        cur_dir = os.getcwd()
                        found_folder = True
                elif folder['queryMatch'] != "":
                    if len(re.split(folder['queryMatch'], post['text'])) != 1 and len(re.split(folder['queryMatchNot'], post['text'])) == 1:
                        os.chdir(folder['title'])
                        cur_dir = os.getcwd()
                        found_folder = True
                if found_folder:
                    break

            if not found_folder:
                os.chdir("Другое")
                cur_dir = os.getcwd()


            print(os.getcwd())

            text = re.split('<br>', post['text'])
            folder_name = text[0]
            del text[0]
            readme = '\n'.join(text)  # generating text for readme files

            try:
                try:
                    os.mkdir(folder_name)
                except OSError:
                    pass

                os.chdir(folder_name)
                changed_dir = True

                cur_dir = os.getcwd()

                for attch in attchs:
                    if attch['type'] == 'doc':
                        # downloading book
                        filename = attch['doc']['title']
                        # making filename valid
                        filename = "".join([x if x.isalnum() else "_" for x in filename])
<<<<<<< HEAD
<<<<<<< HEAD
                        download(attch['doc']['url'], filename + "." + attch['doc']['ext'])
=======
                        download(attch['doc']['url'], attch['doc']['title'] + "." + attch['doc']['ext'])
>>>>>>> 706d605afd2422691518306ec0b10ead5fdb710f
=======
                        download(attch['doc']['url'], filename + "." + attch['doc']['ext'])
>>>>>>> 3792aeb0cd2d09aa19a4a8910d959522cf7d92b8
                    elif attch['type'] == 'photo':
                        # downloading  preview image
                        download(attch['photo']['src_big'], 'preview.jpg')
                    elif attch['type'] == 'link':
                        # adding link
                        readme = readme, '\n Ccылка: ', attch['link']['title'], ' ', attch['link']['url']
                    textfile = open('readme.txt', 'w', encoding='utf-8')
                    textfile.write(readme)
                os.chdir('..')
                cur_dir = os.getcwd()
                os.chdir('..')
                cur_dir = os.getcwd()

            except:
                os.chdir('..')
                if changed_dir:
                    os.chdir('..')

                raise
