try:
    import simplejson as json
except ImportError:
    import json
import requests
import six

from quantumpy.exceptions import *
from decimal import Decimal
from urlparse import urlparse, parse_qsl

class QuantumAPI(object):
    def __init__(self, account_id, jwt, url='https://api.quantum.socialmetrix.com/v1', timeout=None):
        self.url        = url.strip('/')
        self.session    = requests.Session()
        self.account_id = account_id
        self.jwt        = jwt
        self.headers    = {'X-Auth-Token': jwt}
        self.timeout    = timeout

    def get_projects(self, retry=3):
        """
        /accounts/{account_id}/projects
        Get all available projects for account
        """
        response = self._query(
            method = 'GET',
            path   = '/accounts/{}/projects'.format(self.account_id),
            retry  = retry
        )

        if response is False:
            raise QuantumError('Could not get projects.')

        return response

    def get_project_by_id(self, project_id, retry=3):
        """
        /accounts/{account_id}/projects/{project_id}
        Get project properties by id
        """
        response = self._query(
            method = 'GET',
            path   = '/accounts/{}/projects/{}'.format(self.account_id, project_id)
        )

        if response is False:
            raise QuantumError('Could not get project {}.'.format(project_id))

        return response

    def get_facebook_profiles_stat_summary(self, project_id, since, until, ids, timezone='UTC', retry=3):
        """
        /accounts/{account_id}/projects/{project_id}/facebook/profiles/stat-summary?
            since={start_date}
            until={end_date}
            ids={fanpages}
            timezone={timezone}
        Get stat summary for fanpages within a project
        """
        args = locals()
        params = {param: args[param] for param in ['since', 'until', 'ids', 'timezone']}
        response = self._query(
            method = 'GET',
            path   = '/accounts/{}/projects/{}/facebook/profiles/stat-summary'.format(self.account_id, project_id),
            params = params,
            retry  = retry
        )

        if response is False:
            raise QuantumError('Could not get stat summary for project {}.'.format(project_id))

        return response

    def get_facebook_profiles_posts(self, project_id, fanpage_id, since, until, ids, owner=None, type=None, page=False, timezone='UTC', retry=3):
        """
        /accounts/{account_id}/projects/{project_id}/facebook/profiles/{fanpage_id}/posts?
            since={start_date}
            until={end_date}
            ids={fanpages}
            owner={owner}
            type={type}
            timezone={timezone}
        Get all posts for a given fanpage and period
        """
        args = locals()
        params = {param: args[param] for param in ['since', 'until', 'ids', 'owner', 'type', 'timezone']}
        response = self._query(
            method = 'GET',
            path   = '/accounts/{}/projects/{}/facebook/profiles/{}/posts'.format(self.account_id, project_id, fanpage_id),
            params = params,
            retry  = retry,
            page   = page
        )

        if response is False:
            raise QuantumError('Could not get posts for fanpage {}.'.format(fanpage_id))

        return response

    def get_facebook_profiles_post_interactions(self, project_id, since, until, ids, timezone='UTC', retry=3):
        """
        /accounts/{account_id}/projects/{project_id}/facebook/profiles/posts-interactions/count/date?
            since={start_date}
            until={end_date}
            ids={posts}
            timezone={timezone}
        Get post interactions for posts within a project
        """
        args = locals()
        params = {param: args[param] for param in ['since', 'until', 'ids', 'timezone']}
        response = self._query(
            method = 'GET',
            path   = '/accounts/{}/projects/{}/facebook/profiles/posts-interactions/count/date'.format(self.account_id, project_id),
            params = params,
            retry  = retry
        )

        if response is False:
            raise QuantumError('Could not get post interactions for project {}.'.format(project_id))

        return response

    def get_facebook_fans_total_by_country(self, project_id, since, until, ids, timezone='UTC', retry=3):
        """
        /accounts/{account_id}/projects/{project_id}/facebook/fans/total/country?
            since={start_date}
            until={end_date}
            ids={fanpages}
            timezone={timezone}
        """
        args = locals()
        params = {param: args[param] for param in ['since', 'until', 'ids', 'timezone']}
        response = self._query(
            method = 'GET',
            path   = '/accounts/{}/projects/{}/facebook/fans/total/country'.format(self.account_id, project_id),
            params = params,
            retry  = retry
        )

        if response is False:
            raise QuantumError('Could not get fans by country for profile {}.'.format(project_id))

        return response

    def get_facebook_fans_count_by_date(self, project_id, since, until, ids, timezone='UTC', retry=3):
        """
        /accounts/{account_id}/projects/{project_id}/facebook/fans/count/date?
            since={start_date}
            until={end_date}
            ids={fanpages}
            timezone={timezone}
        """
        args = locals()
        params = {param: args[param] for param in ['since', 'until', 'ids', 'timezone']}
        response = self._query(
            method = 'GET',
            path   = '/accounts/{}/projects/{}/facebook/fans/count/date'.format(self.account_id, project_id),
            params = params,
            retry  = retry
        )

        if response is False:
            raise QuantumError('Could not get fans by date for profile {}.'.format(project_id))

        return response

    def get_facebook_profiles_interactions_count_by_date(self, project_id, since, until, ids, timezone='UTC', retry=3):
        """
        /accounts/{account_id}/projects/{project_id}/facebook/profiles/interactions/count/date?
            since={start_date}
            until={end_date}
            ids={fanpages}
            timezone={timezone}
        """
        args = locals()
        params = {param: args[param] for param in ['since', 'until', 'ids', 'timezone']}
        response = self._query(
            method = 'GET',
            path   = '/accounts/{}/projects/{}/facebook/profiles/interactions/count/date'.format(self.account_id, project_id),
            params = params,
            retry  = retry
        )

        if response is False:
            raise QuantumError('Could not get fans by date for profile {}.'.format(project_id))

        return response

    def get_facebook_profiles_posts_count_by_date(self, project_id, since, until, ids, owner=None, type=None, timezone='UTC', retry=3):
        """
        /accounts/{account_id}/projects/{project_id}/facebook/profiles/posts/count/date?
            since={start_date}
            until={end_date}
            ids={posts}
            owner={owner}
            type={type}
            timezone={timezone}
        """
        args = locals()
        params = {param: args[param] for param in ['since', 'until', 'ids', 'owner', 'type', 'timezone']}
        response = self._query(
            method = 'GET',
            path   = '/accounts/{}/projects/{}/facebook/profiles/posts/count/date'.format(self.account_id, project_id),
            params = params,
            retry  = retry
        )

        if response is False:
            raise QuantumError('Could not get post count by date for profile {}.'.format(project_id))

        return response

    def get_facebook_profiles_postinteractions_by_date(self, project_id, since, until, ids, timezone='UTC', retry=3):
        """
        /accounts/{account_id}/projects/{project_id}/facebook/profiles/posts-interactions/count/date?
            since={start_date}
            until={end_date}
            ids={posts}
            timezone={timezone}
        """
        args = locals()
        params = {param: args[param] for param in ['since', 'until', 'ids', 'timezone']}
        response = self._query(
            method = 'GET',
            path   = '/accounts/{}/projects/{}/facebook/profiles/posts-interactions/count/date'.format(self.account_id, project_id),
            params = params,
            retry  = retry
        )

        if response is False:
            raise QuantumError('Could not get post interactions for posts {}'.format(ids))

        return response

    def get_facebook_profiles_engagementrate_by_date(self, project_id, since, until, ids, timezone='UTC', retry=3):
        """
        /accounts/{account_id}/projects/{project_id}/facebook/profiles/engagement-rate/date?
            since={start_date}
            until={end_date}
            ids={fanpages}
            timezone={timezone}
        """
        args = locals()
        params = {param: args[param] for param in ['since', 'until', 'ids', 'timezone']}
        response = self._query(
            method = 'GET',
            path   = '/accounts/{}/projects/{}/facebook/profiles/engagement-rate/date'.format(self.account_id, project_id),
            params = params,
            retry  = retry
        )

        if response is False:
            raise QuantumError('Could not get engagement rate by date for profile {}.'.format(project_id))

        return response

    def get_twitter_profiles_tweets(self, project_id, profile_id, since, until, ids, owner=None, type=None, page=False, timezone='UTC', retry=3):
        """
        /accounts/{account_id}/projects/{project_id}/facebook/profiles/{profile_id}/tweets?
            since={start_date}
            until={end_date}
            ids={profiles}
            owner={owner}
            type={type}
            timezone={timezone}
        Get all tweets for a given profile and period
        """
        args = locals()
        params = {param: args[param] for param in ['since', 'until', 'ids', 'owner', 'type', 'timezone']}
        response = self._query(
            method = 'GET',
            path   = '/accounts/{}/projects/{}/twitter/profiles/{}/tweets'.format(self.account_id, project_id, profile_id),
            params = params,
            retry  = retry,
            page   = page
        )

        if response is False:
            raise QuantumError('Could not get tweets for profile {}.'.format(profile_id))

        return response

    def get_twitter_profiles_tweet_interactions(self, project_id, since, until, ids, timezone='UTC', retry=3):
        """
        /accounts/{account_id}/projects/{project_id}/twitter/profiles/tweet-interactions/count/date?
            since={start_date}
            until={end_date}
            ids={posts}
            timezone={timezone}
        Get post interactions for posts within a project
        """
        args = locals()
        params = {param: args[param] for param in ['since', 'until', 'ids', 'timezone']}
        response = self._query(
            method = 'GET',
            path   = '/accounts/{}/projects/{}/twitter/profiles/tweet-interactions/count/date'.format(self.account_id, project_id),
            params = params,
            retry  = retry
        )

        if response is False:
            raise QuantumError('Could not get tweet interactions for project {}.'.format(project_id))

        return response

    def _query(self, method, path, params=None, retry=0, page=False):
        if not path.startswith('/'):
            if six.PY2:
                path = '/' + six.text_type(path.decode('utf-8'))
            else:
                path = '/' + path

        params = {param: params[param] for param in params if params[param] is not None} if params is not None else None

        try:
            if page:
                return self._paginate(method, path, params)
            else:
                return self._request(method, path, params)[0]
        except QuantumPythonError:
            if retry:
                return self._query(method, path, params, retry - 1)
            else:
                raise

    def _paginate(self, method, path, params):
        while path:
            if urlparse(path)[4] != '':
                params = dict(parse_qsl(urlparse(path)[4]))
                path = urlparse(path)[2]

            result, path = self._request(method, path, params)

            yield result

    def _request(self, method, path, params):
        if params:
            for key in params:
                value = params[key]
            if isinstance(value, (list, dict, set)):
                params[key] = json.dumps(value)

        try:
            if method == 'GET':
                response = self.session.request(
                    method,
                    self.url + path,
                    params          = params,
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

        result = self._parse(response.content)

        try:
            next_url = result['paging']['next']
        except(KeyError, TypeError):
            next_url = None

        return result, next_url

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
