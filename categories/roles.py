import json
from googleapiclient import discovery
from oauth2client.file import Storage

storage = Storage('creds.data')
service = discovery.build('cloudresourcemanager', 'v1', credentials=storage.get())

def insert_roles(projectId, db):
    request = service.projects().getIamPolicy(resource=projectId, body={})
    response = request.execute()['bindings']
    for role in response:
        db.table('Role').insert(role)
