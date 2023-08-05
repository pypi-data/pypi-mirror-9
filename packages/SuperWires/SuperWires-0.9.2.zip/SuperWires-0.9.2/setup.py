from setuptools import setup, find_packages
import sys, os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='SuperWires',
	  version="0.9.2",
	  author = "Akif Patel",
	  author_email = "superwires@supernovaapps.com",
	  keywords="livewires python graphics pygame library",
	  url="http://www.supernovaapps.com/",
	  license="Apache 2.0",
	  description="Rewriting of the graphics library in 'Python for the Absolute Beginner' book.",
      packages=['superwires'],
      install_requires=["Pygame"],
      long_description=read('README'),
	  classifiers=[
			"Development Status :: 3 - Alpha",
			"License :: OSI Approved :: Apache Software License",
			"Programming Language :: Python",
			"Topic :: Multimedia :: Graphics"
	  ]
      )