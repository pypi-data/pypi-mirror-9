from distutils.core import setup
setup(name='HelpGen4Android',
		version='0.3.3',
		url='https://github.com/Eagles2F/HelpGen4Android',
		author='Evan Lee',
		author_email='thueeliyifan@gmail.com',
		license = 'MIT',
		packages = ['HelpGen4Android'],
		desciption = 'A simple python tool for maintaining android app help files from mediawiki',
		classifiers = ['Development Status :: 3 - Alpha','Intended Audience :: Developers',
			'Topic :: Software Development :: Documentation', 'License :: OSI Approved :: MIT License',
			'Programming Language :: Python :: 2.7',],
		keywords = 'mobile app development',
		install_requires = ['bs4']
		)
