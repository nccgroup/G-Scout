import json

from oauth2client.file import Storage
from httplib2 import Http
from core.utility import get_gcloud_creds


def insert_service_accounts(projectId, db):
    try:
        # s = storage.get()
        # if s:
            # resp, content = s.authorize(Http()).request(
                # "https://iam.googleapis.com/v1/projects/" + projectId + "/serviceAccounts/", "GET")
            # for account in json.loads(content)['accounts']:
                # try:
                    # db.table("Service Account").insert(account)
                # except Exception as e:
                    # print("Error inserting service account into database: %s" % (e))
        # else:
            # print("Warning: could not authorize storage access.")
        
    #except Exception as e:
    #   print("Error authorizing Storage access: %s" % (e))
        # service = discovery.build('cloudresourcemanager','v1', credentials=get_gcloud_creds())    
        # request = service.regions().list(project=projectId)
        # while request is not None:
            # response = request.execute()
            # for region in response['items']:
                # #print("Debug: %s" % (region))
                # if 'description' in region.keys():
                    # region_list.append(region['description'])
            # request = service.regions().list_next(previous_request=request, previous_response=response)
        resp, content = get_gcloud_creds().authorize(Http()).request(
            "https://iam.googleapis.com/v1/projects/" + projectId + "/serviceAccounts/", "GET")
        for account in json.loads(content)['accounts']:
            try:
                db.table("Service Account").insert(account)
            except Exception as e:
                print("Error inserting service account '%s' into database: %s" % (account, e))
    except Exception as e:
        print("Error inserting service accounts: %s" % (e))    


def add_role(role):
    def transform(element):
        try:
            element['roles'].append(role)
        except KeyError:
            element['roles'] = [role]

    return transform


def insert_sa_roles(projectId, db):
    for role in db.table('Role').all():
        for sa in db.table('Service Account').all():
            if "serviceAccount:" + str.split(str(sa['name']), '/')[-1] in role['members']:
                db.table("Service Account").update(
                    add_role(role['role']),
                    eids=[sa.eid])
