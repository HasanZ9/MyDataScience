import bs4
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup
import requests

url = "https://twitter.com/KhaadiOfficial"
 
# Getting the webpage, creating a Response object.
response = requests.get(url)
 
# Extracting the source code of the page.
data = response.text
 
# Passing the source code to BeautifulSoup to create a BeautifulSoup object for it.
soup = BeautifulSoup(data, 'lxml')
 
# Extracting all the <a> tags into a list.
tags = soup.find_all("a",href=True)
 
# Extracting URLs from the attribute href in the <a> tags.
urls=[]
for tag in tags:
    if 'status' in tag.get('href'):
        urls.append("https://twitter.com"+tag.get('href'))
        
for my_url in urls:
    #my_url='https://twitter.com/KhaadiOfficial/status/1141353656236892165'
    #opening connection and grabbing the page
    uClient = uReq(my_url)
    page_html = uClient.read()
    uClient.close()
    #html parsing
    page_soup = soup(page_html,"html.parser")

    #grabs tweet replies
    containers = page_soup.findAll("div",{"class":"js-tweet-text-container"})
    len(containers)

    filename = "tweetreplies.csv"
    f = open(filename, "w")

    header= "tweet_text\n"
    f.write(header)
    print("Tweet: ")
    for container in containers:
        replies = container.p.text
        print(replies+"\n")
        f.write(replies)
