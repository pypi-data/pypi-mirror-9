import requests
from urllib.parse import urljoin

from .project import Project

def get_latest_build(project, branch, allow_failures=False):
    filt = 'completed' if allow_failures else 'successful'
    target = '{root}/project/{user}/{project}/tree/{branch}?limit=1&filter={filt}'.format(
                root=project.api_root,
                user=project.username,
                project=project.project,
                branch=branch,
                filt=filt)
    if project.token is not None:
        target += '&circle-token={}'.format(project.token)
    data = requests.get(target, headers={'Accept': 'application/json'})
    output = data.json()
    if len(output) == 0:
        raise ValueError('No matching builds.')
    return output[0]['build_num']

def get_artifact_list(project, build):
    target = '{root}/project/{user}/{project}/{build}/artifacts'.format(
                root=project.api_root,
                user=project.username,
                project=project.project,
                build=build)
    if project.token is not None:
        target += '?circle-token={}'.format(project.token)
    data = requests.get(target, headers={'Accept': 'application/json'})
    output = data.json()
    return {x['pretty_path'][18:]: x['url'] for x in output}

