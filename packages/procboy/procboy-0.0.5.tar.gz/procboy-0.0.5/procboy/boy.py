#!/usr/bin/env python
import os, sys
import shlex
from collections import OrderedDict
from pprint import pprint as pp
import re
import argparse
import signal
import functools
import datetime
import subprocess
import platform
import six

if platform.python_version()[0]=='2':
    import trollius as asyncio
else:
    import asyncio

class ConfigParser(object):
    def __init__(self, filename=None):
        filename = filename or self.DEFAULT_FILE
        if os.path.isfile(filename):
            with open(filename) as f:
                self.read(f.read().strip())
        else:
            print("File ({0}) not found, ignored.".format(filename))

    def read(self, contents):
        self.commands = OrderedDict()
        for line in contents.splitlines():
            m = self.LINE.match(line)
            if m:
                cmd = os.path.expandvars(m.group(2))
                self.commands[m.group(1)] = shlex.split(cmd)

class Procfile(ConfigParser):
    DEFAULT_FILE = './Procfile'
    LINE = re.compile(r'^(\w.+?):\s*(.+)$')

class Inifile(ConfigParser):
    DEFAULT_FILE = './.env'
    LINE = re.compile(r'^(\w.+?)=\s*(.+)$')

BGCOLORS = OrderedDict(
    green='\033[32m',
    yellow='\033[33m',
    blue='\033[34m',
    magenta='\033[35m',
    cyan='\033[36m',
    bold_green='\033[1;32m',
    bold_yellow='\033[1;33m',
    bold_blue='\033[1;34m',
    bold_magenta='\033[1;35m',
    bold_cyan='\033[1;36m',
)

class PsParser:
    """ parse ps output """
    def __init__(self, command="ps -Al"):
        output = subprocess.check_output(command, shell=True)
        self.result = {}
        self.headers = OrderedDict()
        processes = output.splitlines()
        nfields = len(processes[0].split()) - 1
        self.lines = []
        for k, row in enumerate(processes):
            row = row.decode('utf-8')
            data = row.split(None, nfields)
            if k==0:
                self.headers = data
                for k,header in enumerate(data):
                    self.result[header] = []
                continue
            self.lines.append(data)
            for k,value in enumerate(data):
                self.result[self.headers[k]].append(value)
    def get_pid(self, pid):
        result = [Proc(k, self) for k in self.lines if int(k[self.headers.index('PID')])==pid]
        return result[0] if result else None

class Proc:
    def __init__(self, line, psp=[]):
        self.line = line
        self.psp = psp
        self.pid = int(self.line[self.psp.headers.index('PID')])
    def children(self):
        return [Proc(line, self.psp) for line in self.psp.lines if int(line[self.psp.headers.index('PPID')])==self.pid]
    def child_pids(self):
        return [k.pid for k in self.children()]

def get_meta(extra):
    class ClassMeta(type):
        def __new__(cls, name, bases, attrs):
            instance = super(ClassMeta, cls).__new__(cls, name, bases, attrs)
            instance.extra = extra
            return instance
    return ClassMeta


PIDS = []# added from Subprocess (better way?); @TODO {Procfile-name: PID}
def get_protocol(name):
    class Subprocess(asyncio.SubprocessProtocol, six.with_metaclass(get_meta(name))):
        """ fd: 0 IN, 1 OUT, 2 ERR """
        def __init__(self, *args, **kwargs):
            self.fm_name = self.extra.get('name')
            self.fm_color = self.extra.get('color')
            self.name_prefix = self.fm_name[:19].ljust(self.extra.get('max_name_len'))

        def connection_made(self, transport):
            self.transport = transport
            PIDS.append(self.transport.get_pid())

        def connection_lost(self, exc):
            asyncio.get_event_loop().stop()

        def pipe_data_received(self, fd, data):
            lines = data.decode('utf-8').split("\n")
            for line in lines:
                msg = line.rstrip("\n")
                if msg:
                    self.logline(msg)

        def logline(self, msg):
            timenow = datetime.datetime.now().strftime('%H:%m:%S')
            prefix = self.fm_color+"{0} {1} |\033[0m ".format(timenow, self.name_prefix)
            print('{0}{1}'.format(prefix, msg))

    return Subprocess

def ask_exit(signame):
    print("Got signal {0}: exit".format(signame))
    asyncio.get_event_loop().stop()

AVAILABLE_COLORS = list(BGCOLORS.keys())
def get_random_color():
    return BGCOLORS[AVAILABLE_COLORS.pop() or BGCOLORS['green']]
