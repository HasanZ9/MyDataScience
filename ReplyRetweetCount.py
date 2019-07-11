from urllib.request import urlopen
from bs4 import BeautifulSoup

file1="replies2bbc.csv"
file = "5_twitterKhaadi.csv"
f = open(file, "w")
f1 = open(file1, "w")
Headers = "tweet_user, tweet_text,  replies,  retweets\n"
f.write(Headers)
for page in range(0,5):
    url = "https://twitter.com/KhaadiOfficial".format(page)
    html = urlopen(url)
    soup = BeautifulSoup(html,"html.parser")
    tweets = soup.find_all("li", attrs={"class":"js-stream-item"})
    for tweet in tweets:
        try:
            if tweet.find('p',{"class":'tweet-text'}):
             tweet_user = tweet.find('span',{"class":'username'}).text.strip()
             tweet_text = tweet.find('p',{"class":'tweet-text'}).text.encode('utf8').strip()
             replies = tweet.find('span',{"class":"ProfileTweet-actionCount"}).text.strip()
             retweets = tweet.find('span', {"class" : "ProfileTweet-action--retweet"}).text.strip()
             print(tweet_user, tweet_text,  replies,  retweets)
             f.write("{}".format(tweet_user).replace(",","|")+ ",{}".format(tweet_text)+ ",{}".format( replies).replace(",", " ")+ ",{}".format(retweets) +  "\n")
        except: AttributeError
f.close()
