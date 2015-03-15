#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib.request, urllib.error, urllib.parse
import re
import os
import json
import sys
import time


# DONE with statement, json lib support
DOWNLOAD_FOLDER = 'downloads'
BOOKS_JSON = 'books.json'
FOLDERS_JSON = 'folders.json'


class ProgressBar(object):

    def __init__(self, max_value, fill_character="#", rem_character="-", update_time=0.04, width=80):
        self.cur_value = 0
        self.max_value = max_value
        self.fill_char = fill_character
        self.rem_char = rem_character
        self.width = width

        self.update_time = update_time
        self.effective_width = self.width - 2
        self.start_time = time.time()

        self.print_bar(cur_value=0)

    def update(self, cur_value, extra_text=""):
        if cur_value > self.max_value + 1:
            raise ValueError("Update value is too big.")

        if cur_value == self.max_value:
            self.print_bar(cur_value=self.max_value, extra_text=extra_text)

        self.cur_time = time.time()
        self.cur_value = cur_value
        self.delt_t = self.cur_time - self.start_time
        if self.delt_t >= self.update_time:
            self.print_bar(self.cur_value, extra_text=extra_text)
            self.start_time = self.cur_time
            self.cur_time = time.time()

    def print_bar(self, cur_value, extra_text=""):
        ratio = cur_value / self.max_value
        current_progress = int(ratio * 100)
        num_of_hashes = int(ratio * self.effective_width)
        num_of_minuses = self.effective_width - num_of_hashes
        sys.stdout.write('\r[{hashes}{minuses}] {percentage}% {info}'.format(hashes=self.fill_char * num_of_hashes,
                                                                             minuses='-' * num_of_minuses,
                                                                             percentage=current_progress,
                                                                             info=extra_text))
        sys.stdout.flush()


def transform_speed_value(current_speed, suffix_type='speed'):
    """Transforms data into human readable format"""

    speed_suffixes = ['bps', 'kbps', 'mbps', 'gbps', 'tbps']
    size_suffixes = ['B', 'KB', 'MB', 'GB', 'TB']

    if suffix_type == 'speed':
        suffixes = speed_suffixes
    elif suffix_type == 'size':
        suffixes = size_suffixes
    else:
        raise TypeError("Incorrect suffix type {}.".format(suffix_type))

    if current_speed == 0:
        return 0
    i = 0
    while current_speed >= 1024 and i < len(suffixes) - 1:
        current_speed /= 1024
        i += 1
    return "{:.2f} {}".format(current_speed, suffixes[i])


def calculate_speed(time_spent, data_downloaded):
    """Returns average download speed"""
    return int(data_downloaded / time_spent)


def draw_progress_bar(cur_value, max_value, width=72, symbol='#', extra_info=""):
    """Draws progress, evidently"""
    current_progress = int((cur_value * 100) / max_value)

    effective_width = width - 2

    num_of_hashes = int((cur_value * effective_width) / max_value)
    num_of_minuses = effective_width - num_of_hashes

    sys.stdout.write('\r[{hashes}{minuses}] {percentage}% {info}'.format(hashes=symbol * num_of_hashes,
                                                                         minuses='-' * num_of_minuses,
                                                                         percentage=current_progress,
                                                                         info=extra_info))
    sys.stdout.flush()


def gen_dict_from_json(file_name):
    """Returns dict from json file"""
    with open(file_name, 'r', encoding="utf-8") as f:
        text = f.read()
        return json.loads(text)


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
# Fix progress bar, shows extra percents
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
    print("Downloading {filename}, {size}.".format(filename=file_name,
                                                   size=transform_speed_value(file_size, suffix_type='size')))
    pb = ProgressBar(max_value=chunks)
    with open(file_name, 'wb') as f:
        start_time = time.time()
        while True:
            chunk = u.read(chunk_size)
            extra_time = time.time()
            delta_time = extra_time - start_time
            delta_time = delta_time if delta_time else 0.0001
            avg_speed = int(chunks_downloaded * chunk_size / delta_time)
            str_info = transform_speed_value(avg_speed)
            # draw_progress_bar(chunks_downloaded, chunks, extra_info=str_info)
            pb.update(cur_value=chunks_downloaded, extra_text=str_info)
            if not chunk:
                break
            f.write(chunk)
            f.flush()
            chunks_downloaded += 1
    print()
    print(file_name + ' was downloaded.')


def clear_filename(file_name):
    if "/" in file_name:
        return file_name.replace("/", "-")
    else:
        return file_name


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


def download_attachment(attch, folder_path, readme):
    """Downloads attachment according to its type"""
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
        readme = " ".join([readme, '\n Ccылка: ', attch['link']['title'], ' ', attch['link']['url']])
    textfile = open(os.path.join(folder_path, 'readme.txt'), 'w', encoding='utf-8')
    textfile.write(readme)
# creating folders
# DONE creating separate folder
# raising exception if folder are already created


# TODO avoid changing current directory and use
# preformed pathes instead.
def download_books():
    posts = gen_dict_from_json(BOOKS_JSON)
    folders = gen_dict_from_json(FOLDERS_JSON)
    prepare_folders(folders)

    # TODO REFACTOR TO FUCKOUT
    # It's broken when filename contains '/' symbol,
    # so this symbol is now replaced.
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

        # print(os.getcwd())
        if '<br>' in post['text']:
            text = re.split('<br>', post['text'])
        else:
            # So sometimes we face the case that
            # no <br> tag is in description, so we
            # split by (year, type) group
            text = re.split(r'\(([\d]{4}), ([a-zA-Z]+)\)', post['text'])
        folder_name = clear_filename(text[0])

        readme = '\n'.join(text[1:])  # generating text for readme files

        folder_group = clear_filename(get_foldergroup(folders, post))
        folder_path = os.path.join(DOWNLOAD_FOLDER, folder_group, folder_name).strip(" ")

        try:
            if not os.path.exists(folder_path):
                os.mkdir(folder_path)

        except FileNotFoundError as e:
            print("Folder Error", e)

        for attch in attchs:
            download_attachment(attch, folder_path, readme)

if __name__ == "__main__":
    download_books()
    # p = ProgressBar(999)
    # for i in range(100):
    #     time.sleep(0.01)
    #     p.update(i)
    # p.print_bar(cur_value=1000)
