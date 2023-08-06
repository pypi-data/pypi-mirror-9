from  urllib import urlretrieve

#download the image with specified url
def imageDownload(outputDir,page_url,filename):
    urlretrieve(page_url,outputDir+"/images/"+filename)

def pageDownload(outputDir, url, soup):
    name = url.split("/")[-1].split("?")[0]	              
    with open(outputDir+'/'+name.replace(':','_')+'.html','w') as out_file:
        out_file.write(soup.prettify(encoding="utf8"));



