from setuptools import setup
from setuptools.command.install import install


class CustomInstallCommand(install):
    """Customized setuptools install command - prints a friendly greeting."""

    def run(self):
        print "Hello, developer, how are you? :)"


setup(
    name='libK',
    version='0.0.27',
    packages=['libK'],
    url='https://bitbucket.org/Negash/libk',
    license='',
    author='Negash',
    author_email='i@negash.ru',
    description='Lib for fast coding',
    install_requires=['pycurl', 'paramiko', 'pyquery', 'BeautifulSoup'],
    cmdclass={
        'install': CustomInstallCommand,
    }
)