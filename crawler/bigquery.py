"""Connection to Google BigQuery."""

import os
from google.cloud import bigquery
import gender_guesser.detector as gender


USERSCHEMA = (
    bigquery.SchemaField('id', 'INTEGER', mode='required'),
    bigquery.SchemaField('owner_login', 'STRING', mode='required'),
    bigquery.SchemaField('avatar_url', 'STRING', mode='required'),
    bigquery.SchemaField('followers_url', 'STRING', mode='required'),
    bigquery.SchemaField('following_url', 'STRING', mode='required'),
    bigquery.SchemaField('starred_url', 'STRING', mode='required'),
    bigquery.SchemaField('subscriptions_url', 'STRING', mode='required'),
    bigquery.SchemaField('repos_url', 'STRING', mode='required'),
    bigquery.SchemaField('events_url', 'STRING', mode='required'),
    bigquery.SchemaField('name', 'STRING'),
    bigquery.SchemaField('company', 'STRING'),
    bigquery.SchemaField('blog', 'STRING'),
    bigquery.SchemaField('location', 'STRING'),
    bigquery.SchemaField('bio', 'STRING'),
    bigquery.SchemaField('public_repos', 'STRING',),
    bigquery.SchemaField('followers', 'INTEGER'),
    bigquery.SchemaField('following', 'INTEGER'),
    bigquery.SchemaField('created_at', 'STRING'),
    bigquery.SchemaField('updated_at', 'STRING'),
)

REPOSCHEMA = (
    bigquery.SchemaField('id', 'INTEGER', mode='required'),
    bigquery.SchemaField('name', 'STRING', mode='required'),
    bigquery.SchemaField('full_name', 'STRING', mode='required'),
    bigquery.SchemaField('owner_login', 'STRING', mode='required'),
    bigquery.SchemaField('owner_id', 'INTEGER', mode='required'),
    bigquery.SchemaField('description', 'STRING'),
    bigquery.SchemaField('forks_url', 'STRING', mode='required'),
    bigquery.SchemaField('events_url', 'STRING', mode='required'),
    bigquery.SchemaField('languages_url', 'STRING', mode='required'),
    bigquery.SchemaField('commits_url', 'STRING', mode='required'),
    # This contains a list of JSON objects in the format [{ 'length': INTEGER, 'stats': { 'total': INTEGER, 'additions': INTEGER, 'deletions': INTEGER } }]
    bigquery.SchemaField('commits', 'STRING', mode='required'),
    bigquery.SchemaField('created_at', 'STRING', mode='required'),
    bigquery.SchemaField('updated_at', 'STRING', mode='required'),
    bigquery.SchemaField('pushed_at', 'STRING', mode='required'),
    bigquery.SchemaField('size', 'INTEGER', mode='required'),
    bigquery.SchemaField('stargazers_count', 'INTEGER', mode='required'),
    bigquery.SchemaField('langauge', 'STRING'),
    bigquery.SchemaField('has_wiki', 'BOOLEAN', mode='required'),
    bigquery.SchemaField('forks_count', 'INTEGER', mode='required'),
    bigquery.SchemaField('open_issues_count', 'INTEGER', mode='required'),
)

DUMPSIZE = 1000

class BigQuery:
    """Instance of Google BigQuery."""
    def __init__(self):
        """Set up the Google BigQuery connection."""
        # Set up the environmental variable for Google API credentials
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './crawler/creds.json'

        self.client = bigquery.Client()
        dataset_id = 'githubby'
        dataset_ref = self.client.dataset(dataset_id)
        dataset = bigquery.Dataset(dataset_ref)

        if dataset_id not in [dataset.dataset_id for dataset in self.client.list_datasets()]:
            dataset = self.client.create_dataset(dataset)
            print('Dataset {} created and connection established.'.format(
                dataset.dataset_id))
        else:
            print('Dataset {} connection established.'.format(dataset.dataset_id))
        table_users_ref = dataset_ref.table('users')
        table_repos_ref = dataset_ref.table('repos')

        table_users = bigquery.Table(table_users_ref, schema=USERSCHEMA)
        table_repos = bigquery.Table(table_repos_ref, schema=REPOSCHEMA)

        # tables = list(bigquery_client.list_dataset_tables(dataset))

        # table_users = self.client.create_table(table_users)
        # table_repos = self.client.create_table(table_repos)

        self.table_users = self.client.get_table(table_users)
        self.table_repos = self.client.get_table(table_repos)

        self.dump_user = []
        self.dump_repo = []


    def insertrepo(self, rows):
        """Inserts repo rows in buffer to be sent to BigQuery."""
        self.dump_repo += rows

        if len(rows) > DUMPSIZE:
            errors = self.client.create_rows(self.table_repos, self.dump_repo)
            print('Took a repo dump')
            self.dump_repo = []
            if errors != []:
                print(rows)
                print(errors)


    def insertuser(self, rows):
        """Inserts user rows in buffer to be sent to BigQuery."""
        self.dump_user += rows

        if len(rows) > DUMPSIZE:
            errors = self.client.create_rows(self.table_users, self.dump_user)
            print('Took a user dump')
            self.dump_user = []
            if errors != []:
                print(rows)
                print(errors)


    def queryall(self):
        """Gets all users and repos from BigQuery. Comes back in the format:
            male: { ownerlogin: [user data..., repos: [list of [repo data...]]] }
            female: { ownerlogin: [user data..., repos: [list of [repo data...]]] }
        """
        userjob = self.client.query('SELECT * FROM `precise-tenure-184101.githubby.users`')
        users = userjob.result()

        repojob = self.client.query('SELECT * FROM `precise-tenure-184101.githubby.repos`')
        repos = repojob.result()

        maleresults = {}
        femaleresults = {}

        # Get all user info
        gd = gender.Detector()
        for user in users:
            name = user['name']
            # Assume male by default
            results = maleresults
            # Identify gender if available, otherwise stick with default
            if name is not None and not name.isspace():
                firstname = name.split()[0]
                sex = gd.get_gender(firstname)
                if 'female' in sex:
                    results = femaleresults
            ownerlogin = user['owner_login']
            user = [val for val in user]
            results[ownerlogin] = user
            user.append([])

        # Get all repo info
        for repo in repos:
            #if 'owner_login' in repo:
            ownerlogin = repo['owner_login']
                # Add repo to male user
            repo = [val for val in repo]
            if ownerlogin in maleresults:
                maleresults[ownerlogin][-1].append(repo)
            # Add repo to female user
            elif ownerlogin in femaleresults:
                femaleresults[ownerlogin][-1].append(repo)

        return maleresults, femaleresults
