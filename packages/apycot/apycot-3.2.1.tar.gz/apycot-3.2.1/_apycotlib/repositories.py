"""Some standard sources repositories, + factory function

:organization: Logilab
:copyright: 2003-2010 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
:license: General Public License version 2 - http://www.gnu.org/licenses
"""
__docformat__ = "restructuredtext en"

from os import path as osp, environ
from time import localtime

from logilab.common.textutils import split_url_or_path

from apycotlib import register, get_registered, ConfigError


SUPPORTED_REPO_TYPES = ('mercurial', 'subversion')


def get_repository(attrs):
    """factory method: return a repository implementation according to
    <attrs> (a dictionary)
    """
    repo_type = attrs['repository']['type']
    assert repo_type in SUPPORTED_REPO_TYPES, repo_type
    return get_registered('repository', repo_type)(attrs)

class VersionedRepository:
    """base class for versionned repository"""

    id = None
    default_branch = None

    def __init__(self, attrs):
        try:
            self.repository = attrs.pop('repository')
        except KeyError, ex:
            raise ConfigError('Missing %s option: %s' % (ex, attrs))
        if not self.repository:
            raise ConfigError('Repository must be specified (%s)' % (attrs,))
        self.path = attrs.pop('path', '')
        branch = attrs.pop('branch', None)
        if branch is None:
            branch = self.default_branch
        self.branch = branch
        self.ref_repo = self._ref_repo()
        if not self.ref_repo:
            raise ConfigError('Missing information to checkout repository %s'
                              % self.repository)
        # absolute path where the project will be located in the test
        # environment
        self.co_path = osp.join(environ['APYCOT_ROOT'], self._co_path())

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                self.repository == other.repository and
                self.path == other.path and
                self.branch == other.branch)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        """get a string synthetizing the location"""
        myrepr = '%s:%s' % (self.id, self.repository['source_url'] or self.repository['path'])
        if self.path:
            myrepr += '/' + self.path
        if self.branch:
            myrepr += '@%s' % self.branch
        return myrepr

    def co_command(self, quiet=True):
        """return a command that may be given to os.system to check out a given
        package
        """
        raise NotImplementedError()

    def co_move_to_branch_command(self, quiet=True):
        return None

    def normalize_date(self, from_date, to_date):
        """get dates as float or local time and return the normalized dates as
        local time tuple to fetch log information from <from_date> to <to_date>
        included
        """
        if isinstance(from_date, float):
            from_date = localtime(from_date)
        if isinstance(to_date, float):
            to_date = localtime(to_date)
        return (from_date, to_date)

    def changeset(self):
        """return changeset of the working directory"""
        return None

    def revision(self):
        """return revision number of the working directory"""
        return None


class HGRepository(VersionedRepository):
    """extract sources/information for a project from a Mercurial repository"""
    id = 'mercurial'
    default_branch = "default"

    def _ref_repo(self):
        return self.repository['source_url']

    def _co_path(self):
        """return the path where the project will be located in the test
        environment
        """
        copath = split_url_or_path(self.ref_repo)[1]
        if self.path:
            copath = osp.join(copath, self.path)
        return copath

    def co_command(self, quiet=True):
        """return a command that may be given to os.system to check out a given
        package
        """
        if quiet:
            return "hg clone -q %s && hg -R %s up '::. and public()'" % (self.ref_repo, self.co_path)
        return "hg clone %s && hg -R %s up '::. and public()'" % (self.ref_repo, self.co_path)

    def co_move_to_branch_command(self, quiet=True):
        # if branch doesn't exist, stay in default
        if self.branch:
            return "hg -R %s up 'first(id(%s) + max(branch(%s) and public()))'" % (
                    self.co_path, self.branch, self.branch)
        return None

    def changeset(self):
        import hglib
        with hglib.open(self.co_path) as repo:
            parents = repo.parents()
        #assert len(parents) == 0 ?
        return parents[0].node[:12]

    def revision(self):
        import hglib
        with hglib.open(self.co_path) as repo:
            parents = repo.parents()
        #assert len(parents) == 0 ?
        return parents[0].rev

register('repository', HGRepository)

