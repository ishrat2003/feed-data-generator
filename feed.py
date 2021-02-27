import traceback
import urllib3,  urllib
import xmltodict, json
from collections import OrderedDict
import sys, re
import os.path
from bs4 import BeautifulSoup
from datetime import date

dataPath = './data'
urls = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "http://feeds.bbci.co.uk/news/uk/rss.xml",
    "http://feeds.bbci.co.uk/news/business/rss.xml",
    "http://feeds.bbci.co.uk/news/politics/rss.xml",
    "http://feeds.bbci.co.uk/news/health/rss.xml",
    "http://feeds.bbci.co.uk/news/education/rss.xml",
    "http://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
    "http://feeds.bbci.co.uk/news/technology/rss.xml",
    "http://feeds.bbci.co.uk/news/entertainment_and_arts/rss.xml"
];
contentClass = "story-body__inner"
today = date.today();

def saveFile(content, filePath):
    file = open(filePath, "w")
    file.write(content)
    file.close()
    return

def saveJsonFile(content, filePath):
    with open(filePath, 'w') as f:
        json.dump(content, f)
    return

def getPageContent(link):
    fp = urllib.request.urlopen(link)
    mybytes = fp.read()
    page = mybytes.decode("utf8")
    fp.close()
    soup = BeautifulSoup(page, features="html.parser")
    divs = soup.findAll('div',attrs={"class":contentClass})
    text = '';
    for div in divs:
        for item in div.findChildren():
            if item.name in ['p', 'ul', 'li', 'ol']:
                text += str(item.text) + ' '
                
    return text

def getFileName(processedItem):
    name = processedItem['pubDate'][5:7] + processedItem['pubDate'][8:11] + processedItem['pubDate'][12:16] + processedItem['title'][0:30]
    name = re.sub(r'[^a-zA-Z0-9]+', '', name)
    return name

def getFeedName(url):
    name = url.replace('http://', '')
    name = name.replace('https://', '')
    name = re.sub(r'[^a-zA-Z0-9]+', '', name)
    name = today.strftime("%Y%m%d-") + name + '.json'
    return name

def saveContent(rssItem):
    processedItem = {}
    
    for key in rssItem.keys():
        if (key in ['title', 'description', 'link', 'pubDate']):
            processedItem[key] = rssItem[key]
            
    # processedItem['content'] = getPageContent(processedItem['link'], )
    filename = getFileName(processedItem);
    path = os.path.join(dataPath, 'content', filename + ".json") 
    saveJsonFile(processedItem, path)
    return

def getResponse(url):
    http = urllib3.PoolManager()
    return http.request('GET', url)

def saveXmlToItems(url):
    response = getResponse(url)
    try:
        data = xmltodict.parse(response.data)
        filePath = os.path.join(dataPath, 'rss', getFeedName(url)) 
        saveJsonFile(data['rss']['channel'], filePath)
        
        data = data['rss']['channel']['item']
        for item in data:
            saveContent(item)

    except:
        print("Failed to parse xml from response (%s)" % traceback.format_exc())
        
    return


if __name__ == "__main__":
    for url in urls:
        print('Processing ' + url)
        saveXmlToItems(url)

    print('Finishing')
