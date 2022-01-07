#!/usr/bin/env python3

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
import sys
import os

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='robot_hat',


    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version="1.0.1",

    description='Library for SunFounder Robot Hat',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/sunfounder/robot-hat',

    # Author details
    author='SunFounder',
    author_email='service@sunfounder.com',

    # Choose your license
    license='GNU',
    zip_safe=False,
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
    ],

    # What does your project relate to?
    keywords='python raspberry pi GPIO sunfounder',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['tests', 'docs']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['RPi.GPIO', 'spidev', 'pyserial' ],
    
    
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'robot_hat=robot_hat:__main__',
        ],
    },
)

class Config(object):
    ''' 
        To setup /boot/config.txt
    '''

    def __init__(self, file="/boot/config.txt"):
        self.file = file
        with open(self.file, 'r') as f:
            self.configs = f.read()
        self.configs = self.configs.split('\n')

    def remove(self, expected):
        for config in self.configs:
            if expected in config:
                self.configs.remove(config)
        return self.write_file()

    def set(self, name, value=None):
        have_excepted = False
        for i in range(len(self.configs)):
            config = self.configs[i]
            if name in config:
                have_excepted = True
                tmp = name
                if value != None:
                    tmp += '=' + value
                self.configs[i] = tmp
                break

        if not have_excepted:
            tmp = name
            if value != None:
                tmp += '=' + value
            self.configs.append(tmp)
        return self.write_file()

    def write_file(self):
        try:
            config = '\n'.join(self.configs)
            with open(self.file, 'w') as f:
                f.write(config)
            return 0, config
        except Exception as e:
            return -1, e

def run_command(cmd=""):
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    # print(result)
    # print(status)
    return status, result

errors = []
def do(msg="", cmd=""):
    # print(" - %s..." % (msg), end='\r')
    print(" - %s... " % (msg), end='', flush=True)
    status, result = eval(cmd)
    # print(status, result)
    if status == 0 or status == None or result == "":
        print('Done')
    else:
        print('Error')
        errors.append("%s error:\n  Status:%s\n  Error:%s" %
                      (msg, status, result))


APT_INSTALL_LIST = [
    "i2c-tools",
    "espeak",
    "wiringpi", 
    "python3-pyaudio",
    'libsdl2-dev',
    'libsdl2-mixer-dev',
]

PIP_INSTALL_LIST = [
    "gpiozero",
    'pillow',
    "pygame",
]

if sys.argv[1] == 'install':
    try:
    # Install dependency 
        print("Install dependency")
        do(msg="update apt",
            cmd='run_command("sudo apt update")')
        for dep in APT_INSTALL_LIST:
            do(msg="install %s"%dep,
                cmd='run_command("sudo apt install %s -y")'%dep)
        for dep in PIP_INSTALL_LIST:
            do(msg="install %s"%dep,
                cmd='run_command("sudo pip3 install %s")'%dep)
    # Setup interfaces
        print("Setup interfaces")
        do(msg="turn on I2C",
            cmd='Config().set("dtparam=i2c_arm", "on")')
        do(msg="turn on SPI",
            cmd='Config().set("dtparam=spi", "on")')
        do(msg="turn on Lirc",
            cmd='Config().set("dtoverlay=lirc-rpi:gpio_in_pin", "26")')
        do(msg="turn on Uart",
            cmd='Config().set("enable_uart", "1")')  

    # Report error
        if len(errors) == 0:
            print("Finished")
        else:
            print("\n\nError happened in install process:")
            for error in errors:
                print(error)
            print("Try to fix it yourself, or contact service@sunfounder.com with this message")
            sys.exit(1)

    except KeyboardInterrupt:
        print("Canceled.")
    except Exception as e:
        print(e)

