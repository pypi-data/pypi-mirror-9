"""
Author: Ryan Brown <sb@ryansb.com>
License: Apache 2.0
"""

import logging
import os
import pkg_resources
import re
import six
import socket
import uuid

import requests
import time
import oshift
from StringIO import StringIO
import dulwich.porcelain as git


class NotFound(BaseException):
    pass


openshift_files = {
    "setup.py": {
        "contents": """from setuptools import setup
setup(name='thecourse',
      version='1.0',
      description='courseware on openshift',
      author='Dr. Professor',
      author_email='dr@professor.com',
      url='http://www.python.org/sigs/distutils-sig/',
      install_requires=['ofcourse>={version}'],
     )""".format(version=pkg_resources.get_distribution('ofcourse').version),
    },
    "wsgi.py": {
        "contents": """#!/usr/bin/python
# IMPORTANT: Please do not make changes to this file unless you know what
# you're doing. Thank you.

import os

virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
try:
    execfile(virtualenv, dict(__file__=virtualenv))
except IOError:
    pass

import ofcourse.site

application = ofcourse.site.app""",
    },
}


class TempBranch(object):
    def __init__(self, name, repo, delete=True):
        self.branch = 'refs/heads/{}'.format(name)
        self.delete = delete
        self.repo = repo

        # save the starting branch so we know where to go back to
        self.start = self.repo.refs.read_ref('HEAD').replace('ref: ', '')

    def __enter__(self):
        self.repo.refs.add_if_new(self.branch, self.repo.head())

        self.repo.refs.set_symbolic_ref('HEAD', self.branch)

    def __exit__(self, exc_type, value, tb):
        if value is None:
            self.repo.refs.set_symbolic_ref('HEAD', self.start)
            # lol, only reset --hard is supported
            if self.delete:
                self.repo.refs.remove_if_equals(self.branch, None)
        else:
            six.reraise(exc_type, value, tb)

        git.reset(self.repo, "hard")


def push(name, api, domain):
    repo = git.Repo(os.getcwd())
    branch = "temp-{}".format(str(uuid.uuid4())[:8])
    set_deploy_branch(name, branch, api, domain)

    remote = git_url(name, api, domain)

    if is_dirty():
        print("Nuking changes.")
        git.reset(repo, "hard")

    with TempBranch(branch, repo, delete=True):
        for fname, file_info in openshift_files.items():
            with open(fname, 'w') as f:
                f.write(file_info.get("contents", ""))
            repo.stage(fname)
        repo.do_commit("Commit openshift files")
        push_out = StringIO()
        push_err = StringIO()
        print("Pushing to openshift (may take a few minutes)")
        git.push(repo, remote, "refs/heads/{}".format(branch),
                 outstream=push_out, errstream=push_err)

        push_out.seek(0)
        out = push_out.read()
        if not re.match(r'^Push to .* successful.', out):
            print("There was a failure while pushing")
            print("---BEGIN STDERR---")
            push_err.seek(0)
            print(push_err.read())
            print("---BEGIN STDOUT---")
            print(out)
            print("There was a failure while pushing")
        git.rm(repo, openshift_files.keys())
        map(os.remove, openshift_files.keys())

    return get_app(name, api, domain)['app_url']


def is_clean():
    return not is_dirty()


def is_dirty():
    """Check for uncommitted changes. True if dirty."""
    repo = git.Repo(os.getcwd())
    s = git.status(repo)
    return any(s.staged.values() + [s.unstaged])


def get_api(token):
    oshift.log.setLevel(logging.FATAL)
    return oshift.Openshift("openshift.redhat.com", token=token)


def generate_token(uname, passwd):
    session = requests.post(
        "https://openshift.redhat.com/broker/rest/user/authorizations",
        auth=requests.auth.HTTPBasicAuth(uname, passwd),
        params={'scope': 'session'}
    )
    if session.status_code != 201:
        raise Exception("Uhoh {} response={}".format(session.status_code,
                                                     session.text))
    return session.json().get("data", {}).get("token", "")


def new_app(name, api, domain, wait_until_available=True):
    try:
        get_app(name, api, domain)
        return
    except:
        pass
    # Ok, the app doesn't exist
    api.app_create(name, ['python-2.7'], domain_name=domain)
    if not wait_until_available:
        return
    while True:
        try:
            app = get_app(name, api, domain)
            socket.getaddrinfo(requests.utils.urlparse(
                app['app_url']).netloc, 80)
            break
        except NotFound:
            print("Waiting for new app...")
            time.sleep(5)
        except socket.gaierror as e:
            if e.errno != -2:
                raise e
            print("Waiting for new app...")
            time.sleep(5)


def get_app(name, api, domain):
    apps = [a for a in api.app_list(domain_name=domain)[1]
            if a.get("name", "") == name]
    if apps:
        return apps[0]
    raise NotFound("Could not find app {}".format(name))


def git_url(name, api, domain):
    app = get_app(name, api, domain)
    remote = app['git_url']
    # change SSH URL
    # from "ssh://user@host/dir/repo.git"
    # to         "user@host:dir/repo.git"
    return remote.replace("ssh://", "").replace("/", ":", 1)


def set_deploy_branch(name, branch, api, domain):
    app = get_app(name, api, domain)
    if app['deployment_branch'] != branch:
        api.app_action('UPDATE', name, domain_name=domain,
                       deployment_branch=branch)
