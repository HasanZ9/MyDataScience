"""
Created on Mon Jul  2 00:58:13 2019

@author: hasan.zafar
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import requests
import sys
import json


def usage():
    msg = """
    Please use python script_name.py twitter_username to use the program
    """
    print(msg)
    sys.exit(1)


def get_tweet_text(tweet):
    tweet_text_box = tweet.find("p", {"class": "TweetTextSize TweetTextSize--normal js-tweet-text tweet-text"})
    images_in_tweet_tag = tweet_text_box.find_all("a", {"class": "twitter-timeline-link u-hidden"})
    tweet_text = tweet_text_box.text
    for image_in_tweet_tag in images_in_tweet_tag:
        tweet_text = tweet_text.replace(image_in_tweet_tag.text, '')

    return tweet_text

def get_this_page_tweets(soup):
    tweets_list = list()
    #tweets = soup.find_all("li", {"data-item-type": "tweet"})
    
    # Extracting all the <a> tags into a list.
    tags = soup.find_all("a",href=True)

    # Extracting URLs from the attribute href in the <a> tags.
    urls=list()
    for tag in tags:
        if 'status' in tag.get('href'):
            urls.append("https://twitter.com"+tag.get('href'))
    del urls[-1]
    print("working...")
    
    for tweeturl in urls:
        #opening connection and grabbing the page
        uClient = uReq(tweeturl)
        page_html = uClient.read()
        uClient.close()
        #html parsing
        page_soup = BeautifulSoup(page_html,"html.parser")

        #tweet data
        tweets = page_soup.find_all('li', 'js-stream-item')
        
        #grabs tweet replies
        #containers = page_soup.findAll("div",{"class":"js-tweet-text-container"})
        
        #Parent tweet
        parenttweet=page_soup.find("div",{"class":"permalink-tweet-container"})
        parent=parenttweet.div
        ptweet = {
                'id': parent['data-item-id'],
                'username': parent.find('span', 'username').text,
                'time': parent.find('a', 'tweet-timestamp')['title'],
                'no-of-replies': parent.find('span', 'ProfileTweet-actionCount').text.strip(),
                'tweet': parent.find('p', 'tweet-text').text, #.encode('utf-8')
                'likes': parent.find('span', 'ProfileTweet-action--favorite').text.strip(),
                'retweets': parent.find('span','ProfileTweet-action--retweet').text.strip()
                }
        tweets_list.append(ptweet)
        
        #sublist for replies
        replies=list()
        for container in tweets:
            if container.find('p', 'tweet-text'):
                tweetdata = {
                    'id': container['data-item-id'],
                    'username': container.find('span', 'username').text,
                    'time': container.find('a', 'tweet-timestamp')['title'],
                    'reply-tweet': container.find('p', 'tweet-text').text,#.encode('utf-8')
                    'likes': container.find('span', 'ProfileTweet-action--favorite').text.strip(),
                    'retweets': container.find('span','ProfileTweet-action--retweet').text.strip()
                    }
                replies.append(tweetdata)
        ptweet['replies']=replies
        #tweets_list.append(replies)
        #tweets_list.append('x x x x x x x x x x x x x x x x x x x x x x x x x x x')
        break
        """
        Likes = page_soup.findAll("div",{"class":"stream-item-footer"})
        like = Likes[0].find("span",{"class":"ProfileTweet-actionCount"})
        print("Tweet: ")
        #print(like)
        Counter = 0
        for container in containers:            
            Counter = Counter + 1
            print(Counter)
            replies = container.p.text
            tweets_list.append(replies)
            print(replies+"\n")
        """
    return tweets_list


def get_tweets_data(username, soup):
    tweets_list = list()
    tweets_list.extend(get_this_page_tweets(soup))

    next_pointer = soup.find("div", {"class": "stream-container"})["data-min-position"]

    while True:
        next_url = "https://twitter.com/i/profiles/show/" + username + \
                   "/timeline/tweets?include_available_features=1&" \
                   "include_entities=1&max_position=" + next_pointer + "&reset_error_state=false"

        next_response = None
        try:
            next_response = requests.get(next_url)
        except Exception as e:
            # in case there is some issue with request. None encountered so far.
            print(e)
            return tweets_list

        tweets_data = next_response.text
        tweets_obj = json.loads(tweets_data)
        if not tweets_obj["has_more_items"] and not tweets_obj["min_position"]:
            # using two checks here bcz in one case has_more_items was false but there were more items
            print("\nNo more tweets returned")
            break
        next_pointer = tweets_obj["min_position"]
        html = tweets_obj["items_html"]
        soup = BeautifulSoup(html, 'lxml')
        tweets_list.extend(get_this_page_tweets(soup))

    return tweets_list


# dump final result in a json file
def dump_data(username, tweets):
    filename = username+"_twitter.json"
    print("\nDumping data in file " + filename)
    data = dict()
    data["tweets"] = tweets
    with open(filename, 'w') as fh:
        fh.write(json.dumps(data))

    return filename


def get_username():
    # if username is not passed
    if len(sys.argv) < 2:
        usage()
    username = sys.argv[1].strip().lower()
    if not username:
        usage()

    return username


def start(username = None):
    username = get_username()
    url = "http://www.twitter.com/" + username
    print("\n\nFetching tweets for " + username)
    response = None
    try:
        response = requests.get(url)
    except Exception as e:
        print(repr(e))
        sys.exit(1)
    
    if response.status_code != 200:
        print("Non success status code returned "+str(response.status_code))
        sys.exit(1)

    soup = BeautifulSoup(response.text, 'lxml')

    if soup.find("div", {"class": "errorpage-topbar"}):
        print("\n\n Error: Invalid username.")
        sys.exit(1)

    tweets = get_tweets_data(username, soup)
    # dump data in a text file
    dump_data(username, tweets)
    print(str(len(tweets))+" tweets dumped.")


start()
