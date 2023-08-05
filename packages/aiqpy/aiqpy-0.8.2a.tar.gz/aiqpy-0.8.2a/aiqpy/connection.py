import requests
import json
import six

from .exceptions import (
    ConnectionError, OrganizationNotFoundException, LoginError,
    MalformedURLException, MissingEndpointException,
    PlatformException, PlatformResponseException
)


class Connection(object):
    """Represents a connection to the AIQ8 platform"""
    def __init__(self,
                 username=None,
                 password=None,
                 organization=None,
                 platform=None,
                 profile=None,
                 organization_to_manage=None,
                 scope='admin'):

        self.__scope = scope
        self.__session_expires = 0
        self.__organization_to_manage = organization_to_manage
        self.__link_cache = {}
        self.__token_type = None
        self.__access_token = None

        if profile:
            import os.path
            import codecs
            profiles = {}

            if os.path.isfile(os.path.expanduser('~/.aiqpy_profiles')):
                profiles.update(json.load(
                    open(os.path.expanduser('~/.aiqpy_profiles'))
                ))

            if os.path.isfile('.aiqpy_profiles'):
                profiles.update(json.load(open('.aiqpy_profiles')))

            if profile not in profiles:
                raise LoginError('Profile "%s" not found' % profile)

            profile_data = profiles[profile]

            required_keys = ('username',
                             'password',
                             'organization',
                             'platform')

            if not all([key in profile_data.keys() for key in required_keys]):
                raise LoginError('Incorrect profile. Required fields: ' +
                                 ', '.join(required_keys))

            # Add the profile data to the object as private variables.
            for (key, value) in six.iteritems(profile_data):
                setattr(self, '_'+self.__class__.__name__+'__'+key, value)

            password_decoder = codecs.getencoder("rot-13")
            self.__password = password_decoder(profile_data['password'])[0]
        elif username and password and organization:
            self.__username = username
            self.__password = password
            self.__organization = organization
            self.__platform = platform
            self.__scope = scope
        else:
            raise LoginError('You need to provide username, password, ' +
                             'organization and platform or a profile')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, value, traceback):
        self.logout()

    def __generate_cachekey(self, key):
        return self.active_organization + ':' + key

    @property
    def username(self):
        return self.__username

    @property
    def active_organization(self):
        if self.__organization_to_manage:
            return self.__organization_to_manage
        return self.__organization

    def __build_url(self, endpoint=None, organization=None):
        try:
            from urllib.parse import urljoin
        except ImportError:
            from urlparse import urljoin

        # Because you know, I'm all about that baseurl,
        # 'bout that baseurl, no trebleurl
        baseurl = "%s/api/" % self.__platform

        if not endpoint:
            selected_organization = organization if organization \
                else self.active_organization
            endpoint = '?orgName=%s' % selected_organization

        return urljoin(baseurl, endpoint)

    def logout(self):
        """Terminates the session on the platform"""
        if not self.__logged_in():
            return True

        self.__organization_to_manage = None
        response = self.post(['logout'], {})
        if response.status_code != 204:
            raise PlatformException(response.status_code, response.text)

        self.__session_expires = 0

    def __logged_in(self):
        """Determines if there is an active connection to the platform"""
        from time import time
        return time() < self.__session_expires

    def login(self):
        """Attempts to create a connection to the platform"""
        platform_url = self.__build_url(organization=self.__organization)

        try:
            link_request = requests.get(platform_url)
        except (requests.exceptions.MissingSchema,
                requests.exceptions.InvalidSchema):
            raise MalformedURLException('Invalid schema')
        except requests.exceptions.RequestException:
            raise ConnectionError('Unable to connect to the platform')

        if link_request.status_code == 404:
            raise OrganizationNotFoundException()
        elif link_request.status_code != 200:
            raise PlatformException(link_request.status_code,
                                    link_request.text)

        org_data = link_request.json()
        if 'links' not in org_data or 'token' not in org_data['links']:
            raise PlatformResponseException('Missing link data in ' +
                                            'response from platform')

        auth_data = {
            'grant_type': 'password',
            'scope': self.__scope,
            'username': self.__username,
            'password': self.__password
        }

        if hasattr(self, '__auth_params'):
            auth_data.update(self.__auth_params)

        if "device" in self.__scope:
            import sys
            import uuid
            context = {
                'com.appearnetworks.aiq.device': {
                    'os': 'Python',
                    'osVersion': '.'.join(map(str, sys.version_info[0:3])),
                    'clientLibVersion': '0.1 alpha',
                    'clientVersion': '8.1.0.1 alpha',
                    'jsApiLevel': 6
                }
            }

            auth_data['x-deviceId'] = str(uuid.getnode())
            auth_data['x-context'] = json.dumps(context)

        auth_request = requests.post(org_data['links']['token'],
                                     data=auth_data)

        if auth_request.status_code == 400:
            raise LoginError('Incorrect username, password ' +
                             ' or insufficient permissions')
        elif auth_request.status_code != 200:
            raise PlatformException(auth_request.status_code,
                                    auth_request.text)

        auth_data = auth_request.json()

        self.__access_token = auth_data['access_token']
        self.__token_type = auth_data['token_type']

        from time import time
        self.__session_expires = time() + auth_data['expires_in']

        for (key, link) in auth_data['links'].items():
            self.__link_cache[self.__generate_cachekey(key)] = link

    def __get_link(self, resource_path):
        """Resolves a URL through the AIQ8 API Menu structure

        :param resource_path: A path of endpoints to resolve"""
        cachekey = self.__generate_cachekey(resource_path[-1])
        if cachekey in self.__link_cache:
            return self.__link_cache[cachekey]

        next_link = self.__build_url()

        while resource_path:
            data = self.get(next_link)
            for (key, link) in six.iteritems(data['links']):
                self.__link_cache[self.__generate_cachekey(key)] = link
            if resource_path[0] in data['links']:
                next_link = data['links'][resource_path[0]]
            else:
                raise MissingEndpointException('Missing endpoint')
            resource_path = resource_path[1:]

        return next_link

    def set_organization(self, new_organization):
        """Changes the active organization

        :param new_organization: The new organization as a string"""
        org_url = self.__build_url(organization=new_organization)

        try:
            response = self.get(org_url)
        except PlatformException as e:
            if e.http_status == 404:
                raise OrganizationNotFoundException('No such organization')
            else:
                raise

        self.__organization_to_manage = new_organization

    def __do_request(self,
                     method,
                     endpoint,
                     entity=None,
                     content_type='application/json',
                     files=None):
        """Performs a request against the platform.

        :param method: The HTTP method to use
        :param endpoint: The endpoint to call
        :param entity: Any data to request/send to the server
        :param content_type: The type of data to send to the server
        :param files: Any files for upload to the server
        """
        if not self.__logged_in():
            self.login()

        if isinstance(endpoint, six.string_types):
            resource_link = endpoint
        else:
            resource_link = self.__get_link(endpoint)

        request_url = self.__build_url(resource_link)

        if not method == 'post':
            if isinstance(entity, six.string_types):
                request_url += '/'+entity
            elif isinstance(entity, dict) and '_id' in entity:
                request_url += '/'+entity['_id']

        if files:
            data = files
        elif content_type == 'application/json':
            data = json.dumps(entity)
        else:
            data = entity

        headers = {
            'Authorization': self.__token_type+' '+self.__access_token,
            'Content-Type': content_type
        }

        request_method = getattr(requests, method)

        response = request_method(request_url, headers=headers, data=data)
        if 200 <= response.status_code < 300:
            if 'Content-Type' in response.headers and \
                    response.headers['Content-Type'] == 'application/json':
                return response.json()
            else:
                return response
        else:
            raise PlatformException(response.status_code, response.text)

    def get(self, endpoint, entity=None, **filters):
        """Sends a GET request to the platform. Returns the response from the server

        :param endpoint: The endpoint to use
        :param entity: The entity to request
        :param **filters: Filters to apply to the request
        """
        match_doc = lambda doc, conditions: \
            all(key in doc for key in conditions.keys()) \
            and all([doc[field] == value for field, value
                    in six.iteritems(conditions)])

        results = self.__do_request('get', endpoint, entity)
        if not filters:
            return results
        else:
            return [r for r in results if match_doc(r, filters)]

    def post(self, endpoint, entity):
        """Sends a POST request to the platform. Returns the response from the server

        :param endpoint: The endpoint to use
        :param entity: The entity to send to the platform
        """
        return self.__do_request('post', endpoint, entity)

    def put(self,
            endpoint,
            entity=None,
            content_type='application/json',
            files=None):
        """Sends a PUT request to the platform. Returns the response from the server

        :param endpoint: The endpoint to use
        :param entity: The entity to send to the platform
        :param content_type: The content type of send to the platform
        """
        return self.__do_request('put', endpoint, entity, content_type, files)

    def delete(self, endpoint, entity):
        """Sends a DELETE request to the platform. Returns the response
        from the server

        :param endpoint: The endpoint to use
        :param entity: The entity to remove
        """
        return self.__do_request('delete', endpoint, entity)
