# -*- coding: utf-8 -*-
#  Copyright 2013 Takeshi KOMIYA
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import re
import sys
import yaml
import signal
import socket
import pycassa
import tempfile
import subprocess
from glob import glob
from time import sleep
from shutil import copyfile, copytree, rmtree
from datetime import datetime

__all__ = ['Cassandra', 'skipIfNotInstalled', 'skipIfNotFound']

SEARCH_PATHS = ['/usr/local/cassandra', '/usr/local/apache-cassandra']
DEFAULT_SETTINGS = dict(auto_start=2,
                        base_dir=None,
                        cassandra_home=None,
                        pid=None,
                        copy_data_from=None)


class Cassandra(object):
    def __init__(self, **kwargs):
        self.settings = dict(DEFAULT_SETTINGS)
        self.settings.update(kwargs)
        self.pid = None
        self._owner_pid = os.getpid()
        self._use_tmpdir = False

        if self.base_dir:
            if self.base_dir[0] != '/':
                self.settings['base_dir'] = os.path.join(os.getcwd(), self.base_dir)
        else:
            self.settings['base_dir'] = tempfile.mkdtemp()
            self._use_tmpdir = True

        if self.cassandra_home is None:
            self.settings['cassandra_home'] = find_cassandra_home()

        self.settings.setdefault('cassandra_bin', os.path.join(self.cassandra_home, 'bin', 'cassandra'))

        user_config = self.settings.get('cassandra_yaml')
        with open(os.path.join(self.cassandra_home, 'conf', 'cassandra.yaml')) as fd:
            self.settings['cassandra_yaml'] = yaml.load(fd.read())
            self.settings['cassandra_yaml']['commitlog_directory'] = os.path.join(self.base_dir, 'commitlog')
            self.settings['cassandra_yaml']['data_file_directories'] = [os.path.join(self.base_dir, 'data')]
            self.settings['cassandra_yaml']['saved_caches_directory'] = os.path.join(self.base_dir, 'saved_caches')

            if user_config:
                for key, value in user_config.items():
                    self.settings['cassandra_yaml'][key] = value

        if self.auto_start:
            if os.path.exists(self.pid_file):
                raise RuntimeError('cassandra is already running (%s)' % self.pid_file)

            if self.auto_start >= 2:
                self.setup()

            self.start()

    def __del__(self):
        self.stop()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()

    def __getattr__(self, name):
        if name in self.settings:
            return self.settings[name]
        else:
            raise AttributeError("'Cassandra' object has no attribute '%s'" % name)

    @property
    def pid_file(self):
        return os.path.join(self.base_dir, 'tmp', 'cassandra.pid')

    def server_list(self):
        hostname = '127.0.0.1:%d' % self.cassandra_yaml['rpc_port']
        return [hostname]

    def setup(self):
        # copy data files
        if self.copy_data_from:
            try:
                datadir = os.path.join(self.base_dir, 'data')
                copytree(self.copy_data_from, datadir)
            except Exception as exc:
                raise RuntimeError("could not copytree %s to %s: %r" %
                                   (self.copy_data_from, datadir, exc))

        # (re)create directory structure
        for subdir in ['conf', 'commitlog', 'data', 'saved_caches', 'tmp']:
            try:
                path = os.path.join(self.base_dir, subdir)
                os.makedirs(path)
            except:
                pass

        # conf directory
        orig_dir = os.path.join(self.cassandra_home, 'conf')
        conf_dir = os.path.join(self.base_dir, 'conf')
        for filename in os.listdir(os.path.join(orig_dir)):
            srcpath = os.path.join(orig_dir, filename)
            destpath = os.path.join(conf_dir, filename)
            if not os.path.exists(destpath):
                if filename == 'log4j-server.properties':
                    logpath = os.path.join(self.base_dir, 'tmp', 'system.log')
                    with open(srcpath) as src:
                        with open(destpath, 'w') as dest:
                            property = re.sub('log4j.appender.R.File=.*',
                                              'log4j.appender.R.File=%s' % logpath,
                                              src.read())
                            dest.write(property)
                elif os.path.isdir(srcpath):
                    copytree(srcpath, destpath)
                else:
                    copyfile(srcpath, destpath)

    def prestart(self):
        # assign ports to cassandra
        ports = self.get_unused_ports(5)
        jmx_port = ports.pop()
        config_keys = ['rpc_port', 'storage_port', 'ssl_storage_port', 'native_transport_port']
        for key in config_keys:
            if key in self.settings['cassandra_yaml']:
                self.settings['cassandra_yaml'][key] = ports.pop()

        # replace cassandra-env.sh
        with open(os.path.join(self.base_dir, 'conf', 'cassandra-env.sh'), 'rt+') as fd:
            script = re.sub('JMX_PORT="7199"', 'JMX_PORT="%d"' % jmx_port, fd.read())
            fd.seek(0)
            fd.write(script)

        # generate cassandra.yaml
        with open(os.path.join(self.base_dir, 'conf', 'cassandra.yaml'), 'wt') as fd:
            fd.write(yaml.dump(self.cassandra_yaml))

    def start(self):
        if self.pid:
            return  # already started

        self.prestart()

        logger = open(os.path.join(self.base_dir, 'tmp', 'cassandra.log'), 'wt')
        pid = os.fork()
        if pid == 0:
            os.dup2(logger.fileno(), sys.__stdout__.fileno())
            os.dup2(logger.fileno(), sys.__stderr__.fileno())

            try:
                with open(self.pid_file, 'wt') as fd:
                    fd.write(str(pid))

                os.environ['CASSANDRA_CONF'] = os.path.join(self.base_dir, 'conf')
                os.execl(self.cassandra_bin, self.cassandra_bin, '-f')
            except Exception as exc:
                raise RuntimeError('failed to launch cassandra: %r' % exc)
        else:
            logger.close()

            while True:
                try:
                    sock = socket.create_connection(('127.0.0.1', self.cassandra_yaml['rpc_port']), 1.0)
                    sock.shutdown(socket.SHUT_RDWR)
                    sock.close()
                    break
                except Exception:
                    pass

                if os.waitpid(pid, os.WNOHANG)[0] != 0:
                    raise RuntimeError("*** failed to launch cassandra ***\n" + self.read_log())

                sleep(1)

            self.pid = pid

            # create test keyspace
            conn = pycassa.system_manager.SystemManager(self.server_list()[0])
            try:
                conn.create_keyspace('test', pycassa.SIMPLE_STRATEGY, {'replication_factor': '1'})
            except pycassa.InvalidRequestException:
                pass
            conn.close()

    def stop(self, _signal=signal.SIGTERM):
        self.terminate(_signal)
        self.cleanup()

    def terminate(self, _signal=signal.SIGTERM):
        if self.pid is None:
            return  # not started

        if self._owner_pid != os.getpid():
            return  # could not stop in child process

        try:
            os.kill(self.pid, _signal)
            killed_at = datetime.now()
            while (os.waitpid(self.pid, os.WNOHANG)):
                if (datetime.now() - killed_at).seconds > 10.0:
                    os.kill(self.pid, signal.SIGKILL)
                    raise RuntimeError("*** failed to shutdown cassandra (timeout) ***\n" + self.read_log())

                sleep(0.1)
        except:
            pass

        self.pid = None

        try:
            os.unlink(self.pid_file)
        except:
            pass

    def cleanup(self):
        if self.pid is not None:
            return

        if self._use_tmpdir and os.path.exists(self.base_dir):
            rmtree(self.base_dir, ignore_errors=True)

    def read_log(self):
        try:
            with open(os.path.join(self.base_dir, 'tmp', 'cassandra.log')) as log:
                return log.read()
        except Exception as exc:
            raise RuntimeError("failed to open file:tmp/cassandra.log: %r" % exc)

    def get_unused_ports(self, count=1):
        ports = []
        sockets = []
        for _ in range(count):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('127.0.0.1', 0))
            _, port = sock.getsockname()

            ports.append(port)
            sockets.append(sock)

        for sock in sockets:
            sock.close()

        return ports


