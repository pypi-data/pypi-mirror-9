#from distutils.core import setup
from setuptools import setup

with open('README.rst', 'r') as fh:  txt = fh.read()
with open('LICENSE.txt', 'r') as fh:  lic = fh.read()
script = "s = '''\n" + txt + '\n' + lic + "\n'''\n\ndef readme(): return s"
with open('tbgxmlutils/readme.py', 'w') as fh: fh.write(script)

setup(
  name='TBGXMLUtils',
  install_requires=['lxml>=3.4.0', 'xmltodict>=0.9.0'],
  version='0.1.3',
  author='Marc Schwarzschild',
  author_email='ms@TheBrookhavenGroup.com',
  url='http://github.com/Schwarzschild/TBGXMLUtils',
  license='MIT',
  description='Easy XML utility.',
  keywords=['xml'],
  packages=['tbgxmlutils',],
)
