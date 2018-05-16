from googleapiclient import discovery
from oauth2client.client import ApplicationDefaultCredentialsError
from oauth2client.client import HttpAccessTokenRefreshError
from oauth2client.file import Storage
from tinydb import TinyDB
import os
from core.fetch import fetch
import logging
import argparse

# configure command line parameters
parser = argparse.ArgumentParser(description='Google Cloud Platform Security Tool')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--project', '-p', help='Project name to scan')
group.add_argument('--organization', '-o', help='Organization id to scan')
args = parser.parse_args()

storage = Storage('creds.data')

logging.basicConfig(filename="log.txt")
logging.getLogger().setLevel(logging.ERROR)
# Silence some errors
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

try:
    os.remove("projects.json")
except:
    pass
db = TinyDB('projects.json')


def list_projects(project_or_org, specifier):
    service = discovery.build('cloudresourcemanager',
                              'v1', credentials=storage.get())

    if project_or_org == "organization":
        request = service.projects().list(filter='parent.id:%s' % specifier)
    elif project_or_org == "project":
        request = service.projects().list(filter='name:%s' % specifier)
        # TODO add filtering with project ID
        # request = service.projects().list(filter='id:%s' % specifier)
    else:
        raise Exception('Organization or Project not specified.')
    while request is not None:
        response = request.execute()
        if 'projects' in response.keys():
            for project in response['projects']:
                if (project['lifecycleState'] != "DELETE_REQUESTED"):
                    db.table('Project').insert(project)

        request = service.projects().list_next(previous_request=request,
                                               previous_response=response)


def fetch_all(project):
    try:
        os.makedirs("project_dbs")
    except:
        pass
    try:
        os.makedirs("Report Output/" + project['projectId'])
    except:
        pass
    try:
        fetch(project['projectId'])
    except Exception as e:
        print("Error fetching ", project['projectId'])
        logging.exception(e)


def main():

    try:
        os.makedirs("Report Output")
    except:
        pass
    try:
        list_projects(project_or_org='project' if args.project else 'organization',
                      specifier=args.project if args.project else args.organization)
    except (HttpAccessTokenRefreshError, ApplicationDefaultCredentialsError):
        from core import config
        list_projects(project_or_org='project' if args.project else 'organization',
                      specifier=args.project if args.project else args.organization)

    for project in db.table("Project").all():
        print("Scouting ", project['projectId'])
        fetch_all(project)


if __name__ == "__main__":
    main()