def skipIfNotInstalled(arg=None):
    if sys.version_info < (2, 7):
        from unittest2 import skipIf
    else:
        from unittest import skipIf

    def decorator(fn, path=arg):
        if path:
            cond = not os.path.exists(path)
        else:
            try:
                find_cassandra_home()  # raise exception if not found
                cond = False
            except:
                cond = True  # not found

        return skipIf(cond, "Cassandra not found")(fn)

    if callable(arg):  # execute as simple decorator
        return decorator(arg, None)
    else:  # execute with path argument
        return decorator


skipIfNotFound = skipIfNotInstalled


def find_cassandra_home():
    for dir in SEARCH_PATHS:
        if os.path.exists(os.path.join(dir, 'bin', 'cassandra')):
            return dir

    def strip_version(dir):
        m = re.search('(\d+)\.(\d+)\.(\d+)', dir)
        if m is None:
            return None
        else:
            return [int(ver) for ver in m.groups()]

    # search newest cassandra-x.x.x directory
    cassandra_dirs = [dir for dir in glob("/usr/local/*cassandra*") if os.path.isdir(dir)]
    if cassandra_dirs:
        return sorted(cassandra_dirs, key=strip_version)[-1]

    raise RuntimeError("could not find CASSANDRA_HOME")


def get_path_of(name):
    path = subprocess.Popen(['/usr/bin/which', name],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE).communicate()[0]
    if path:
        return path.rstrip().decode('utf-8')
    else:
        return None
