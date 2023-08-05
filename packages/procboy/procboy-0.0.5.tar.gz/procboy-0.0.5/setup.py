from setuptools import setup, find_packages, Command
from setuptools.command.test import test
from setuptools.command.install import install

import os, sys, subprocess

class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        raise SystemExit(
            subprocess.call([sys.executable,
                             '-m',
                             'unittest',
                             'discover']))

class InstallCommand(install):
    def run(self):
        install.do_egg_install(self)

base_dir = os.path.dirname(os.path.abspath(__file__))

install_requires = ["six"]
if sys.version_info.major == 2:
    install_requires.append('trollius')

setup(
    name = "procboy",
    version = "0.0.5",
    description = "ProcBoy - Manage processes",
    url = "http://github.com/futurice/procboy",
    author = "Jussi Vaihia",
    author_email = "jussi.vaihia@futurice.com",
    packages = ["procboy"],
    include_package_data = True,
    keywords = 'process procboy processboy',
    license = 'BSD',
    install_requires = install_requires,
    entry_points={
        'console_scripts': [
            'procboy = procboy.utils.runner:main',
        ],
    },
    cmdclass = {
        'test': TestCommand,
        #'install': InstallCommand,
    },
)
