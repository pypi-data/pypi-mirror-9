# Paramiko + gevent
# File: setup.py
# Desc: needed

from setuptools import setup


if __name__ == '__main__':
    setup(
        version='1.3',
        name='paramiko-gevent',
        description='A tiny wrapper around Paramiko\'s SSHClient to enable running commands in parallel with gevent. ',
        author='Nick @ Oxygem',
        author_email='nick@oxygem.com',
        url='http://github.com/Fizzadar/paramiko-gevent',
        py_modules=['paramiko_gevent'],
        install_requires=['paramiko', 'gevent']
    )
