"""
Module that setups paths and environment variables
"""

import os
import time
import shutil
import hashlib
import logging
import subprocess
from props import loadProperties

DEBUG=False

# Setting logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

fmt = logging.Formatter(datefmt="%H:%M:%S",
                        fmt='%(asctime)s %(levelname)-8s: %(name)s: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(fmt)
log.addHandler(sh)

"""
Utils
"""

# get the number of running process for a given process name
def get_num_of_running_procs(proc_name=None):
    count = 0
    if proc_name:
        try:
            tmp = os.popen("ps -Af").read()
            count = tmp.count(proc_name)
        except Exception:
            pass
    return count

# Creates dir recursively
def create_dir(dirpath=None):
    if dirpath and not os.path.exists(dirpath):
        os.mkdir(dirpath)

# Creates empty file
def create_file(fpath=None):
    if  fpath and \
        os.path.exists(os.path.dirname(fpath)):
        if os.path.exists(fpath):
            return
        with open(fpath,'w') as f:
            pass

# Returns the hash from a absolute file path
def get_file_hash(fpath):
    if fpath and os.path.exists(fpath):
        hasher = hashlib.md5()
        with open(fpath, 'rb') as _f:
            buf = _f.read()
            hasher.update(buf)
        return hasher.hexdigest()

# Hashing based on tt of modified file
def get_file_hash2(fpath):
    if os.path.exists(fpath):
        return time.ctime(os.path.getmtime(fpath))
    return ''

def clean_up(dirpath=None):
    if dirpath and os.path.exists(dirpath):
        shutil.rmtree(dirpath)

def execute_command(command, cwd=None, os_env=None):
    if DEBUG:
        print " ".join(command)
    curdir = cwd if os.path.exists(cwd) else os.path.abspath(os.path.curdir)
    os_env = os_env if os_env else os.environ.copy()
    if DEBUG:
        log.debug('executing command=%s', command)
    cmd_run = subprocess.Popen(command,
                               cwd=curdir,
                               stdout=subprocess.PIPE,
                               env=os_env)
    while cmd_run.poll() is None:
        if DEBUG:
            if cmd_run.stdout:
                for line in cmd_run.stdout.readlines():
                    log.info('cmd: %s', line[:-1])
            if cmd_run.returncode:
                log.info("cmd returned: %d", cmd_run.returncode)
                if cmd_run.returncode != 0:
                   raise Exception("Executing command {} failed".format(command))
        else:
            pass
    return cmd_run.returncode == 0 if cmd_run.returncode else True

def get_files(dir, exts):
    list_fs = []
    if dir and exts:
        for root, directories, filenames in os.walk(dir):
            for filename in filenames:
                for ext in exts:
                    if filename.endswith(ext):
                        list_fs.append(os.path.join(root,
                                                    filename))
                        break
    return list_fs


def check_files(dir=None, exts=None):
    return True if len(get_files(dir, exts)) > 0 else False

def find_file(dir=None, filename=None):
    found_files = []
    f_name, f_ext = os.path.splitext(filename)
    for _f in get_files(dir, [f_ext]):
        if _f.endswith(filename):
            found_files.append(_f)
    return found_files

# check if there is new or modified files in the given folder
def check_if_new_or_modified_files(meta_info_path=None, dir=None, exts=None):
    new_or_modified_files = []
    if meta_info_path and dir and exts:
        list_files = get_files(dir, exts)
        meta_info = loadProperties(meta_info_path)
        for _fpath in list_files:
            _f_hash = get_file_hash2(_fpath)
            if (meta_info.has_key(_fpath) and meta_info[_fpath] != _f_hash) or \
                    not meta_info.has_key(_fpath):
                new_or_modified_files.append((_fpath,
                                              'A' if not meta_info.has_key(_fpath) else 'M'))
                # Update hash
                meta_info[_fpath] = _f_hash
        # save metadata to file
        with open(meta_info_path, 'w') as _fmi:
            meta_info.store(_fmi)
    print_new_modified_files(new_or_modified_files)
    return new_or_modified_files

def print_new_modified_files(new_or_modified_files):
    if len(new_or_modified_files) > 0:
        log.info('Following files are (A)dded or (M)odified:')
        for _f, _t in new_or_modified_files:
            log.info('\t%s\t%s' % (_t, _f.split('/')[-1]))

class BuildSetup():
    """
    Class that setups paths and environment variables
    """
    def __init__(self, *args, **kwargs):
        self.os_environ = os.environ.copy()
        self._prop_file = os.path.join(os.path.dirname(__file__),
                                       'setup.properties')
        self._props = {}
        self._read_props()

    def _run_setup(self):
        execute_command(['%s/setup.sh' % (os.path.dirname(__file__))],
                        cwd=os.path.dirname(__file__),
                        os_env=self.os_environ)

    def get_os_environ(self):
        return self.os_environ

    def _read_props(self):
        if not os.path.exists(self._prop_file):
            log.warn('Build setup file not found! Running setup.sh script first')
            self._run_setup()
        if os.path.exists(self._prop_file):
            self._props = loadProperties(self._prop_file)

    def save_key(self, key, value):
        if not self._props.has_key(key):
            self._props[key] = value
            with open(self._prop_file, 'w') as f:
                self._props.store(f)
            return True
        return False

    def _get_key(self, key=None):
        if key and \
        isinstance(key,basestring) and \
        self._props.has_key(key):
            return self._props[key]
        return None

    def get_author(self):
        return  self._get_key('author')

    def get_workspace_path(self):
        return  self._get_key('workspace_path')

    def get_android_bin(self):
        return  self._get_key('android_bin')

    def get_api_ver(self):
        return  self._get_key('api_ver')

    def get_java_home(self):
        if not self.os_environ.has_key('JAVA_HOME'):
            self.os_environ['JAVA_HOME'] = self._get_key('java_home')
            log.warn('JAVA_HOME is not defined! Using "%s"'%(self.os_environ['JAVA_HOME']))
        return self.os_environ['JAVA_HOME']

    def get_android_home(self):
        if not self.os_environ.has_key('ANDROID_HOME'):
            self.os_environ['ANDROID_HOME'] = self._get_key('android_home')
            log.warn('ANDROID_HOME is not defined! Using "%s"'%(self.os_environ['ANDROID_HOME']))
        return self.os_environ['ANDROID_HOME']

    def get_android_jar(self):
        return  self._get_key('android_jar')

    def get_aapt_bin(self):
        return  self._get_key('aapt_bin')

    def get_dx_bin(self):
        return  self._get_key('dx_bin')

    def get_adb_bin(self):
        return  self._get_key('adb_bin')

    def get_zipalign_bin(self):
        return  self._get_key('zipalign_bin')

    def get_javac_bin(self):
        return  self._get_key('javac_bin')

    def get_key_store(self):
        return self._get_key('key_store')

    def get_jarsigner_bin(self):
        return self._get_key('jarsigner_bin')

    def get_key_pass(self):
        return self._get_key('key_pass')

    def get_store_pass(self):
        return self._get_key('store_pass')

    def get_key_alias(self):
        return self._get_key('key_alias')

    def get_unsigned_prefix(self):
        return self._get_key('unsigned_prefix')

    def get_signed_prefix(self):
        return self._get_key('signed_prefix')

    def get_zipped_prefix(self):
        return self._get_key('zipped_prefix')

    def get_emulator_bin(self):
        return self._get_key('emulator_bin')

    def get_emu_name(self):
        return self._get_key('emu_name')

    def get_emu_proc_name(self):
        return self._get_key('emu_proc_name')

    def get_activity_name(self):
        return self._get_key('activity_name')

def setup():
    bs = BuildSetup()

if __name__ == '__main__':
    setup()