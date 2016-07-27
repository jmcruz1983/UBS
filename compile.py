"""
Module that compiles a basic android project
"""

import os
import logging
from utils import BuildSetup, create_dir, create_file, \
    execute_command, check_files, get_files, find_file, \
    check_if_new_or_modified_files

# Setting logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

fmt = logging.Formatter(datefmt="%H:%M:%S",
                        fmt='%(asctime)s %(levelname)-8s: %(name)s: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(fmt)
log.addHandler(sh)


class Compile():
    """
    Class that parses and compiles resources, compiles sources and generates binary executable
    """
    def __init__(self, *args, **kwargs):
        # Setup
        bs = BuildSetup()
        self.os_environ = bs.get_os_environ()
        self.author = bs.get_author()
        self.java_home = bs.get_java_home()
        self.android_home = bs.get_android_home()
        self.aapt_bin = bs.get_aapt_bin()
        self.dx_bin = bs.get_dx_bin()
        self.javac_bin = bs.get_javac_bin()
        self.android_jar = bs.get_android_jar()
        # Local setup
        if not kwargs.has_key('name'):
            log.warn('No project name given!')
            return
        self.project_name = kwargs['name']
        self.project_path = os.path.join(bs.get_workspace_path(),
                                         self.project_name)
        self.package_name = 'com.%s.%s'%(self.author,
                                         self.project_name)
        self.app_manifest = os.path.join(self.project_path,
                                         'AndroidManifest.xml')
        self.meta_info_path = os.path.join(self.project_path,
                                           'meta.info')
        create_file(self.meta_info_path)

    def _check_files(self, dir=None, exts=None):
        return check_files(os.path.join(self.project_path,
                                        dir),
                           exts)
    def _get_files(self, dir=None, exts=None):
        return get_files(os.path.join(self.project_path,
                                      dir),
                         exts)

    def _find_file(self, dir=None, filename=None):
        return find_file(os.path.join(self.project_path,
                                      dir),
                          filename)

    def _check_resources(self):
        return self._check_files('res', ['.xml', '.png'])

    def _check_sources(self):
        return self._check_files('src', ['.java'])

    def _check_classes(self):
        return self._check_files('obj', ['.class'])

    def _get_sources(self):
        return self._get_files('src', ['.java'])

    def _get_classes(self):
        return self._get_files('obj', ['.class'])

    def _check_if_new_or_modified_files(self, dir=None, exts=None):
        return check_if_new_or_modified_files(self.meta_info_path,
                                              os.path.join(self.project_path ,dir),
                                              exts)

    def _check_if_new_or_modified_resources(self):
        return self._check_if_new_or_modified_files('res', ['.xml'])

    def _check_if_new_or_modified_sources(self):
        return self._check_if_new_or_modified_files('src', ['.java'])

    def _check_if_new_or_modified_classes(self):
        return self._check_if_new_or_modified_files('obj', ['.class'])

    def _need_to_re_create_R_java(self):
        return len(self._check_if_new_or_modified_resources()) > 0

    def _need_to_re_compile_java_sources(self):
        return len(self._check_if_new_or_modified_sources()) > 0

    def _need_to_re_compile_java_classes(self):
        return len(self._check_if_new_or_modified_classes()) > 0

    def _check_R_java(self):
        return len(self._find_file('src','R.java')) > 0

    def _get_R_java(self):
        return self._find_file('src','R.java')

    def _check_dex(self):
        return len(self._find_file('bin','.dex')) > 0

    def _create_R_java_PRE(self):
        if os.path.exists(self.project_path):
            if self._check_resources() and \
                    (True if self.aapt_bin else False) and \
                    (True if self.app_manifest else False) and \
                    (True if self.android_jar else False):

                log.info('Generating R.java')
                if  self._need_to_re_create_R_java() or \
                    not self._check_R_java():
                    self._create_R_java_task()
                else:
                    log.info('No new/modified resources to re-generate R.java')
                    self._create_R_java_POST()
            else:
                log.warn('Missing resources and/or build tools!')
        else:
            log.warn('Project "%s" does not exist in workspace!'%(self.project_name))

    def _create_R_java_task(self):
        # Generate R.java
        cmd = [self.aapt_bin,
                'package', '-f', '-m',
                '-S', '%s/res'%(self.project_path),
                '-M', '%s'%(self.app_manifest),
                '-I', '%s'%(self.android_jar),
                '-J', '%s/src'%(self.project_path)]
        if execute_command(cmd, cwd=self.project_path, os_env=self.os_environ):
            log.info('Generated R.java')
        self._create_R_java_POST()

    def _create_R_java_POST(self):
        if self._check_R_java():
            self._compile_java_code_PRE()
        else:
            log.warn('Failed on generating R.java!')

    def _compile_java_code_PRE(self):
        if self._check_sources() and \
                (True if self.javac_bin else False) and \
                (True if self.project_path else False) and \
                (True if self.android_jar else False):

            # Create obj folder if doesn't exist
            create_dir(os.path.join(self.project_path, 'obj'))

            log.info('Compiling java source')
            if  self._need_to_re_compile_java_sources() or \
                not self._check_classes():
                self._compile_java_code_task()
            else:
                log.info('No new/modified sources to re-compile sources')
                self._compile_java_code_POST()
        else:
            log.warn('Missing sources and/or build tools!')

    def _compile_java_code_task(self):
        # Compile java sources
        cmd = [self.javac_bin,
                '-d', '%s/obj'%(self.project_path),
                '-classpath', '%s'%(self.android_jar),
                '-sourcepath', '%s/src'%(self.project_path)]
        cmd.extend([_s for _s in self._get_sources()])

        if execute_command(cmd, cwd=self.project_path, os_env=self.os_environ):
            log.info('Compiled sources')
        self._compile_java_code_POST()

    def _compile_java_code_POST(self):
        if self._check_classes():
            self._create_dex_PRE()
        else:
            log.warn('Failed on compiling sources!')

    def _create_dex_PRE(self):
        if self._check_classes() and \
                (True if self.dx_bin else False) and \
                (True if self.project_path else False):

            # Create bin folder if doesn't exist
            create_dir(os.path.join(self.project_path, 'bin'))

            log.info('Generating DEX executable')
            if self._need_to_re_compile_java_classes() or \
                    not self._check_dex():
                self._create_dex_task()
            else:
                log.info('No new/modified classes to re-generate DEX executable')
                self._create_dex_POST()
        else:
            log.warn('Missing compiled classes and/or build tools!')

    def _create_dex_task(self):
        # Creates Dalvik executable
        cmd = [self.dx_bin, '--dex',
               '--output=%s/bin/classes.dex' % (self.project_path),
               '%s/obj'%(self.project_path),
               '%s/libs' % (self.project_path)]

        if execute_command(cmd, cwd=self.project_path, os_env=self.os_environ):
            log.info('Generated DEX executable')
        self._create_dex_POST()

    def _create_dex_POST(self):
        if not self._check_dex():
            log.warn('Failed on generating DEX binary excutable!')

    def compile_project(self):
        self._create_R_java_PRE()

def compile_project(*args, **kwargs):
    c = Compile(*args, **kwargs)
    c.compile_project()

if __name__ == '__main__':
    compile_project(name='HelloWorld')