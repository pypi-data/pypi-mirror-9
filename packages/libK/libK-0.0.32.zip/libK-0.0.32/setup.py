from time import sleep
from distutils.core import setup
from distutils.command.install_data import install_data


class post_install(install_data):
    def run(self):
        # Call parent
        install_data.run(self)
        # Execute commands
        print "Running"
        sleep(2)


setup(
    name='libK',
    cmdclass={"install_data": post_install},
    version='0.0.32',
    packages=['libK'],
    url='https://bitbucket.org/Negash/libk',
    license='',
    author='Negash',
    author_email='i@negash.ru',
    description='Lib for fast coding'
)