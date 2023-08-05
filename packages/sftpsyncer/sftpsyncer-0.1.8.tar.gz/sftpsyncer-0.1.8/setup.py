from setuptools import setup

setup(
    name='sftpsyncer',
    version='0.1.8',
    author='Chris Horsley',
    author_email='chris.horsley@csirtfoundry.com',
    packages=['sftpsyncer', 'sftpsyncer.test'],
    scripts=[],
    url='http://bitbucket.org/dsms/sftpsyncher/',
    license='LICENSE.txt',
    description='Synchronise files between a local cache and an SFTP server',
    long_description=open('README').read(),
    install_requires=[
        "paramiko"
    ],
)
