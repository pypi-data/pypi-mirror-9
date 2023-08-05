try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
      name='cfscrapefork',
      version='1.0.3',
      author='Steven Veshkini',
      author_email='sveshkini@berkeley.edu',
      packages=['cfscrape'],
      url='https://github.com/StevenVeshkini/cloudflare-scrape',
      description='cfscrapefork',
      install_requires=[
            "PyExecJS >= 1.1.0",
            ],
      )
