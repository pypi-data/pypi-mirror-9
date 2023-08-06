from distutils.core import setup
import os

setup(
    name='cmdhist',
    version='0.2.0',
    author='Manish R Jain',
    author_email='manishrjain@gmail.com',
    scripts=['bin/cmdhist.py', 'bin/cmdhistd.py'],
    url='https://bitbucket.org/manishrjain/cmdhist',
    license='LICENSE.txt',
    description='Commandline history in the cloud',
    long_description=open('README.txt').read(),
    install_requires=[
        "argparse >= 1.2.1",
        "requests[secure] >= 2.2.1",
    ],
    data_files=[(os.path.expanduser("~") + "/cmdhist", ['config.txt'])],
)
