from distutils.core import setup

with open('DESCRIPTION.rst') as f:
    long_des = f.read()

setup(
    name='servconn',
    version='1.3.0',
    author=u'Brandon Chinn',
    author_email='brandonchinn178@gmail.com',
    packages=['servconn'],
    url='http://github.com/brandonchinn178/servconn',
    description='Defines classes that wraps connections to servers',
    long_description=long_des,
    zip_safe=False
)