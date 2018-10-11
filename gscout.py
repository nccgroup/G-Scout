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
group.add_argument('--project-name', '-p-name', help='Project name to scan')
group.add_argument('--project-id', '-p-id', help='Project id to scan')
group.add_argument('--organization', '-o', help='Organization id to scan')
group.add_argument('--folder-id', '-f-id', help='Folder id to scan')
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
    service2 = discovery.build('cloudresourcemanager',
                               'v2',credentials=storage.get())
    if project_or_org == "organization":
        child = service2.folders().list(parent='organizations/%s' % specifier)
        child_response = child.execute()
        request = service.projects().list(filter='parent.id:%s' % specifier)
        if 'folders' in child_response.keys() :
            for folder in child_response['folders'] :
                list_projects("folder-id", folder['name'].strip(u'folders/'))
    elif project_or_org == "project-name":
        request = service.projects().list(filter='name:%s' % specifier)
    elif project_or_org == "project-id":
        request = service.projects().list(filter='id:%s' % specifier)
    elif project_or_org=="folder-id":
        child = service2.folders().list(parent='folders/%s' % specifier)
        child_response = child.execute()
        request = service.projects().list(filter='parent.id:%s' % specifier)
        if 'folders' in child_response.keys() :
            for folder in child_response['folders'] :
                list_projects("folder-id", folder['name'].strip(u'folders/'))

    else:
        raise Exception('Organization or Project not specified.')
    add_projects(request, service)

def add_projects(request, service):
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
        if args.project_name :
            list_projects(project_or_org='project-name', specifier=args.project_name)
        elif args.project_id :
            list_projects(project_or_org='project-id', specifier=args.project_id)
        elif args.folder_id :
            list_projects(project_or_org='folder-id', specifier=args.folder_id)
        else:
            list_projects(project_or_org='organization', specifier=args.organization)
    except (HttpAccessTokenRefreshError, ApplicationDefaultCredentialsError):
        from core import config
        list_projects(project_or_org='project' if args.project else 'organization',
                      specifier=args.project if args.project else args.organization)

    for project in db.table("Project").all():
        print("Scouting ", project['projectId'])
        fetch_all(project)


if __name__ == "__main__":
    main()