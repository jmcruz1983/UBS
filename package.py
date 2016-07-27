"""
Module that generates, signs debug and zip aligns a specific android package
"""

import os
import logging
from utils import BuildSetup, execute_command, check_files, \
    get_files, find_file, check_if_new_or_modified_files

# Setting logger
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

fmt = logging.Formatter(datefmt="%H:%M:%S",
                        fmt='%(asctime)s %(levelname)-8s: %(name)s: %(message)s')
sh = logging.StreamHandler()
sh.setFormatter(fmt)
log.addHandler(sh)

class Package():
    """
    Class that generates, signs debug and zip aligns a specific android package
    """
    def __init__(self, *args, **kwargs):
        # Setup
        bs = BuildSetup()
        self.os_environ = bs.get_os_environ()
        self.author = bs.get_author()
        self.java_home = bs.get_java_home()
        self.android_home = bs.get_android_home()
        self.android_jar = bs.get_android_jar()
        self.aapt_bin = bs.get_aapt_bin()
        self.dx_bin = bs.get_dx_bin()
        self.zipalign_bin = bs.get_zipalign_bin()
        self.javac_bin = bs.get_javac_bin()
        self.jarsigner_bin = bs.get_jarsigner_bin()
        self.key_store = bs.get_key_store()
        self.key_pass = bs.get_key_pass()
        self.store_pass = bs.get_store_pass()
        self.key_alias = bs.get_key_alias()
        self.unsigned_prefix = bs.get_unsigned_prefix()
        self.signed_prefix = bs.get_signed_prefix()
        self.zipped_prefix = bs.get_zipped_prefix()

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

    def _check_files(self, dir, exts):
        return check_files(os.path.join(self.project_path,
                                        dir),
                           exts)
    def _get_files(self, dir, exts):
        return get_files(os.path.join(self.project_path,
                                        dir),
                         exts)

    def _find_file(self, dir=None, filename=None):
        return find_file(os.path.join(self.project_path,
                                      dir),
                          filename)

    def _check_dex(self):
        return len(self._find_file('bin','.dex')) > 0

    def _check_unsigned_apk(self):
        return len(self._find_file('bin','.%s.apk'%(self.unsigned_prefix))) > 0

    def _check_signed_apk(self):
        return len(self._find_file('bin','.%s.apk'%(self.signed_prefix))) > 0

    def _check_aligned_apk(self):
        return len(self._find_file('bin','.%s.apk'%(self.zipped_prefix))) > 0

    def _check_if_new_or_modified_files(self, dir=None, exts=None):
        return check_if_new_or_modified_files(self.meta_info_path,
                                              os.path.join(self.project_path,
                                                           dir),
                                              exts)

    def _need_to_re_create_unsigned_apk(self):
        return len(self._check_if_new_or_modified_dex()) > 0

    def _need_to_re_sign_apk(self):
        return len(self._check_if_new_or_modified_unsigned_apk()) > 0

    def _need_to_re_align_apk(self):
        return len(self._check_if_new_or_modified_signed_apk()) > 0

    def _check_if_new_or_modified_dex(self):
        return self._check_if_new_or_modified_files('bin', ['.dex'])

    def _check_if_new_or_modified_unsigned_apk(self):
        return self._check_if_new_or_modified_files('bin', ['.%s.apk'%(self.unsigned_prefix)])

    def _check_if_new_or_modified_signed_apk(self):
        return self._check_if_new_or_modified_files('bin', ['.%s.apk'%(self.signed_prefix)])


    def _create_unsigned_apk_PRE(self):
        if os.path.exists(self.project_path):
            if self._check_dex() and \
                    (True if self.aapt_bin else False) and \
                    (True if self.app_manifest else False) and \
                    (True if self.android_jar else False):

                log.info('Creating application package')
                if  self._need_to_re_create_unsigned_apk() or \
                    not self._check_unsigned_apk():
                    self._create_unsigned_apk_task()
                else:
                    log.info('No new/modified binary executable to re-created unsigned apk')
                    self._create_unsigned_apk_POST()
            else:
                log.warn('Missing binary executable and/or build tools!')
        else:
            log.warn('Project "%s" does not exist in workspace!'%(self.project_name))

    def _create_unsigned_apk_task(self):
        # Create unsigned APK
        cmd = [ self.aapt_bin,
                'package', '-f',
                '-M', '%s'%(self.app_manifest),
                '-I', '%s'%(self.android_jar),
                '-F', '%s/bin/%s.%s.apk'%(self.project_path,
                                          self.project_name,
                                          self.unsigned_prefix),
                '-S', '%s/res' % (self.project_path),
                '%s/bin'%(self.project_path)]

        if execute_command(cmd, cwd=self.project_path, os_env=self.os_environ):
            log.info('Created %s.%s.apk' % (self.project_name,
                                            self.unsigned_prefix))
        self._create_unsigned_apk_POST()

    def _create_unsigned_apk_POST(self):
        if self._check_unsigned_apk():
            self._sign_apk_PRE()
        else:
            log.warn('Failed on creating apk!')

    def _sign_apk_PRE(self):
        if self._check_unsigned_apk() and \
                (True if self.jarsigner_bin else False) and \
                (True if self.key_store else False) and \
                (os.path.exists(self.key_store)) and \
                (True if self.key_pass else False) and \
                (True if self.store_pass else False) and \
                (True if self.key_alias else False):

            log.info('Signing application package')
            if self._need_to_re_sign_apk() or \
                    not self._check_signed_apk():
                self._sign_apk_task()
            else:
                log.info('No new/modified unsigned apk to re-sign apk')
                self._sign_apk_POST()
        else:
            log.warn('Missing unsigned apk and/or signing tools!')

    def _sign_apk_task(self):
        # Sign the apk
        cmd = [ self.jarsigner_bin,
                '-keystore', self.key_store,
                '-storepass', self.store_pass,
                '-keypass', self.key_pass,
                '-signedjar', '%s/bin/%s.%s.apk'%(self.project_path,
                                                  self.project_name,
                                                  self.signed_prefix),
                '%s/bin/%s.%s.apk'%(self.project_path,
                                    self.project_name,
                                    self.unsigned_prefix),
                self.key_alias ]

        if execute_command(cmd, cwd=self.project_path, os_env=self.os_environ):
            log.info('Signed application "%s.%s.apk"' % (self.project_name,
                                                         self.signed_prefix))
        self._sign_apk_POST()

    def _sign_apk_POST(self):
        if self._check_signed_apk():
            self._zip_align_apk_PRE()
        else:
            log.warn('Failed on signing apk!')

    def _zip_align_apk_PRE(self):
        if self._check_signed_apk() and \
                (True if self.zipalign_bin else False):

            log.info('zip aligning application package')
            if self._need_to_re_align_apk() or \
                    not self._check_aligned_apk():
                self._zip_align_apk_task()
            else:
                log.info('No new/modified signed apk to re-align apk')
                self._zip_align_apk_POST()
        else:
            log.warn('Missing signed apk and/or zip aligning tools!')

    def _zip_align_apk_task(self):
        # Zip align the apk
        cmd = [ self.zipalign_bin,
                '-f', '4',
                '%s/bin/%s.%s.apk'%(self.project_path,
                                    self.project_name,
                                    self.signed_prefix),
                '%s/bin/%s.%s.apk'%(self.project_path,
                                    self.project_name,
                                    self.zipped_prefix)]
        if execute_command(cmd, cwd=self.project_path, os_env=self.os_environ):
            log.info('Zip aligned application "%s.%s.apk"'%(self.project_name,
                                                            self.zipped_prefix))
        self._zip_align_apk_POST()

    def _zip_align_apk_POST(self):
        if not self._check_aligned_apk():
            log.warn('Failed on zip aligning apk!')

    def package_project(self):
        self._create_unsigned_apk_PRE()

def package_project(*args, **kwargs):
    p = Package(*args, **kwargs)
    p.package_project()

if __name__ == '__main__':
    package_project(name='HelloWorld')