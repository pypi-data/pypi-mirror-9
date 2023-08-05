from distutils.core import setup
from distutils.command.install import install


class test(install):
    def run(self):
        print("HELLO!!!!!!!!!!!!!!!!!!!!")
        install.run(self)

setup(
    name='libK',
    version='0.0.35',
    packages=['libK'],
    url='https://bitbucket.org/Negash/libk',
    license='',
    author='Negash',
    author_email='i@negash.ru',
    description='Lib for fast coding',
    cmdclass={'install': test}
)