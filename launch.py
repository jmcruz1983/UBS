"""
Module that launches a specific android application on the active simulator
"""

import os
import logging
from utils import BuildSetup, execute_command, find_file, get_num_of_running_procs

# Setting logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

fmt = logging.Formatter(datefmt="%H:%M:%S",
                        fmt='%(asctime)s %(levelname)-8s: %(name)s: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(fmt)
log.addHandler(sh)

class Launch():
    """
    Class that launches a specific android application on the active simulator
    """
    def __init__(self, *args, **kwargs):
        # Setup
        bs = BuildSetup()
        self.os_environ = bs.get_os_environ()
        self.author = bs.get_author()
        self.adb_bin = bs.get_adb_bin()
        self.zipped_prefix = bs.get_zipped_prefix()
        self.emu_proc_name  = bs.get_emu_proc_name()
        self.activity_name = bs.get_activity_name()
        # Local setup
        if not kwargs.has_key('name'):
            log.warn('No project name given!')
            return
        self.project_name = kwargs['name']
        self.project_path = os.path.join(bs.get_workspace_path(),
                                         self.project_name)
        self.package_name = 'com.%s.%s' % (self.author,
                                           self.project_name)
        self.app_activity = '%s/.%s'%(self.package_name,
                                      self.activity_name)

    def _find_file(self, dir=None, filename=None):
        return find_file(os.path.join(self.project_path,
                                      dir),
                          filename)

    def _check_if_emulator_is_running(self):
        return get_num_of_running_procs(self.emu_proc_name) > 0

    def _check_aligned_apk(self):
        return len(self._find_file('bin','.%s.apk'%(self.zipped_prefix))) > 0

    def _get_aligned_apk(self):
        apks = self._find_file('bin','.%s.apk'%(self.zipped_prefix))
        if len(apks) > 0:
            return apks.pop()
        return None

    def _install_app_PRE(self):
        if os.path.exists(self.project_path):
            if self._check_if_emulator_is_running():
                if self._check_aligned_apk() and \
                        (True if self.adb_bin else False):
                    log.info('Installing application into the emulator')
                    self._install_app_task()
                else:
                    log.warn('Not apk and/or adb tool found!')
            else:
                log.warn('Emulator is not running! Please r e-run setup.sh script')
        else:
            log.warn('Project "%s" does not exist in workspace!' % (self.project_name))

    def _install_app_task(self):
        # Install the application into emulator
        cmd = [ self.adb_bin, '-e', 'install', '-r', self._get_aligned_apk() ]
        if execute_command(cmd, cwd=self.project_path, os_env=self.os_environ):
            log.info('Installed application "%s.%s.apk" to emulator'%(self.project_name,
                                                                      self.zipped_prefix))
        self._install_app_POST()

    def _install_app_POST(self):
        self._launch_app_PRE()

    def _launch_app_PRE(self):
        if  (True if self.adb_bin else False) and \
            (True if self.app_activity else False) and \
            (True if self.activity_name else False):
            log.info('Launching the application in the emulator')
            self._launch_app_task()
        else:
            log.warn('Not activity name and/or adb tool found!')

    def _launch_app_task(self):
        # Launch the application into emulator
        cmd = [ self.adb_bin, 'shell',  'am',  'start',  '-n', self.app_activity ]
        if execute_command(cmd, cwd=self.project_path, os_env=self.os_environ):
            log.info('Launched the application in the emulator')
        self._launch_app_POST()

    def _launch_app_POST(self):
        pass

    def launch_project(self):
        self._install_app_PRE()

def launch_project(*args, **kwargs):
    l = Launch(*args, **kwargs)
    l.launch_project()

if __name__ == '__main__':
    launch_project(name='HelloWorld')