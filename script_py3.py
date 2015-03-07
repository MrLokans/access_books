#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request, urllib.error, urllib.parse
import re
import os
import json
import sys

# DONE with statement, json lib support
with open('books.json', 'r', encoding='utf-8') as f:
    text = f.read()
    posts = json.loads(text)

# DONE with statement, status bar
# ???
def download(url, file_name):
    u = urllib.request.urlopen(url)

    file_size = int(u.info()["Content-Length"])

    if os.path.isfile(file_name):
        if os.path.getsize(file_name):
            print("File {} already exists, skipping.".format(file_name))
            return None

    chunk_size = 1024
    chunks = file_size // chunk_size
    chunks_downloaded = 0
    print("Downloading {}, {} bytes.".format(file_name, file_size))
    with open(file_name, 'wb') as f:
        while True:
            chunk = u.read(chunk_size)
            percent = int(chunks_downloaded / chunks * 100)
            sys.stdout.write('\r [{0}] {1}%'.format('#' * int(percent / 10), percent))
            if not chunk:
                break
            f.write(chunk)
            f.flush()
            chunks_downloaded += 1
    print()
    print(file_name + ' was downloaded.')

# DONE move to separate file or DB
# query is simple filter for text of post, queryMatch is RegEx filter for text of post, queryMatchNot is Regex antifilter
with open('folders.json', 'r') as f:
    folders_text = f.read()
    folders = json.loads(folders_text)

# creating folders
# DONE creating separate folder
# raising exception if folder are already created
try:
    folder_name = 'downloads'
    if not os.path.exists(folder_name):
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
                        download(attch['doc']['url'], filename + "." + attch['doc']['ext'])
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
