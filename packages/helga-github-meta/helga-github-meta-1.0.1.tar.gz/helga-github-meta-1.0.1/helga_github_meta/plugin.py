""" Plugin entry point for helga """
import json, requests
from datetime import datetime
from dateutil.parser import parse
from helga import log
from helga.plugins import match

logger = log.getLogger(__name__)

@match(r'github\.com/[\S]*')
def github_meta(client, channel, nick, message, match):
    """ Plugin entry point """
    query = match[0][11:].rstrip('/')
    if query == '':
        return ''
    try:
        if '/' not in query:
            return meta_user(query)
        if 'issues' in query:
            return meta_issue(query)
        return meta_repo(query)
    except Exception as e:
        logger.warn('Github meta exception for ' + query + ":" + e)
    return ''

def meta_repo(query):
    """ Return meta information about a repo """
    meta = execute_request('repos/' + query)
    last_update = time_since(meta['updated_at'])
    template = 'Name: {}, description: {}, last update: {}'
    return template.format(meta['name'], meta['description'], last_update)

def meta_issue(query):
    """ Return meta information about an issue """
    meta = execute_request('repos/' + query)
    last_update = time_since(meta['updated_at'])
    template = 'Title: {}, state: {}, last update: {}'
    return template.format(meta['title'], meta['state'], last_update)

def meta_user(query):
    """ Return meta information about a user """
    meta = execute_request('users/' + query)
    template = 'Name: {}, email: {}, blog: {}, company: {}, public repos: {}'
    return template.format(meta['name'], meta['company'], meta['blog'],
                           meta['email'], meta['public_repos'])

def time_since(time_utc):
    """ Return time since the given utc time """
    modified = datetime.strptime(time_utc,'%Y-%m-%dT%H:%M:%SZ')
    delta = datetime.utcnow() - modified
    return str(delta) + ' ago'

def execute_request(query):
    """ Invoke API to retrieve json hopefully representing request """
    api_url = 'https://api.github.com/'
    response = requests.get(api_url + query)
    if response.status_code != 200:
        raise Exception('Status code returned: ' + str(response.status_code))
    response_json = json.loads(response.content)
    if not response_json:
        raise Exception('Response falsy for given query: ' + query)
    return response_json
