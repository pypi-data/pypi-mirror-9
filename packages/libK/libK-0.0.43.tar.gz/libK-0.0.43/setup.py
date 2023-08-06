from distutils.core import setup

setup(
    name='libK',
    version='0.0.43',
    packages=['libK'],
    url='https://bitbucket.org/Negash/libk',
    license='',
    author='Negash',
    author_email='i@negash.ru',
    description='Lib for fast coding',
    requires=['pycurl', 'paramiko', 'pyquery', 'BeautifulSoup']
)