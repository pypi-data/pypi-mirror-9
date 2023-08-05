from distutils.core import setup

setup(
      name='cfscrapefork',
      version='1.0.0',
      author='Steven Veshkini',
      author_email='sveshkini@berkeley.edu',
      packages=['cfscrape'],
      url='http://pypi.python.org/pypi/cf-scrape-fork/',
      description='cfscrape',
      long_description=open('README.md').read(),
      install_requires=[
            "PyExecJS >= 1.1.0",
            ],
      )
