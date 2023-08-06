import ConfigParser
def configure(**args):
    config = ConfigParser.SafeConfigParser()

    config.add_section('s1')
    config.set('s1', 'wikiTemplateURL',args['url'])
    config.set('s1', 'outputDir', args['outputDir'])
    #config.set('s1', 'outputDir', 'HelloWorld')
    #config.set('s1', 'wikiTemplateURL','http://128.2.116.101/mediawiki/index.php/HelpGenWiki4android')
    with open('config.cfg', 'wb') as configfile:
        config.write(configfile)
if __name__== "__main__":
    configure(url='https://www.timecat.info/wiki/index.php/TimeCat:Doc:Help',
	      outputDir='Timecat')
