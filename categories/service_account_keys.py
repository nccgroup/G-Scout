import datetime
import json

from httplib2 import Http
from oauth2client.file import Storage
from googleapiclient import discovery

storage = Storage('creds.data')


def insert_service_account_keys(projectId, db):
    service_accounts = db.table("Service Account").all()
    for sa in service_accounts:
        sa_keys = list_service_account_keys(sa, projectId)
        for sa_key in sa_keys['keys']:
            db.table('Service Account').update(
                add_key({
                    "keyAlgorithm": sa_key['keyAlgorithm'],
                    "validBeforeTime": sa_key['validBeforeTime'],
                    "validAfterTime": sa_key['validAfterTime']
                }),
                eids=[sa.eid])


def list_service_account_keys(sa, projectId):
    service = discovery.build("iam", "v1", credentials=storage.get())
    request = service.projects().serviceAccounts().keys().list(name="projects/" + projectId + "/serviceAccounts/" + sa['email'])
    response = request.execute()
    return response


# Function to pass Tinydb for the update query
def add_key(key):
    def transform(element):
        try:
            element['keys'].append(key)
        except KeyError:
            element['keys'] = [key]

    return transform


def key_is_old(key):
    creation_date = datetime.datetime.strptime(key['validAfterTime'][:10], "%Y-%m-%d")
    if creation_date < datetime.datetime.now() - datetime.timedelta(days=90):
        return True
    return False
