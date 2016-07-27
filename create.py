"""
Module that creates basic layout for an android project
"""

import os
import logging
from utils import BuildSetup, execute_command

# Setting logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

fmt = logging.Formatter(datefmt="%H:%M:%S",
                        fmt='%(asctime)s %(levelname)-8s: %(name)s: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(fmt)
log.addHandler(sh)

class Create():
    """
    Class that creates basic layout for an android project
    """
    def __init__(self, *args, **kwargs):
        # Build setup
        bs = BuildSetup()
        self.author = bs.get_author()
        self.android_bin = bs.get_android_bin()
        self.target = 'android-%s'%(bs.get_api_ver())
        self.activity_name = bs.get_activity_name()
        # Local setup
        if not kwargs.has_key('name'):
            log.warn('No project name given!')
            return
        self.project_name = kwargs['name']
        self.project_path = os.path.join(bs.get_workspace_path(),
                                         self.project_name)
        self.package_name = 'com.%s.%s'%(self.author,
                                         self.project_name)

    def isGood(self):
        return hasattr(self, 'project_name')

    def create_project_PRE(self):
        if self.isGood():
            log.info('Creating "%s" project'%(self.project_name))
            self.create_project_task()
        else:
            log.warn('Failed on creating the project, it is missing the project name!')
            self.create_project_POST()

    def create_project_task(self):
        # Create/update basic project
        cmd = [ self.android_bin,
                'update' if os.path.exists(self.project_path) else 'create', 'project',
                '--path', self.project_path ]
        if not os.path.exists(self.project_path):
            cmd.extend([
                '--name', self.project_name,
                '--activity',  self.activity_name,
                '--package', self.package_name,
                '--target', self.target
            ])
        if execute_command(cmd, cwd=self.project_path):
            if cmd[1] == 'update':
                log.info('Updating project "%s" ALREADY created in "%s"' % (self.project_name,
                                                                      self.project_path))
            else:
                log.info('Project "%s" is created in "%s"' % (self.project_name,
                                                              self.project_path))
        self.create_project_POST()

    def create_project_POST(self):
        pass

def create_project(*args, **kwargs):
    cp = Create(*args, **kwargs)
    cp.create_project_PRE()

if __name__ == '__main__':
    create_project(name='HelloWorld')