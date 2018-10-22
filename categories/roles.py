import json

from googleapiclient import discovery
from httplib2 import Http
from oauth2client.file import Storage
from core.utility import get_gcloud_creds

storage = Storage('creds.data')
service = discovery.build('iam', 'v1', credentials=get_gcloud_creds())


def insert_roles(projectId, db):
    headers = {"Content-Length": 0}
    try:
        resp, content = get_gcloud_creds().authorize(Http()).request(
            "https://cloudresourcemanager.googleapis.com/v1/projects/" + projectId + ":getIamPolicy", "POST",
            headers=headers)
        role_list = None
        try:
            role_list = json.loads(content)['bindings']
		#	request = service.roles().list()
		#	response = request.execute()
		#	if 'roles' in response:
		#		role_list = response['roles']
		#	else:
		#		print("Warning: no roles returned for project '%s'" % (projectId))
        except Exception as e:
            print("Error obtaining role list from JSON: %s" % (e))
            #print("Error obtaining role list: %s" % (e))
        if role_list:
            for role in role_list:
                try:
                    db.table('Role').insert(role)
                except Exception as e:
                    print("Error inserting role into database: %s" % (e))
        # this does not support pagination of results
    except Exception as e:
        print("Error enumerating roles: %s" % (e))
