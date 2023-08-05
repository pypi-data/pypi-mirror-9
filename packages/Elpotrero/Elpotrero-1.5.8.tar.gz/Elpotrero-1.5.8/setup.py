from distutils.core import setup

setup(
    name='Elpotrero',
    version='1.5.8',
    author='Ronny Abraham',
    author_email='this.ronny@gmail.com',
    packages=['elpotrero', 'elpotrero.lib', ],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='libraries for installing a basic django frame',
    long_description=open('README.txt').read(),
)
