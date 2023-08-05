import apycotlib
import logging
import os
import subprocess
from glob import glob
from checkers.apycot import BaseChecker

class DebianLintianChecker(BaseChecker):
    """Runs the lintian program after building a debian package. Lintian
    checks for bugs and debian policy violations."""

    id = 'lintian'

    checked_extensions = ('.changes',)
    options_def = {
        'changes-files': {
            'type': 'csv',
            'required': False,
            'help': 'changes files to check',
        },
    }
    def get_output(self, path):
        cmd = subprocess.Popen(['lintian', '-I', '--suppress-tags',
                                'bad-distribution-in-changes-file', path],
                               stdout=subprocess.PIPE,
                               stdin=open('/dev/null'),
                               stderr=subprocess.STDOUT)
        for line in cmd.stdout:
            yield line
        cmd.wait()

    def do_check(self, test):
        status = apycotlib.SUCCESS
        changes_files = self.options.get('changes-files')
        if not changes_files:
            build_folder = os.path.join(test.project_path(), os.pardir)
            changes_files = glob(os.path.join(build_folder, '*', '*.changes'))
        if not changes_files:
            status = apycotlib.NODATA
        for f in changes_files:
            iter_line = self.get_output(f)
            for line in iter_line:
                line_parts = line.split(':', 1)
                try:
                    mtype, msg = line_parts
                except ValueError:
                    self.writer.fatal('unexpected line %r' % line, path=f)
                    for line in iter_line:
                        self.writer.info('followed by: %r' % line, path=f)
                    return apycotlib.ERROR
                else:
                    if mtype == 'I':
                        self.writer.info(msg, path=f)
                    elif mtype == 'W':
                        self.writer.warning(msg, path=f)
                    elif mtype == 'E':
                        self.writer.error(msg, path=f)
                        status = apycotlib.FAILURE
                    else:
                        self.writer.info(msg, path=f)
        return status

apycotlib.register('checker', DebianLintianChecker)

class DebianPiupartsChecker(BaseChecker):
    id = 'piuparts'

    checked_extensions = ('.changes',)
    options_def = {
        'changes-files': {
            'type': 'csv',
            'required': False,
            'help': 'changes files to check',
        },
        'extra-repos': {
            'type': 'csv',
            'required': False,
            'help': 'extra repos to add to sources.list',
        },
    }

    def __init__(self, *args, **kwargs):
        super(DebianPiupartsChecker, self).__init__(*args, **kwargs)
        self.basetgz = '/var/cache/lgp/buildd'
        lgp_config = subprocess.Popen(['lgp', 'setup', '--dump-config'],
                                      stdout=subprocess.PIPE)
        for line in lgp_config.stdout:
            if line.startswith('basetgz='):
                self.basetgz = line.split('=', 1)[1].strip()
                break
        if lgp_config.wait() != 0:
            self.writer.error('could not get lgp config')
        lgp_config.stdout.close()


    def get_output(self, path, dist, arch):
        basetgz = os.path.join(self.basetgz, '%s-%s.tgz' % (dist, arch))
        command = ['sudo', 'piuparts', '-b', basetgz, '-d', dist]
        for extra_repo in self.options.get('extra-repos'):
            command += ['--extra-repo', extra_repo.replace('@DIST@', dist)]
        command.append(path)
        cmd = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stdin=open('/dev/null'),
                               stderr=subprocess.STDOUT)
        output = []
        for line in cmd.stdout:
            if output and not line.startswith(' '):
                yield output
                output = []
            output.append(line)
        if output:
            yield output
        cmd.wait()

    def do_check(self, test):
        from debian.deb822 import Deb822

        status = apycotlib.SUCCESS
        changes_files = self.options.get('changes-files')
        if not changes_files:
            build_folder = os.path.join(test.project_path(), '..')
            changes_files = glob(os.path.join(build_folder, '*', '*.changes'))
        if not changes_files:
            status = apycotlib.NODATA
        for f in changes_files:
            with open(f) as changes:
                deb_desc = Deb822(changes)
                archs = set(deb_desc['Architecture'].split()) - set(('source',
                                                                     'any',
                                                                     'all'))
                distribution = deb_desc['Distribution'] #should be single
            for arch in archs or ('amd64',):
                iter_line = self.get_output(f, distribution, arch)
                for lines in iter_line:
                    msg = ''.join(lines)
                    try:
                        timestamp, mtype, _ = lines[0].split(None, 2)
                    except ValueError:
                        timestamp, mtype = lines[0].split(None, 2)
                    if mtype == 'DEBUG:' or mtype == 'DUMP:':
                        self.writer.debug(msg, path=f)
                    elif mtype == 'ERROR:':
                        self.writer.error(msg, path=f)
                        status = apycotlib.FAILURE
                    elif mtype == 'INFO:':
                        self.writer.info(msg, path=f)
                    else:
                        self.writer.fatal('unexpected line %r' % msg, path=f)
                        for lines in iter_line:
                            self.writer.info('followed by: %r' % ''.join(lines),
                                             path=f)
                        return apycotlib.ERROR
        return status

apycotlib.register('checker', DebianPiupartsChecker)


