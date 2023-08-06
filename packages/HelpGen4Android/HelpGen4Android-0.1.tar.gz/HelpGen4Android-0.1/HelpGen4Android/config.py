import ConfigParser

config = ConfigParser.SafeConfigParser()

config.add_section('s1')
config.set('s1', 'wikiTemplateURL',
'https://www.timecat.info/wiki/index.php/TimeCat:Doc:Help')
config.set('s1', 'outputDir', 'TimeCat')
#config.set('s1', 'outputDir', 'HelloWorld')
#config.set('s1', 'wikiTemplateURL','http://128.2.116.101/mediawiki/index.php/HelpGenWiki4android')
with open('config.cfg', 'wb') as configfile:
    config.write(configfile)
