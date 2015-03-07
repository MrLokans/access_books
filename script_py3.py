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
        for folder in folders:
            os.mkdir(os.path.join(DOWNLOAD_FOLDER, folder['title']))
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


def get_foldergroup(folders_dict, post):
    """Specifies group folder (e.g C, C++, or 'Другое') """
    folder_group = ""
    found_folder = False
    for folder in folders_dict:
        if folder['query']:
            result_pattern = '(^|[ \(\)\.\,\!\?"])' + folder['query'] + '([ \(\)\,\!\?"]|$)'
            is_pattern_in_text = len(re.split(result_pattern, post['text'])) != 1
            if is_pattern_in_text:
                folder_group = folder['title']
                found_folder = True

        elif folder['queryMatch']:
            is_pattern_in_text = len(re.split(folder['queryMatch'], post['text'])) != 1
            is_prohibited_pattern_absent = len(re.split(folder['queryMatchNot'], post['text'])) == 1
            if is_pattern_in_text and is_prohibited_pattern_absent:
                folder_group = folder['title']
                found_folder = True
        if found_folder:
            break

    if not found_folder:
        folder_group = "Другое"

    return folder_group


# creating folders
# DONE creating separate folder
# raising exception if folder are already created

# TODO avoid changing current directory and use
# preformed pathes instead.
def download_books():
    posts = get_books_info()
    folders = get_folders_info()
    prepare_folders(folders)

    # TODO REFACTOR TO FUCKOUT
    for post in posts:
        post.setdefault('attachments', 0)
        attchs = post['attachments']

        isbook = False
        # found_folder = False
        # folder_group = ""

        if not attchs:
            continue

        for attch in attchs:
            if attch['type'] == 'doc':
                isbook = True
                break

        if not isbook:
            continue

        print(os.getcwd())

        text = re.split('<br>', post['text'])
        folder_name = text[0]

        readme = '\n'.join(text[1:])  # generating text for readme files

        folder_group = get_foldergroup(folders, post)
        folder_path = os.path.join(DOWNLOAD_FOLDER, folder_group, folder_name).strip(" ")

        try:
            if not os.path.exists(folder_path):
                print(os.listdir())
                os.mkdir(os.path.join(folder_path))

        except FileNotFoundError as e:
            print("Folder Error", e)

        for attch in attchs:
            if attch['type'] == 'doc':
                # downloading book
                filename = attch['doc']['title']
                # making filename valid
                filename = "".join([x if x.isalnum() else "_" for x in filename])
                filename = filename + "." + attch['doc']['ext']
                filename = os.path.join(folder_path, filename)
                download(attch['doc']['url'], filename)
            elif attch['type'] == 'photo':
                # downloading  preview image
                filename = os.path.join(folder_path, 'preview.jpg')
                download(attch['photo']['src_big'], filename)
            elif attch['type'] == 'link':
                # adding link
                readme = readme, '\n Ccылка: ', attch['link']['title'], ' ', attch['link']['url']
            textfile = open(os.path.join(folder_path, 'readme.txt'), 'w', encoding='utf-8')
            textfile.write(readme)

if __name__ == "__main__":
    download_books()
