#!/usr/bin/env python3
"""Download/view all Instagram media from an account.

Displays:
    - ID with 'get_id' function
    - General Data with 'get_general_data' function
    - Username with 'get_username' function
    - Media with 'get_media' function
    - Photo URLs in an array with 'get_photo_urls' function
    - Downloads Photos into a specific directory with 'download_photos' function.

If this module is imported and the access_token hasn't been set, a browser window
will open and will request an access token from Instagram."""

import json
import os
import urllib.request
import webbrowser

__author__ = "Ali Raja"
__copyright__ = "Copyright 2013-2015, Ali Raja"
__credits__ = ["Ali Raja"]
__license__ = "GPL"
__version__ = "1.0"
__maintainer__ = "Ali Raja"
__email__ = "alir6716@gmail.com"
__status__ = "Production"

__all__ = [ # FUNCTIONS
            "get_id", "get_general_data", "get_username", "get_media",
            "get_photo_urls", "download_photos"]


protocol = "https"
host = "api.instagram.com"
base_path = "/v1"

client_id = "b1781d233c2b42a79bb3b80ab1feea78"
access_token = None


def get_access_token(client_id=client_id, redirect_uri="http://localhost"):
    """
    Opens a browser which grabs the access token off a person's account.
    You might have to log in and accept access for the app if permission hasn't already been granted.
    The access token should then be in the address bar.
    """
    webbrowser.open("https://instagram.com/oauth/authorize/?client_id=%s&redirect_uri=%s&response_type=token"
                    % (client_id, redirect_uri))
    return ("You might have to log in and accept access.",
            "After that, access token should be in the address bar.",
            "( %s/#access_token=[HERE] )" % redirect_uri,
            "Copy and paste the token and set it to the 'access_token' variable")


if access_token is None:
    get_access_token()
    exit(1)


def url(path):
    """
    Forms up the URL used to connect to Instagram and get data.
    The argument 'path' gets added onto the returned answer, along with the
    protocol, host, base path, and access token.
    """
    if path.find("?") != -1:
        pre = "&"
    else:
        pre = "?"
    return protocol +"://" +host +base_path +path +pre +"access_token=" +access_token


def get_id(user_name):
    """
    Gets Instagram ID of a specified user.
    """
    path = url("/users/search?q=%s" % user_name)
    insta_id = urllib.request.urlopen(path)
    insta_id = insta_id.read().decode("utf-8")
    insta_id = json.loads(insta_id)
    insta_id = insta_id["data"]
    insta_id = insta_id[0]
    insta_id = insta_id["id"]
    insta_id = int(insta_id)
    return insta_id


def get_general_data(insta_id):
    """
    Gets general information of a specified account.
    """
    insta_id = str(insta_id)
    path = url("/users/%s" % insta_id)
    data = urllib.request.urlopen(path)
    data = data.read().decode("utf-8")
    data = json.loads(data)
    data = data["data"]
    return data


def get_username(insta_id):
    """
    Gets username of a specific account.
    """
    insta_id = str(insta_id)
    username = get_general_data(insta_id)
    username = username["username"]
    return username


def get_media(insta_id, max_id=None):
    """
    Gets recent media from a specified Instagram ID.
    To get more info, get the ID of the oldest photo given, and set the max_id
    variable to that value.
    """
    insta_id = str(insta_id)
    path = url("/users/%s/media/recent/" % insta_id)
    if max_id != None:
        path = path +"&max_id=%s" % max_id
    res = urllib.request.urlopen(path)
    res = res.read().decode("utf-8")
    res = json.loads(res)
    return res


def get_photo_urls(insta_id):
    """
    Uses 'get_media' to get URLs of pictures from a specified account.
    """
    insta_id = str(insta_id)
    urls = []
    media_count = get_general_data(insta_id)
    media_count = media_count["counts"]
    media_count = media_count["media"]
    max_id = None
    while len(urls) < media_count:
        res = get_media(insta_id, max_id)
        for img in res["data"]:
            img = img["images"]
            img = img["standard_resolution"]
            img = img["url"]
            urls.append(img)
        max_id = res["data"][-1]["id"]
    return urls


def download_photos(insta_id, save_to=os.getcwd()):
    """
    Uses 'get_photo_urls' to save pictures from a specified account.
    Creates a folder with the account's username, and downloads photos into
    that folder, in order of time created (1 being the oldest)
    """
    insta_id = str(insta_id)
    os.chdir(save_to)
    username = get_general_data(insta_id)
    username = username["username"]
    if not os.path.isdir(username):
        os.mkdir(username)
    os.chdir(username)
    res = get_photo_urls(insta_id)
    count = get_general_data(insta_id)
    count = count["counts"]
    count = count["media"]
    for url in res:
        file_name = str(count) +".jpg"
        if not os.path.isfile(file_name):
            urllib.request.urlretrieve(url, file_name)
        count -= 1
    return len(res)