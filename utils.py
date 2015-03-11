import os
import json
import argparse
import pprint
from vk_api.Vk import Vk

GROUP_ALIAS = "proglib"

# TODO:
# - Work with Post class abstraction?
# - Fix json formatting (spacing).
# - Make setup.py?
# - Turn vk_api into dependency

class Post(object):

    def __init__(post_dict):
        pass

    def save_to_file(self, file_name):
        pass

    def __str__(self):
        return "Post dummy."


def get_all_posts(vk, post_num=100):
    pp = pprint.PrettyPrinter(indent=4)
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


def main():
    vk = Vk()
    posts = get_all_posts(vk)
    generate_json_file(posts)
    # print("Ready to work!")

if __name__ == "__main__":
    main()
