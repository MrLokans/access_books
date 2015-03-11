import os
import sys
import json
import argparse
from vk_api.Vk import Vk

GROUP_ALIAS = "proglib"

# TODO:
# - Work with Post class abstraction?
# - Fix json formatting (spacing).
# - Make setup.py?
# - Turn vk_api into dependency
# - configure argparse

class Post(object):

    def __init__(post_dict):
        pass

    def save_to_file(self, file_name):
        pass

    def __str__(self):
        return "Post dummy."


def get_all_posts(vk, post_num=100):
    posts = []
    offset = 0
    request_num = post_num // 100
    for i in range(request_num):
        r = vk.api_method("wall.get", domain=GROUP_ALIAS, offset=offset, count=100)
        for item in r["response"]["items"]:
            posts.append(item)
        offset += 100
    posts = sorted(posts, key=lambda x: x["likes"]["count"])
    return posts


def generate_json_file(posts, filename="my_books.json"):
    with open(filename, "w", encoding="utf-8") as f:
        for post in posts:
            print(type(post))
            json.dump(post, f, indent=4)


def setup_argparser(args):
    parser = argparse.ArgumentParser(description="Option chooser")
    parser.add_argument('--generate-json', help="An option to generate json.", nargs="?")
    parser.add_argument('-f', help="Filename data is written to.", action="store_const", const="my_books.json")

    args = parser.parse_args()
    print(args)

def print_hello():
    print("Args are working!")


def main():
    setup_argparser(sys.argv)
    # vk = Vk()
    # posts = get_all_posts(vk)
    # generate_json_file(posts)
    # print("Ready to work!")

if __name__ == "__main__":
    main()
