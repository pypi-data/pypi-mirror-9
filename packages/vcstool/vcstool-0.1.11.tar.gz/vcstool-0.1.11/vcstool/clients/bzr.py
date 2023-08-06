import copy
import os

from .vcs_base import VcsClientBase, which


class BzrClient(VcsClientBase):

    type = 'bzr'
    _executable = None

    @staticmethod
    def is_repository(path):
        return os.path.isdir(os.path.join(path, '.bzr'))

    def __init__(self, path):
        super(BzrClient, self).__init__(path)

    def branch(self, _command):
        return self._get_parent_branch()

    def custom(self, command):
        cmd = [BzrClient._executable] + command.args
        return self._run_command(cmd)

    def diff(self, _command):
        cmd = [BzrClient._executable, 'diff']
        return self._run_command(cmd)

    def import_(self, command):
        if not command.url:
            return {
                'cmd': '',
                'cwd': self.path,
                'output': "Repository data lacks the 'url' value",
                'returncode': 1
            }

        not_exist = self._create_path()
        if not_exist:
            return not_exist

        if BzrClient.is_repository(self.path):
            # verify that existing repository is the same
            result_parent_branch = self._get_parent_branch()
            if result_parent_branch['returncode']:
                return result_parent_branch
            parent_branch = result_parent_branch['output']
            if parent_branch != command.url:
                return {
                    'cmd': '',
                    'cwd': self.path,
                    'output': 'Path already exists and contains a different repository',
                    'returncode': 1
                }
            # pull updates for existing repo
            cmd_pull = [BzrClient._executable, 'pull']
            return self._run_command(cmd_pull)

        else:
            cmd_branch = [BzrClient._executable, 'branch']
            if command.version:
                cmd_branch += ['-r', command.version]
            cmd_branch += [command.url, '.']
            result_branch = self._run_command(cmd_branch)
            if result_branch['returncode']:
                result_branch['output'] = "Could not branch repository '%s': %s" % (command.url, result_branch['output'])
                return result_branch
            return result_branch

    def log(self, command):
        if command.limit_tag or command.limit_untagged:
            tag = None
            if command.limit_tag:
                tag = command.limit_tag
            else:
                # determine nearest tag
                cmd_tag = [BzrClient._executable, 'tags', '--sort=time']
                result_tag = self._run_command(cmd_tag)
                if result_tag['returncode']:
                    return result_tag
                for line in result_tag['output'].splitlines():
                    parts = line.split(' ', 2)
                    if parts[1] != '?':
                        tag = parts[0]
                if not tag:
                    result_tag['output'] = 'Could not determine latest tag',
                    result_tag['returncode'] = 1
                    return result_tag
            # determine revision number of tag
            cmd_tag_rev = [BzrClient._executable, 'revno', '--rev', 'tag:%s' % tag]
            result_tag_rev = self._run_command(cmd_tag_rev)
            if result_tag_rev['returncode']:
                if command.limit_tag:
                    result_tag_rev['output'] = "Repository lacks the tag '%s'" % tag
                return result_tag_rev
            try:
                tag_rev = int(result_tag_rev['output'])
                tag_next_rev = tag_rev + 1
            except ValueError:
                tag_rev = result_tag_rev['output']
                tag_next_rev = tag_rev
            # determine revision number of HEAD
            cmd_head_rev = [BzrClient._executable, 'revno']
            result_head_rev = self._run_command(cmd_head_rev)
            if result_head_rev['returncode']:
                return result_head_rev
            try:
                head_rev = int(result_head_rev['output'])
            except ValueError:
                head_rev = result_head_rev['output']
            # output log since nearest tag
            cmd_log = [BzrClient._executable, 'log', '--rev', 'revno:%s..' % str(tag_next_rev)]
            if tag_rev == head_rev:
                return {
                    'cmd': ' '.join(cmd_log),
                    'cwd': self.path,
                    'output': '',
                    'returncode': 0
                }
            result_log = self._run_command(cmd_log)
            return result_log
        cmd = [BzrClient._executable, 'log']
        if command.limit != 0:
            cmd += ['--limit', '%d' % command.limit]
        return self._run_command(cmd)

    def pull(self, _command):
        cmd = [BzrClient._executable, 'pull']
        return self._run_command(cmd)

    def push(self, _command):
        cmd = [BzrClient._executable, 'push']
        return self._run_command(cmd)

    def remotes(self, _command):
        return self._get_parent_branch()

    def status(self, _command):
        cmd = [BzrClient._executable, 'status']
        return self._run_command(cmd)

    def _get_parent_branch(self):
        cmd = [BzrClient._executable, 'info']
        # parsing the text output requires enforcing language
        env = copy.copy(os.environ)
        env['LANG'] = 'en_US.UTF-8'
        result = self._run_command(cmd, env)
        if result['returncode']:
            return result
        branch = None
        prefix = '  parent branch: '
        for line in result['output'].splitlines():
            if line.startswith(prefix):
                branch = line[len(prefix):]
                break
        if not branch:
            result['output'] = 'Could not determine parent branch',
            result['returncode'] = 1
            return result
        result['output'] = branch
        return result


if not BzrClient._executable:
    BzrClient._executable = which('bzr')
    if not BzrClient._executable:
        raise ImportError('Could not find executable "bzr" for vcstool.clients.BzrClient')
