# -*- coding: utf-8 -*-
"""
Created on Wed Jan 14 16:37:36 2015

@author: yifan
"""
from collections import Counter
from bs4 import BeautifulSoup,SoupStrainer,Tag
import httplib2
from urllib import urlopen
from urllib import urlretrieve
from downloadUtils import imageDownload, pageDownload
from parseUtils import parseImage, parsePage
import config
import shutil
import sys
import ConfigParser
import os

def configure():
    # get configuration
    config = ConfigParser.SafeConfigParser()
    config.read('config.cfg')
    
    outputDir = config.get('s1','outputDir')  
    URL = config.get('s1','wikitemplateurl')+"?action=render"
    server = URL.split("/")[0]+"//"+URL.split("/")[2]
    return outputDir,URL,server

def getInitialLinks(traversal_queue,  download_queue, URL):
    http = httplib2.Http()
    status,response = http.request(URL)

    #enque the link in the template page
    for link in BeautifulSoup(response, parseOnlyThese = SoupStrainer('a')):
        if link.has_attr('href') and link.has_attr('title'):
	    print link
            traversal_queue.append(link['href']+'?action=render')
    return traversal_queue, download_queue

def traverseLinkGraph(traversal_queue, download_queue, server):
    http = httplib2.Http()
    while  traversal_queue:
	link = traversal_queue.pop(0)
	#find internel links
	status, response = http.request(link)
        soup = BeautifulSoup(response)
	ilinks=soup.find_all('a')
	for ilink in ilinks:
            if ilink.has_attr('href'):
                render_ilink =ilink['href']+'?action=render'    
	        if ilink['href'].startswith(server) \
			and render_ilink not in traversal_queue\
			and render_ilink not in download_queue\
			and not (ilink.has_attr('class') and ilink['class']!='image' ):
	            traversal_queue.append(render_ilink)
        #enque link into download_queue
        download_queue.append(link)
    return download_queue

def download(download_queue, outputDir, server):
    http = httplib2.Http()
    while download_queue:
	link = download_queue.pop(0)
        status, response = http.request(link)
	soup = BeautifulSoup(response)
        #parse and download images
        soup = parseImage(outputDir, server, soup)
        #parse page
        soup = parsePage(server,soup)
        #download page
        pageDownload(outputDir, link, soup)

def helpGen():
    
    outputDir, URL, server = configure()
    
    #preparing output directory
    if not os.path.exists(outputDir):
        os.makedirs(outputDir)
    if not os.path.exists(outputDir+'/images/'):
        os.makedirs(outputDir+'/images/') 
    
    traversal_queue = []
    download_queue = []

    #get initial page set from wiki template
    traversal_queue, download_queue = getInitialLinks(traversal_queue, download_queue, URL) 
    
    #traverse the link graph
    download_queue = traverseLinkGraph(traversal_queue, download_queue, server)

    #download the link
    download(download_queue, outputDir, server)   
        
if __name__== "__main__":
    helpGen()
