import requests
from jinja2 import Template
import ConfigParser
import logging
import argparse



log = logging.getLogger('bbissues')


parser = argparse.ArgumentParser(
    description='Collect issues from bitbucket issue trackers.')
parser.add_argument('--config', dest='config_path', help='Config file.',
    required=True)


BASE_URL = 'https://api.bitbucket.org/1.0/repositories/gocept/{}/issues?status=!resolved'
WEB_BASE_URL = 'https://bitbucket.org/{}'
TEMPLATE = ''


def collect_project_issues(project):
    url = BASE_URL.format(project)
    result = requests.get(url)
    if not result.ok:
        error = result.json()['error']['message']
        log.warn('Error while calling {}: {}'.format(url, error))
        return
    issues = result.json()
    data = []
    for issue in issues['issues']:
        issuedata = dict(
            title=issue['title'],
            content=issue['content'],
            status=issue['status'],
            created=issue['created_on'],
            priority=issue['priority'],
            url=WEB_BASE_URL.format(issue['resource_uri'][18:]),
            author=issue['reported_by']['display_name'])
        data.append(issuedata)
    return data


def main():
    args = parser.parse_args()
    config = ConfigParser.ConfigParser()
    config.read(args.config_path)
    with open(config.get('config', 'template_path')) as templatefile:
        TEMPLATE = Template(templatefile.read())
    logging.basicConfig(
        filename=config.get('config', 'log'), level=logging.WARNING)
    projects = config.get('config', 'projects')
    projectsdata = []
    for project in projects.split():
        issuedata = collect_project_issues(project)
        if issuedata is not None:
            projectsdata.append(dict(name=project, issues=issuedata))

    result = TEMPLATE.render(projects=projectsdata)
    print result


if __name__ == '__main__':
    main()
