import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
setup(
    name = "ErepMessenger",
    version = "0.9.4.3",
    scripts = ['ez_setup.py','install.bat'],
    packages = ['erepmessenger'],
    package_data = {'erepmessenger': ['messenger.pyw','config.cfg','messenger.gif','messenger.ico']},
    
    install_requires = ['requests>=2.2.1', 'beautifulsoup4>=4.3.2'],
    author = "Mike Ontry",
    author_email = "mr.ontry@gmail.com",
    description = "App to send mass in game messages for Erepublik",
    license = "PSF",
    long_description=open('README.rst').read(),
    keywords = "erepublik mass messaging",
    url = "https://pypi.python.org/pypi/ErepMessenger"    
)
