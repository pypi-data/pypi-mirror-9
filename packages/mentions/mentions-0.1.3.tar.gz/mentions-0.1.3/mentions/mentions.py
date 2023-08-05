# -*- coding: utf-8 -*-

"""
This module contains the primary objects that power Mention.
"""

import json
import requests
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Karma v0.1.0', 'From': '@thinkxl'}

# Facebook
def get_facebook_data(method, url):
    try:
        facebook_url = 'https://api.facebook.com/method/fql.query?query=select \
                ' + method + ' from link_stat where url="' + url + '"&format=json'
        r = requests.get(facebook_url, headers=headers)
        json_data = json.loads(r.text)
        return json_data[0][method]
    except:
        return 0

def facebook_total_count(url):
    return get_facebook_data('total_count', url)

def facebook_like_count(url):
    return get_facebook_data('like_count', url)

def facebook_comment_count(url):
    return get_facebook_data('comment_count', url)

def facebook_share_count(url):
    return get_facebook_data('share_count', url)

# Twitter
def tweets(url):
    """tweets count"""
    try:
        twitter_url = 'http://urls.api.twitter.com/1/urls/count.json?url=' + url
        r = requests.get(twitter_url, headers=headers)
        json_data = json.loads(r.text)
        return json_data['count']
    except:
        return 0

# Google+
def google_plus_one(url):
    """+1's count"""
    try:
        google_url = 'https://plusone.google.com/_/+1/fastbutton?url=' + url
        soup = BeautifulSoup(requests.get(google_url, headers=headers).text)
        tag = soup.find_all(id="aggregateCount")[0]
        count = tag.string.extract()
        return count
    except:
        return 0

def linkedin_mentions(url):
    """mentions count"""
    try: 
        linkedin_url = 'http://www.linkedin.com/countserv/count/share?url=' \
                        + url + '&format=json'
        json_data = json.loads(requests.get(linkedin_url, headers=headers).text)
        return json_data['count']
    except:
        return 0

def pinterest_shares(url):
    """pinterest share count"""
    try:
        pinterest_url = 'http://api.pinterest.com/v1/urls/count.json?url=' \
                        + url
        response = requests.get(pinterest_url).text\
                   .replace('receiveCount(', '')\
                   .replace(')', '')
        json_data = json.loads(response)
        return json_data['count']
    except: 
        return 0

def stumbleupon_views(url):
    """views count"""
    try:
        stumbleupon_url = 'http://www.stumbleupon.com/services/1.01/badge.getinfo?\
                        url=' + url + '&format=jsonp'
        json_data = json.loads(requests.get(stumbleupon_url).text)
        return json_data['result']['views']
    except:
        return 0

# def delicious_count(url):
#     """bookmarked count"""
#     delicious_url = 'http://feeds.delicious.com/v2/json/urlinfo/data?url='\
#                     + url
#     return requests.get(delicious_url).response

def reddit_mentions(url):
    """mentions count"""
    try:
        reddit_url = 'http://www.reddit.com/api/info.json?url=' + url
        json_data = json.loads(requests.get(reddit_url, headers=headers).text)
        return len(json_data['data']['children'])
    except:
        return 0
