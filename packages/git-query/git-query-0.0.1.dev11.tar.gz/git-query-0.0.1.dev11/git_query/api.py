import json
import os
import re

from sh import cut
from sh import git

import requests
from requests.auth import HTTPDigestAuth

from git_query import constants


class Gerrit(object):
    """Adapter for Gerrit REST API.

    """

    def __init__(self, username, http_password):
        self.digest = HTTPDigestAuth(username, http_password)

    def validate(self, response):
        if response.status_code != 200:
            raise Exception(response.text)
        return response

    def list_ssh_keys(self):
        r = self.validate(
            requests.get(constants.SSH_KEYS_URL, auth=self.digest))
        return json.loads(r.text[5:])

    def add_ssh_key(self, ssh_key):
        r = self.validate(
            requests.post(
                constants.SSH_KEYS_URL, data=ssh_key, auth=self.digest))
        return r.text

    def changes(self, params=[]):
        query = '&'.join(map(lambda k: k + '=' + params[k], params))
        r = self.validate(
            requests.get(
                constants.CHANGES_URL + '?' + query, auth=self.digest))
        return json.loads(r.text[5:])


class Git(object):

    def __init__(self):
        self.origin_url = str(git('ls-remote', '--get-url', 'origin'))
        self.repo_name = os.path.split(self.origin_url)[1].replace('.git', '')
        self.change_ids = reduce(self.updateChangeSet, self.getBranches(), {})

    def getChangeId(self, branch):
        '''Gets Gerrit change ID for a branch.

        '''
        try:
            if branch is None:
                return re.search(
                    '(?<=Change-Id: )\w+',
                    str(git('--no-pager', 'show', '--stat'))
                ).group(0)
            else:
                return re.search(
                    '(?<=Change-Id: )\w+',
                    str(git('--no-pager', 'show', '--stat', branch))
                ).group(0)
        except Exception:
            return None

    def getBranches(self):
        # credits to http://stackoverflow.com/a/14693789
        escape = re.compile(r'\x1b[^m]*m')
        return list(
            escape.sub('', s.encode('ascii').rstrip()) for s in
            cut(git('--no-pager', 'branch'), '-c', '3-')
        )

    def updateChangeSet(self, data, branch):
        '''Updates and returns dictionary with Gerrit change id and branch.

        '''
        change_id = self.getChangeId(branch)
        if change_id in data:
            data[change_id].append(branch)
        else:
            data[change_id] = [branch]
        return data
