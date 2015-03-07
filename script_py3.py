#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request, urllib.error, urllib.parse
import re
import os
import json
import sys

# DONE with statement, json lib support
DOWNLOAD_FOLDER = 'downloads'


def get_books_info(books_file="books.json"):
    """Gets all data from books file"""
    with open('books.json', 'r', encoding='utf-8') as f:
        books_text = f.read()
        return json.loads(books_text)


def get_folders_info(folders_file="folders.json"):
    """Gets all data from folders file"""
    with open('folders.json', 'r') as f:
        folders_text = f.read()
        return json.loads(folders_text)


def prepare_folders(folders):
    """Creates all required folders"""
    try:
        folder_name = DOWNLOAD_FOLDER
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
        os.chdir(folder_name)
        for folder in folders:
            os.mkdir(folder['title'])
    except OSError:
        pass


# DONE with statement, status bar
# ???
def download(url, file_name):
    u = urllib.request.urlopen(url)

    file_size = int(u.info()["Content-Length"])

    if os.path.isfile(file_name):
        if os.path.getsize(file_name) == file_size:
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


# creating folders
# DONE creating separate folder
# raising exception if folder are already created

# TODO avoid changing current directory and use
# preformed pathes instead.
def download_books():
    posts = get_books_info()
    folders = get_folders_info()
    prepare_folders(folders)

    cur_dir = os.getcwd()

    # TODO REFACTOR TO FUCKOUT
    for post in posts:
        post.setdefault('attachments', 0)
        attchs = post['attachments']

        isbook = False
        found_folder = False
        changed_dir = False

        if not attchs:
            continue

        for attch in attchs:
            if attch['type'] == 'doc':
                isbook = True
                break

        if not isbook:
            continue

        for folder in folders:
            if folder['query']:
                result_pattern = '(^|[ \(\)\.\,\!\?"])' + folder['query'] + '([ \(\)\,\!\?"]|$)'
                is_pattern_in_text = len(re.split(result_pattern, post['text'])) != 1
                if is_pattern_in_text:
                    os.chdir(folder['title'])
                    cur_dir = os.getcwd()
                    found_folder = True

            elif folder['queryMatch']:
                is_pattern_in_text = len(re.split(folder['queryMatch'], post['text'])) != 1
                is_prohibited_pattern_absent = len(re.split(folder['queryMatchNot'], post['text'])) == 1
                if is_pattern_in_text and is_prohibited_pattern_absent:
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
        # del text[0]
        readme = '\n'.join(text[1:])  # generating text for readme files

        try:

            if not os.path.exists(folder_name):
                os.mkdir(folder_name)

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

if __name__ == "__main__":
    download_books()
