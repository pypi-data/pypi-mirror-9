from fabric.operations import run, prompt
from fabric.api import task, env, get, put, local
from fabric.contrib.files import exists
import ConfigParser
import StringIO
import posixpath
from .utils import STATIC_COLLECTED, DATA_DIRECTORY
from django_utils import django_settings_file, append_settings
import os
from .messages import CAUTION
from .utils import config


@task
def update():
    test = run("cd %(path)s; git --no-pager diff --stat" % env)
    if "files changed" in test:
        print CAUTION
        print "You have local file changes to the git repository on the server. Run 'fab %s git.reset' to remove them, " \
              "or keep them by applying the diff locally with the command 'git apply filename.diff' and upload it to your git host" % env.identifier
        print
        print "You now have the following options:"
        print
        print "[D]ownload diff"
        print "Continue and [R]eset changes"
        print "[E]xit"
        download_diff = prompt("What do you want to do?", default="D")
        if download_diff.lower() == "d":
            diff = run(("cd %(path)s; git diff --color .") % env)
            for i in range(1, 50):
                print
            print diff
            for i in range(1, 5):
                print
            exit()
        elif download_diff.lower() == "e":
            exit()
    run("cd %(path)s; find . -iname '*.pyc' -delete" % env)
    run("cd %(path)s; git fetch origin" % env)
    run("cd %(path)s; git reset --hard" % env)
    run("cd %(path)s; git checkout %(branch)s" % env)
    run("cd %(path)s; git pull origin %(branch)s" % env)
    if exists(posixpath.join(env.path, ".gitmodules")):
        run("cd %(path)s; git submodule init" % env)
        run("cd %(path)s; git submodule update" % env)
    append_settings()


@task
def diff(what=''):
    run(("cd %(path)s; git --no-pager diff " + what) % env)


@task
def status():
    run("cd %(path)s; git status" % env)


@task
def reset():
    """
    discard all non-committed changes
    """
    run("cd %(path)s; find . -iname '*.pyc' -delete" % env)
    run("cd %(path)s; git reset --hard HEAD" % env)


@task
def incoming(remote='origin', branch=None):
    """
    Displays incoming commits 
    """
    if not branch:
        branch = env.branch
    run(("cd %(path)s; git fetch " + remote + " && git log --oneline .." + remote + '/' + branch) % env)


def local_branch_is_dirty(ignore_untracked_files=True):
    untracked_files = '--untracked-files=no' if ignore_untracked_files else ''
    git_status = local(
        'git status %s --porcelain' % untracked_files, capture=True)
    return git_status != ''


def local_branch_matches_remote():
    local_branch = local(
        'git rev-parse --symbolic-full-name --abbrev-ref HEAD',
        capture=True).strip()
    target_branch = env.branch.strip()
    return local_branch == target_branch
