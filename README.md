There are two ways for the project owner to grant API permissions.

User Account:
1. Use an account with Viewer and Security Reviewer permissions on the project (may require the project to activate the Google Identity and Access Management API, which can be done in the console).
2. Approve the Oauth2 authentication request when prompted in your browser.

Service Account:
1. Go to the console service accounts page at https://console.cloud.google.com/iam-admin/serviceaccounts/project?project=[project] and create a service account.
2. Go to IAM management console at https://console.cloud.google.com/iam-admin/iam/project?project=[project]
and add Security Reviewer and Viewer permissions to the service account created in step 1.
3. Generate a Service Account key from https://console.cloud.google.com/apis/credentials?project=[project].
4. Place the JSON file (named keyfile.json) generated in step 3 into the application directory.

For the security reviewer, to run the application:<br>
sudo pip -r requirements.txt <br>
python gscout.py "project" "project name" <br> 
The HTML report output will be in the HTML folder. <br>

When specifying the project name you can also use a wildcard to run G-Scout on multiple projects, for example: python gscout.py "project" "dev-*". You can also run G-Scout on all projects in an organization like this: python gscout.py "organization" "organization id", where the id will be a number you can find next to the organization name in the GCP console. 

To create a custom rule, add it to the rules.py file. A Rule object takes a name, a category, and a filter function. The function will be passed a json object corresponding to the category. To see an example for each category (some of which are altered from the standard API response), see the entity_samples.json file.