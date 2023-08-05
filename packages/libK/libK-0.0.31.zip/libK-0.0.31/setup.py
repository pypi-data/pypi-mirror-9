from distutils.core import setup, Command
from time import sleep


class CleanCommand(Command):

    def run(self):
        print("HELLO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sleep(2)


setup(
    name='libK',
    version='0.0.31',
    packages=['libK'],
    url='https://bitbucket.org/Negash/libk',
    license='',
    author='Negash',
    author_email='i@negash.ru',
    description='Lib for fast coding',
    cmdclass={
        'clean': CleanCommand
    }
)