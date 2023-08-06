from .version import *
from .project import Project
from .circle_api import get_latest_build, get_artifact_list
import argparse
import sys
from fnmatch import fnmatch
from urllib.request import urlretrieve

API_ROOT = 'https://circleci.com/api/v1'

def main():
    arguments = argparse.ArgumentParser(description=SHORT_DESCRIPTION)
    arguments.add_argument('--version', action='version', version='%(prog)s ' + VERSION)
    arguments.add_argument('--api-root', type=str, help='API root for CircleCI',
                           default=API_ROOT)
    arguments.add_argument('--token', type=str, help='API key', nargs='?')
    arguments.add_argument('username', type=str, help='GitHub username')
    arguments.add_argument('project', type=str, help='GitHub project')
    arguments.add_argument('artifact', type=str,
                           help='Artifact name (or pattern) to get',
                           nargs='*', default=['*'])
    arguments.add_argument('--branch', type=str,
                           help='Project branch', default='master')
    arguments.add_argument('--accept-failed', action='store_true',
                           help='Accepts artifacts from the latest build')
    arguments.add_argument('--build', type=int, default=None,
                           help='Go to a specific build')
    args = arguments.parse_args()
    project = Project(username = args.username,
                      project  = args.project,
                      api_root = args.api_root,
                      token    = args.token)
    build = args.build
    if build is None:
        build = get_latest_build(project, args.branch, args.accept_failed)
    artifacts = get_artifact_list(project, build)
    for name, url in artifacts.items():
        if any(fnmatch(name, pattern) for pattern in args.artifact):
            print('Downloading {}...'.format(name), end='')
            sys.stdout.flush()
            urlretrieve(url, filename=name)
            print('{}[DONE]'.format(' '*(60 - len(name))))
