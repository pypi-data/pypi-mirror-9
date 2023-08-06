try:
    import simplejson as json
except ImportError:
    import json
import requests
import six

from quantumpy.exceptions import *
from decimal import Decimal

class QuantumAPI(object):
    def __init__(self, account_id, jwt, url='https://api.quantum.socialmetrix.com', timeout=None):
        self.url        = url.strip('/')
        self.session    = requests.session()
        self.account_id = account_id
        self.jwt        = jwt
        self.headers    = {'X-Auth-Token': jwt}
        self.timeout    = timeout

    def get_projects(self, retry=3):
        """
        /account/{account_id}/projects
        Get all available projects for account
        """
        response = self._query(
            method = 'GET',
            path   = '/account/{}/projects'.format(self.account_id),
            retry  = retry
        )

        if response is False:
            raise QuantumError('Could not get projects.')

        return response

    def get_project(self, project_id, retry=3):
        """
        /account/{account_id}/projects/{project_id}
        Get project properties by id
        """
        response = self._query(
            method = 'GET',
            path   = '/account/{}/projects/{}'.format(self.account_id, project_id)
        )

        if response is False:
            raise QuantumError('Could not get project {}.'.format(project_id))

        return response

    def get_fanpages_stat_summary(self, project_id, since, until, entities, timezone='-02:00', retry=3):
        """
        /account/{account_id}/project/{project_id}/profiles/fanpages/stat-summary?
            since={start_date}
            until={end_date}
            entities={fanpages}
            timezone={timezone}
        Get stat summary for fanpages within a project
        """
        args = locals()
        params = {param: args[param] for param in ['since', 'until', 'entities', 'timezone']}
        response = self._query(
            method = 'GET',
            path   = '/account/{}/project/{}/facebook/profiles/stat-summary'.format(self.account_id, project_id),
            params = params,
            retry  = retry
        )

        if response is False:
            raise QuantumError('Could not get stat summary for project {}.'.format(project_id))

        return response

    def get_fanpages_post_interactions(self, project_id, since, until, entities, timezone='-02:00', retry=3):
        """
        /account/{account_id}/project/{project_id}/facebook/profiles/posts-interactions/count/date?
            since={start_date}
            until={end_date}
            entities={posts}
            timezone={timezone}
        Get post interactions for posts within a project
        """
        args = locals()
        params = {param: args[param] for param in ['since', 'until', 'entities', 'timezone']}
        response = self._query(
            method = 'GET',
            path   = '/account/{}/project/{}/facebook/profiles/posts-interactions/count/date'.format(self.account_id, project_id),
            params = params,
            retry  = retry
        )

        if response is False:
            raise QuantumError('Could not get stat summary for project {}.'.format(project_id))

    def _query(self, method, path, params=None, retry=0):
        if not path.startswith('/'):
            if six.PY2:
                path = '/' + six.text_type(path.decode('utf-8'))
            else:
                path = '/' + path

        url = self.url + path

        try:
            return self._request(method, url, params)
        except QuantumPythonError:
            if retry:
                return self._query(method, path, params, retry - 1)
            else:
                raise

    def _request(self, method, url, params):
        if params:
            for key in params:
                value = params[key]
            if isinstance(value, (list, dict, set)):
                params[key] = json.dumps(value)

        try:
            if method == 'GET':
                response = self.session.request(
                    method,
                    url,
                    data            = params,
                    allow_redirects = True,
                    timeout         = self.timeout,
                    headers         = self.headers
                )
            if method in ['POST', 'PUT', 'DELETE']:
                raise NotImplementedError(
                    'Quantum API does not yet support {} requests'.format(method)
                )
        except requests.RequestException as e:
            raise HTTPError(e)

        return self._parse(response.content)

    def _parse(self, data):
        if type(data) == type(bytes()):
            data = data.decode('utf-8')
        data = json.loads(data, parse_float=Decimal)

        if type(data) is dict:
            if 'code' in data:
                if data['code'] == 'authentication':
                    raise AuthenticationError(data['message'])
            elif 'message' in data:
                if 'Handler not found' in data['message']:
                    raise HandlerNotFoundError(data['message'])
                elif 'Internal server error' in data['message']:
                    raise InternalServerError(data['message'])

        return data
