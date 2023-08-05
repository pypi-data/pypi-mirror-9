# -*- coding: utf-8 -*-

import os
import os.path as osp
import shutil
import tempfile
import itertools
from glob import glob
from atkit import exc
from atkit.config import config
from atkit.util import atprint
import sys
from functools import partial

class ModulePathManipulator(object):
    def symlink(self, src, dst):
        self.makedirs(osp.dirname(dst))
        self.remove_bytecode_files(dst)
        os.symlink(src, dst)  # TODO: calculate, make relative

    def remove(self, path):
        self.remove_bytecode_files(path)
        os.remove(path)

    def rename(self, src, dst):
        self.remove_bytecode_files(dst)
        os.rename(src, dst)

    def remove_bytecode_files(self, path):
        for bytecode_type in 'co':
            bytecode_file = path + bytecode_type
            if osp.exists(bytecode_file):
                os.unlink(bytecode_file)

    def rmdir(self, path):
        os.rmdir(path)

    def makedirs(self, path):
        if not osp.exists(path):
            os.makedirs(path)

    def copyfile(self, src, dst):
        if osp.isdir(dst):
            basename = osp.basename(src)
            dst = osp.join(dst, basename)
        dirname = osp.dirname(dst)
        self.makedirs(dirname)
        shutil.copyfile(src, dst)

    def prune_empty_dirs(self, path, remove_all_bytecode=True):
        while True:
            try:
                if remove_all_bytecode:
                    bytecode_files = []
                    bytecode_files.extend(glob(osp.join(path, '*.pyc')))
                    bytecode_files.extend(glob(osp.join(path, '*.pyo')))
                    for file in bytecode_files:
                        self.remove(file)
                self.rmdir(path)
                path = osp.dirname(path)
            except OSError:
                break
            if path.strip() == osp.sep.strip():  # paranoid: we break for sure when we reach root.
                break


class UserCustomizer(ModulePathManipulator):
    # TODO: check for enimies to usercustomize (see site.check_enableusersite and "no-global-site-packages.txt")

    def __init__(self):
        self.ucust_target_path = osp.join(config.lib_dir, 'usercustomize.py')
        self.atkit_ucust_module_path = osp.realpath(osp.join(osp.dirname(__file__), '_usercustomize.py'))
        self.backup_name = self.ucust_target_path + '.orig'

    @property
    def installed(self):
        return (osp.exists(self.ucust_target_path) and
                osp.realpath(self.ucust_target_path) == self.atkit_ucust_module_path)

    def uninstall(self):
        if not self.installed:
            raise exc.AtKitUnexpectedState('Not installed')
        self.remove(self.ucust_target_path)
        if osp.exists(self.backup_name):
            self.rename(self.backup_name, self.ucust_target_path)

    def install(self):

        if self.installed:
            return

        if not osp.exists(config.lib_dir):
            raise exc.PathError("%s: no such directory. Cannot proceed." % config.lib_dir)
        if osp.exists(self.ucust_target_path):
            if osp.exists(self.backup_name):
                raise exc.PathError("Backup exists. Cannot proceed: %s" % self.backup_name)
            self.rename(self.ucust_target_path, self.backup_name)

        self.symlink(self.atkit_ucust_module_path, self.ucust_target_path)


