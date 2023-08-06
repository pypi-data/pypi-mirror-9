from bs4 import BeautifulSoup, SoupStrainer, Tag
from downloadUtils import imageDownload

def parseImage(outputDir, server,soup):
    #Take care of the images inside each page:
    imgs = soup.find_all('a',{'class':'image'})
    for im in imgs:
        filename = im.img['src'].split("/")[-1]
	imageDownload(outputDir,server+im.img['src'],filename)
 	#modify the reference to the image
        new_tag =soup.new_tag( 'img', src="images/"+filename)
	soup.find('a',{'href':im['href']}).replaceWith(new_tag) 
    return soup

def parsePage(server,soup):
     #Take care of the links inside each page  
    ilinks = soup.find_all('a');
    for ilink in ilinks:
        #find out the static file name
        filename = ilink['href'].split("/")[-1] 
        if filename != '' and ilink['href'].startswith(server):
        #modify name to fix a mediawiki bug
            if ilink.has_key('class') and 'new' in ilink['class']: 
		#disable signature and file downloading on wiki
 		ilink.name = 'b'
                del ilink['href']
		del ilink['class']
	    else:
                filename = filename.replace(':','_')
	        ilink['href']=filename+".html"
	        del(ilink['title'])
    return soup
 
