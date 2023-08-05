# -*- coding: utf-8 -*-

import requests

github_api = 'https://api.github.com'


class GitHub(object):

    def __init__(self, user='Jayin'):
        self.user = user

    def get_releases(self, owner, repo):
        url = github_api + '/repos/{owner}/{repo}/releases' . format(owner=owner,repo=repo)
        r = requests.get(url)
        return r.json()

    def get_silentor_latest(self):
        latest_rc = self.get_releases('jayin', 'silentor')[0]
        return latest_rc





