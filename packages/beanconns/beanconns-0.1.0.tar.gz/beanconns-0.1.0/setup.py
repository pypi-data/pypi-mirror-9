#coding=utf-8
from distutils.core import setup

setup(
      name='beanconns',
      version='0.1.0',
      py_modules=['connections'],
      author='ldd',
      author_email='dongdongl@oupeng.com',
      license='LGPL',
      install_requires=["gevent>=0.1.0"],
      description="Connections Pool for beanstalk",
      keywords ='beanstalk connections pool',
      url='http://oupeng.com/'
)
