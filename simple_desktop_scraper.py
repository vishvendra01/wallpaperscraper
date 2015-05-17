__author__ = "Vishvendra Singh"
__version__ = 0.1

import os
import sys
import time

from bs4 import BeautifulSoup
import requests

import progressbar

try:
    import cPickle as pickle
except ImportError:
    import pickle


# global constants
CONFIG_FILE = ".img_dl_links.p"
DOWNLOAD_PATH = ".dl_path.txt"
BASE_URL = "http://simpledesktops.com"


def image_links_from_page(htmlsource):
    """returns images links and address of next page"""
    img_links = []
    soup = BeautifulSoup(htmlsource)
    div_src = soup.find_all("div", {"class": "desktop"})
    for each_div in div_src:
        soup2 = BeautifulSoup(str(each_div))
        img_links.append(soup2.find("img")["src"])

    img_links = extract_img_url(img_links)

    next_link = soup.find("a", {"class": "more"})
    if next_link:
        return img_links, next_link["href"]
    else:
        return img_links, None


def extract_img_url(img_links):
    tmp = []
    for each_link in img_links:
        if "jpg" in each_link:
            tmp.append(each_link[0:each_link.find("jpg") + 3])
        elif "png" in each_link:
            tmp.append(each_link[0: each_link.find("png") + 3])
    return tmp


def file_exist_status(file_name):
    """check existence of a file. used for checking status of config file"""
    if os.path.isfile(file_name) and os.access(file_name, os.R_OK):
        return True
    else:
        return False


def get_all_image_links():
    """retrieves all image links of images available on simpledesktops.com"""
    pbar = progressbar.AnimatedProgressBar(end=47, width=50)
    print("getting all links for image urls")
    pbar.show_progress()
    img_dl_links = []
    next_link = "/browse/1/"
    while next_link:
        fh = requests.get("%s%s" % (BASE_URL, next_link), allow_redirects=False)
        # print fh.url
        result = image_links_from_page(fh.text)
        fh.close()
        img_dl_links.append(result[0])
        next_link = result[1]
        pbar += 1
        pbar.show_progress()
        # print next_link
    # flattening list of links
    print()
    tmp = []
    for x in img_dl_links:
        for y in x:
            tmp.append(y)
    img_dl_links = tmp
    return img_dl_links


def query():
    """Prompts user for a yes/no answer
    if user responds with 'yes', 'ye', or 'y', return True
    if user responds with 'no' or 'n', return False.
    else: return None
    """

    # raw_input returns the empty string for "enter"
    yes = {'yes', 'y', 'ye', ''}
    no = {'no', 'n'}

    choice = input().lower()
    if choice in yes:
        return True
    elif choice in no:
        return False
    else:
        sys.stdout.write("Please respond with 'yes' or 'no'")


def get_dl_path():
    print("input path to save files:")
    PATH = input()
    if os.path.isdir(PATH) and os.access(PATH, os.W_OK):
        print("given path accepted")
        return PATH
    else:
        print("path is not valid. Create now? (Y/n):")
        answer = query()
        if answer:
            os.makedirs(PATH)
        else:
            get_dl_path()


def download_images(img_dl_links, PATH):
    """download images and remove downloaded images from img_links"""
    end = len(img_dl_links)
    pbar = progressbar.AnimatedProgressBar(end=end, width=50)
    print('downloading wallpapers..')
    pbar.show_progress()
    for img_url in img_dl_links:
        tmp = requests.request('get', img_url)
        with open(os.path.join(PATH, img_url.split('/')[-1]), 'w') as f:
            f.write(str(tmp.content))
        update_config_file(img_url)
        time.sleep(1)
        pbar += 1
        pbar.show_progress()
    print()


def update_config_file(img_link):
    """remove downloaded links from config file"""
    img_dl_links = pickle.load(open(CONFIG_FILE, "rb"))
    img_dl_links.pop(img_dl_links.index(img_link))
    pickle.dump(img_dl_links, open(CONFIG_FILE, "wb"))


def main():
    if file_exist_status(CONFIG_FILE) and file_exist_status(DOWNLOAD_PATH):
        img_dl_links = pickle.load(open(CONFIG_FILE, "rb"))
        PATH = ""
        with open(DOWNLOAD_PATH) as f:
            PATH = f.read()
        print("[resuming wallpaper download]")
        print("[to stop downloading press Ctrl+z]")
        download_images(img_dl_links, PATH)
        print("wallpapers download complete")
    else:
        PATH = get_dl_path()
        with open(DOWNLOAD_PATH, "w") as f:
            f.write(PATH)
        img_dl_links = get_all_image_links()
        pickle.dump(img_dl_links, open(CONFIG_FILE, "wb"))
        print("[to stop downloading press Ctrl+z]")
        download_images(img_dl_links, PATH)
        print("wallpapers download complete")


if __name__ == "__main__":
    main()
