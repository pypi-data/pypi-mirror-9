from distutils.core import setup
setup(
  name = 'gardenkit',
  packages = ['gardenkit'], # this must be the same as the name above
  version = '1.3',
  description = 'GreenIQ Smart Garden Hub API',
  author = 'Golan Derazon',
  author_email = 'golan@greeniq.co',
  url = 'https://bitbucket.org/greeniqrd/gardenkit-python-sdk', # use the URL to the github repo
  download_url = 'https://bitbucket.org/greeniqrd/gardenkit-python-sdk', # I'll explain this in a second
  keywords = ['IoT', 'home', 'automation'], # arbitrary keywords
  classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Home Automation",
        ],
    long_description = \
    """
    GreenIQ revolutionise gardening with the Smart Garden Hub and cuts outdoor water consumption by 50%. 
    The GardenKit API is a REST API which gives the developer all the components that are required to build a full or partial app for the Smart Garden Hub. 
    When you use the GardenKit, you agree GreenIQ’s API License Agreement.
    
    Having questions? Email us to developers@greeniq.co    
    
    REST API documentation:
    http://greeniq.co/api.htm
    
    """
)
