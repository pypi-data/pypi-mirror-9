from setuptools import setup

setup(name='Titley',
      version='1.5',
      description='To download and find matching subtitle for a movie.',
      url='http://bitbucket.org/sras/titley',
      author='Sandeep.C.R',
      author_email='sandeepcr2@gmail.com',
      license='MIT',
      scripts=['bin/titley-get.py'],
      packages=['titley', 'titley/sources', 'titley/lib/Bot', 'titley/lib/UserAgent'],
      install_requires=[
          'requests',
          'beautifulsoup4',
          'html5lib',   
          'pysrt',
      ],
      zip_safe=False)