class SandboxedModule(ModulePathManipulator):

    def __init__(self, module_path):
        self.module_path = osp.abspath(module_path)
        self.module_backup_path = self.module_path + '.orig'
        if not osp.exists(self.module_path):
            raise exc.PathError('%s: no such file.')
        self.sandbox_path = osp.join(config.sandbox, self.module_path.lstrip(osp.sep))  # have to remove the leading slash from arg[1:]
        self.sandbox_path_saved_copy = self.sandbox_path + '.saved'
        self.sandboxed_notice_banner = '########  THIS IS A "SANDBOXED" MODULE  ########\n'

    def sandbox(self, add_notice_printer=True):
        if self.sandboxed:
            return
        cya_backup = osp.join(tempfile.gettempdir(), osp.basename(self.module_path))
        self.copyfile(self.module_path, cya_backup)
        try:
            self.copyfile(self.module_path, self.sandbox_path)
            if add_notice_printer:
                self.add_notice_printer(self.sandbox_path)
            self.rename(self.module_path, self.module_backup_path)
            self.symlink(self.sandbox_path, self.module_path)
        except Exception:
            self.rename(cya_backup, self.module_path)
        finally:
            self.remove(cya_backup)

    def unsandbox(self, save=False, prune_empty_dirs=True):
        if not self.sandboxed:
            raise exc.AtKitUnexpectedState('Not sandboxed.')
        self.remove(self.module_path)
        self.rename(self.module_backup_path, self.module_path)
        if save:
            if osp.exists(self.sandbox_path_saved_copy):
                raise exc.PathError('Already a saved copy of %s . What do?' % self.sandbox_path_saved_copy)
            self.copyfile(self.sandbox_path, self.sandbox_path_saved_copy)
        self.remove(self.sandbox_path)
        if prune_empty_dirs:
            self.prune_empty_dirs(path=osp.dirname(self.sandbox_path))

    @property
    def sandboxed(self):
        return (osp.exists(self.module_path) and
                osp.realpath(self.module_path) == self.sandbox_path)

    def add_notice_printer(self, path):
        statement = [
            self.sandboxed_notice_banner,  # this also serves as a "sentinal": banner present? ... yes/no
            '## This notice inserted by %s wich is/was defined in %s\n' % (self.__class__.__name__, osp.realpath(__file__)),
            'import sys\n',
            'import os\n',
            'mypath = os.path.realpath(__file__)\n',
            '''sys.stderr.write('NOTICE: Using a "sandboxed" module: %s\\n' % mypath)\n''',
            '################################################\n',
        ]
        new_sfile = []
        added = False
        with open(path, 'r') as orig_sfile:
            for line in orig_sfile:
                if line.strip().startswith(self.sandboxed_notice_banner.rstrip()):
                    return  # We're done
                if line and not added and not line.startswith('#'):
                    new_sfile.extend(statement)
                    added = True
                new_sfile.append(line)

        with open(path, 'w') as sfile:
            sfile.writelines(new_sfile)

    def edit(self, sandbox=True, path=None):
        if path is None:
            path = self.sandbox_path
        if sandbox:
            self.sandbox()
        for editor in os.getenv('VISUAL'), os.getenv('EDITOR'), 'vi':
            if editor is not None:
                os.system('%s %s' % (editor, path))
                break


class LogView(object):

    def __init__(self, path=None):
        if path is None:
            self.path = config.omnilog.log_path
        else:
            self.path = path
        self.cmds = [
            (('pager', 'less'), config.omnilog.pager),
            (('grep',), config.omnilog.grep),
            (('tail',), config.omnilog.tail),
            (('cat',), config.omnilog.cat),
            (('ls',), self.ls),
        ]
        for names, cmd in self.cmds:
            if callable(cmd):
                func = cmd
            else:
                func = partial(self._cmd, cmd)
            for name in names:
                setattr(self, name, func)

    def ls(self, args=None):
        atprint(self.path)

    def _cmd(self, cmd, args=''):
        os.system('%s %s %s' % (cmd, args, self.path))


def logview():
    try:
        action = sys.argv[1]
    except IndexError:
        action = 'pager'

    lfv = LogView()
    cmds = itertools.chain(*[n for n,v in lfv.cmds])
    if action not in cmds:
        atprint('Do not understand action "%s"' % action, fd=sys.stderr)
        sys.exit(1)
    getattr(lfv, action)(' '.join(sys.argv[2:]))

def activate():
    try:
        action = sys.argv[1]
    except IndexError:
        action = 'install'  # the script/func is called "activate" so default to "install"

    uc = UserCustomizer()
    if action == 'install':
        uc.install()
    elif action == 'uninstall':
        try:
            uc.uninstall()
        except exc.AtKitUnexpectedState:
            atprint('Not installed.')
            sys.exit(1)
    else:
        atprint('Do not understand action "%s"' % action, fd=sys.stderr)
        sys.exit(1)

def sandbox():
    try:
        action = sys.argv[2]
    except IndexError:
        action = 'sandbox'
        path = sys.argv[1]

    action, path = sys.argv[1:3]

    sbm = SandboxedModule(module_path=path)
    if action == 'sandbox':
        sbm.sandbox()
    elif action == 'unsandbox':
        try:
            sbm.unsandbox()
        except exc.AtKitUnexpectedState:
            atprint('Not sandboxed.')
            sys.exit(1)
    elif action == 'edit':
        sbm.edit()
    else:
        atprint('Do not understand action "%s"' % action, fd=sys.stderr)
        sys.exit(1)
