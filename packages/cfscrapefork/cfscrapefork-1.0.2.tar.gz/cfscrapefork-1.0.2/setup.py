try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
      name='cfscrapefork',
      version='1.0.2',
      author='Steven Veshkini',
      author_email='sveshkini@berkeley.edu',
      packages=['cfscrape'],
      url='http://pypi.python.org/pypi/cf-scrape-fork/',
      description='cfscrape',
      install_requires=[
            "PyExecJS >= 1.1.0",
            ],
      )
