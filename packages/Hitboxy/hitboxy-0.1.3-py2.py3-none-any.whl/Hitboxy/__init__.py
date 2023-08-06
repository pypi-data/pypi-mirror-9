from __future__ import unicode_literals

__license__ = """
Copyright (c) 2015, David Ewelt <uranoxyd@gmail.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

__version__ = '0.1.3'

try:
    from httplib import HTTPConnection 
except ImportError:
    from http.client import HTTPConnection

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

import json
import logging
import random
import time
import datetime
import gzip
from StringIO import StringIO

API_HOSTNAME = 'api.hitbox.tv'

class ApiError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
        
class RequestForbiddenError(ApiError):
    def __init__(self, msg):
        ApiError.__init__(self, msg)        

class AuthFailedError(ApiError):
    def __init__(self, msg):
        ApiError.__init__(self, msg)
        
class AuthenticationNeededError(ApiError):
    def __init__(self):
        ApiError.__init__(self, 'Authentication-Token needed for this method. Call authenticate() before using.')
        
class EditorNotFoundError(ApiError):
    def __init__(self):
        ApiError.__init__(self, 'Editor not found.')

class HttpClient(object):
    def __init__(self, hostname='api.hitbox.tv'):
        self.hostname = hostname
    #-
    
    def _process_response(self, response, decode_json=True):
        if response.status != 200: return response.status, response.reason, None

        data = response.read()
        encoding = response.getheader('Content-Encoding', '')
        if encoding == 'gzip':
            buf = StringIO(data)
            with gzip.GzipFile(fileobj=buf) as fp:
                data = fp.read()
        
        if decode_json: data = json.loads(data)
        
        return response.status, response.reason, data
    #-
        

    def GET(self, path, query=None, decode_json=True):
        if not query is None and len(query) > 0:
            path += '?' + urlencode(query)
        
        c = HTTPConnection(self.hostname)
        c.request("GET", path)

        return self._process_response(c.getresponse(), decode_json)
    #-

    def PUT(self, path, body=None, query=None, decode_json=True):
        if not query is None and len(query) > 0:
            path += '?' + urlencode(query)
        
        c = HTTPConnection(self.hostname)
        c.request("PUT", path, body)
        
        return self._process_response(c.getresponse(), decode_json)
    #-

    def POST(self, path, data=None, query=None, decode_json=True):
        body = None
        if not data is None:
            body = json.dumps(data)
        if not query is None and len(query) > 0:
            path += '?' + urlencode(query)

        c = HTTPConnection(self.hostname)
        c.request("POST", path, body=body)

        return self._process_response(c.getresponse(), decode_json)
    #-
#-

class ApiClient(object):
    http = HttpClient()

    def __init__(self):
        self.auth_token = None
    #-

    def __str__(self):
        return "<Hitboxy(auth_token=%s)>" % self.auth_token
    
    #================================================================================================================================
    #== private methods
    #================================================================================================================================
    
    def _check_auth_token(self):
        if self.auth_token is None:
            raise AuthenticationNeededError() 
   
    #================================================================================================================================
    #== static methods
    #================================================================================================================================

    @staticmethod
    def get_auth_token(username, password, app='desktop'):
        """
            Get a Authentication-Token by submitting Hitbox username and password.
            
            :param str username: hitbox.tv username
            :param str password: hitbox.tv password
            
            :return: auth token
            :rtype: str
        """
        status, reason, data = ApiClient.http.POST('/auth/token', {'login': username, 'pass': password, 'app': app})
        if status != 200:
            raise AuthFailedError('Wrong status response from api: %s - %s' % (status, reason))
        if not 'authToken' in data:
            raise AuthFailedError("Bad response payload from api: key 'authToken' not found!")
        return data['authToken']
    #-

    @staticmethod
    def get_chat_servers():
        """
            Fetch a list of currently available chat servers.
            
            :return: List of server IPs/Hostnames. Example: ``[u'ec2-54-82-114-34.compute-1.amazonaws.com', u'ec2-54-211-95-56.compute-1.amazonaws.com', ...]``
            :rtype: list
        """
        status, reason, data = ApiClient.http.GET('/chat/servers', query={'redis':'true'})
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        return [ e['server_ip'] for e in data ] 
    #-

    #================================================================================================================================
    #== public methods
    #================================================================================================================================
    
    #--------------------------------------------------------------------------------------------------------------------------------
    #-- Authentication
    #--------------------------------------------------------------------------------------------------------------------------------

    def authenticate(self, username, password, app='desktop'):
        """
            Get a Authentication-Token by submitting Hitbox username and password.
            The token is saved in the ApiClient object for further use.
            If you just want a Authentication-Token use the ApiClient.get_auth_token static method instead.
            
            :param str username: hitbox.tv username
            :param str password: hitbox.tv password
            
            :return: auth token
            :rtype: str            
        """
        self.username = username
        self.auth_token = ApiClient.get_auth_token(username, password, app)
        return self.auth_token
    #-   

    def get_login_info(self):
        """
            Returns account information. (Needs authentication)
        """
        self._check_auth_token()
        status, reason, data = ApiClient.http.POST('/auth/login', {'authToken': self.auth_token})
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        return data
    #-    

    #--------------------------------------------------------------------------------------------------------------------------------
    #-- User
    #--------------------------------------------------------------------------------------------------------------------------------

    def get_user_info(self, username=None):
        """
            Get user account information.
            
            :param str username: hitbox.tv username or ``None`` to use the authenticated user
            :return: dict with user account information
            :rtype: dict 
        """
        query = None
        if username is None:
            self._check_auth_token()
            username = self.username
            query = {'authToken': self.auth_token}
        status, reason, data = ApiClient.http.GET('/user/%s' % username, query)
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        return data
    #-

    def _update_user_info(self, **kwargs):
        """
            Change user information. (not implemented / working for now!)
        """
        query = {'authToken': self.auth_token,
                 'user_name': self.username}
        query.update(kwargs)
        status, reason, data = ApiClient.http.PUT('/user/%s' % self.username, json.dumps(query))#, json.dumps(query), {'authToken': self.auth_token})
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        return data
    #-
       
    #--------------------------------------------------------------------------------------------------------------------------------
    #-- Games
    #--------------------------------------------------------------------------------------------------------------------------------
    
    def get_games(self, query=None, limit=None, live_only=False):
        """
            Get list of games.

            :param str query: search query
            :param int limit: limit the number of results to the given count. Pass ``None`` for no limit.
            :param bool live_only: show only games that are currently live

            :return: list of dict
            :rtype: list
        """
        http_query = {}
        if not query is None: http_query['q'] = query
        if not limit is None: http_query['limit'] = limit
        if live_only: http_query['liveonly'] = 'true'
        status, reason, data = ApiClient.http.GET('/games', http_query)
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        if not 'categories' in data:
            raise ApiError("Bad response payload from api: key 'livestream' not found!")
        """
            Example response:
            [
                {
                    u'category_channels': None,
                    u'category_id': u'427',
                    u'category_logo_large': u'/static/img/games/2302957-i2cs9uzmq4yua.jpg',
                    u'category_logo_small': None,
                    u'category_media_count': u'29',
                    u'category_name': u'Counter-Strike: Global Offensive',
                    u'category_name_short': None,
                    u'category_seo_key': u'counter-strike-global-offensive',
                    u'category_updated': u'2015-03-31 20:06:24',
                    u'category_viewers': u'7524'
                },
                ...
            ]
        """
        return data['categories']
    #-

    def get_top_games(self, query=None, limit=None):
        """
            Get list of games ordered by viewer count.
            
            :param str query: search query
            :param int limit: limit the number of results to the given count. Pass ``None`` for no limit.

            :return: list of dict
            :rtype: list
        """
        http_query = {}
        if not query is None: http_query['q'] = query
        if not limit is None: http_query['limit'] = limit
        status, reason, data = ApiClient.http.GET('/games/top', http_query)
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        if not 'categories' in data: return []
        return data['categories']
    #-

    def get_game_info(self, game):
        """
            Get details about a game.

            :param game: Game-ID or SEO-Key
            :type game: str or int
            :return: dict with game info or None if not found
        """
        query = None
        if type(game) == str: query = {'seo': 'true'} 
        status, reason, data = ApiClient.http.GET('/game/%s' % game, query)
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        if not 'category' in data: return None
        if len(data['category']) == 0: return None
        return data['category']
    #-

    #--------------------------------------------------------------------------------------------------------------------------------
    #-- Media
    #--------------------------------------------------------------------------------------------------------------------------------

    def get_livestream_info(self, channel):
        """
            Get stream information.
            
            :param str channel: Channel
            :return: dict with channel informations
            :rtype: dict

            :todo: first check the channels visibility to work around the 404 error!?
        """
        self._check_auth_token()
        status, reason, data = ApiClient.http.GET('/media/live/' + channel, {'authToken': self.auth_token})
        if status == 403:
            raise ApiError("Received '403 - Forbidden' from the API. Maybe you have sumbitted the wrong credentials for this channel.")
        if status == 404:
            raise ApiError("Received '404 - Not found' from the API. This can be happen when the channel is hidden.")        
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        if not 'livestream' in data:
            raise ApiError("Bad response payload from api: key 'livestream' not found!")
        return data['livestream']
    #-

    def get_livestream_list(self):
        """
            Get list of livestreams.
            
            :return: list of dict with informations about the active livestreams
            :rtype: list
        """
        status, reason, data = ApiClient.http.GET('/media/live/list')
        if status == 403:
            raise ApiError("Received '403 - Forbidden' from the API. Maybe you have sumbitted the wrong credentials for this channel.")
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        if not 'livestream' in data:
            raise ApiError("Bad response payload from api: key 'livestream' not found!")
        return data['livestream']
    #-    

    #--------------------------------------------------------------------------------------------------------------------------------
    #-- Editors
    #--------------------------------------------------------------------------------------------------------------------------------

    def get_channel_editors(self, channel):
        """
            Returns list of editors of a channel. (Needs authentication)
            
            :param str channel: Channel
            
            :return: list of dict with details about the channel editors
            :rtype: list
        """
        self._check_auth_token()
        status, reason, data = ApiClient.http.GET('/editors/' + channel, {'authToken': self.auth_token})
        if status == 403:
            raise ApiError("Received '403 - Forbidden' from the API. Maybe you have sumbitted the wrong credentials for this channel.")
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        if not 'list' in data:
            raise ApiError("Bad response payload from api: key 'list' not found!")
        return data['list']
    #-

    def get_editor_channels(self, username):
        """
            Returns list of channels a user is a editor in. (Needs authentication)
            
            :param str username: Username 
            
            :return: List of dict with details about the channel a user is a editor in
        """
        self._check_auth_token()
        status, reason, data = ApiClient.http.GET('/editor/' + username, {'authToken': self.auth_token})
        if status == 403:
            raise ApiError("Received '403 - Forbidden' from the API. Maybe you have sumbitted the wrong credentials for this channel.")
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        if not 'list' in data:
            raise ApiError("Bad response payload from api: key 'list' not found!")
        return data['list']
    #-

    def add_channel_editor(self, channel, username):
        """
            Adds an editor to a channel. (Needs authentication)
            
            :param str channel: Channel
            :param str username: Username of the editor
            
            :return: ``True`` if success (even on duplicate), ``False`` if not
            :rtype: bool
            
            :raise RequestForbiddenError: If the http api returns status code 403. This can happen if you submit the wrong credentials for the given channel.
            :raise ApiError: If the http api returns a status code other than 200
        """
        self._check_auth_token()
        status, reason, data = ApiClient.http.POST('/editors/' + channel, {
            'authToken': self.auth_token,
            'user_name': self.username,
            'editor': username,
            'remove': False
        }, decode_json=False)
        if status == 403:
            raise RequestForbiddenError("Received '403 - Forbidden' from the API. Maybe you have sumbitted the wrong credentials for this channel.")
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        if data == 'editor_not_found': raise EditorNotFoundError()
        return data == 'success'
    #-

    def remove_channel_editor(self, channel, username):
        """
            Remove a editor from a channel. (Needs authentication)
            
            :param str channel: Channel
            :param str username: Username of the editor to remove
            
            :return: ``True`` if the user was removed or ``False`` if not (not 100% sure)

            :raise RequestForbiddenError: If the http api returns status code 403. This can happen if you submit the wrong credentials for the given channel.   
        """
        self._check_auth_token()
        status, reason, data = ApiClient.http.POST('/editors/' + channel, {
            'authToken': self.auth_token,
            'user_name': self.username,
            'editor': username,
            'remove': True
        }, decode_json=False)
        if status == 403:
            raise RequestForbiddenError("Received '403 - Forbidden' from the API. Maybe you have sumbitted the wrong credentials for this channel.")
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        if data == 'editor_not_found': raise EditorNotFoundError()        
        return data == 'success'
    #-

    #--------------------------------------------------------------------------------------------------------------------------------
    #-- Channels
    #--------------------------------------------------------------------------------------------------------------------------------

    def get_channel_status(self, channel):
        """
            :todo: documentation ;)
        """
        status, reason, data = ApiClient.http.GET('/media/status/' + channel)
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        return data
    #-

    def get_channel_total_views(self, channel):
        """
            :todo: documentation ;)
        """
        status, reason, data = ApiClient.http.GET('/media/views/' + channel)
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        if not 'total_live_views' in data:
            raise ApiError("Bad response payload from api: key 'total_live_views' not found!")        
        return data['total_live_views']
    #-

    def get_channel_hosters(self, channel):
        """
            Returns channels hosting your stream. (Needs authentication)
            
            :param str channel: Channel 
            
            :return: List of dictionaries with 'user_logo' and 'user_name' of the channels
        """
        self._check_auth_token()
        status, reason, data = ApiClient.http.GET('/hosters/' + channel, {'authToken': self.auth_token})
        if status == 403:
            raise ApiError("Received '403 - Forbidden' from the API. Maybe you have sumbitted the wrong credentials for this channel.")
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        if not 'hosters' in data:
            raise ApiError("Bad response payload from api: key 'hosters' not found!")
        return data['hosters']
    #-

    def get_channel_followers(self, channel, offset=None, limit=None, reverse=False):
        """
            Get a list of followers for a channel.
            
            :param str channel: Channel
            :param offset: Offsets the results by the provided number
            :type offset: int or None 
            :param limit: Limits the results to provided number
            :type limit: int or None 
            :param bool reverse: Reverse the order of the results 
        """
        query = {}
        if not offset is None: query['offset'] = offset
        if not limit is None and not limit == -1: query['limit'] = limit
        if reverse: query['reverse'] = 'true'
        status, reason, data = ApiClient.http.GET('/followers/user/' + channel, query)
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        if not 'followers' in data:
            raise ApiError("Bad response payload from api: key 'list' not found!")
        return data['followers']
    #-

    def get_channel_media_key(self, channel):
        """
            Returns stream key of a channel. (Needs authentication)
            
            :param str channel: Channel 
            :return: Stream key of channel.
            :rtype: str
        """
        self._check_auth_token()
        status, reason, data = ApiClient.http.GET('/mediakey/' + channel, {'authToken': self.auth_token})
        if status == 403:
            raise ApiError("Received '403 - Forbidden' from the API. Maybe you have sumbitted the wrong credentials for this channel.")
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        if not 'streamKey' in data:
            raise ApiError("Bad response payload from api: key 'hosters' not found!")
        return data['streamKey']
    #-

    def reset_channel_media_key(self, channel):
        """
            Resets the stream key of a channel. (Needs authentication)
            
            :param str channel: Channel 
            :return: New stream key of channel.
            :rtype: str
        """
        self._check_auth_token()
        status, reason, data = ApiClient.http.PUT('/mediakey/' + channel, query={'authToken': self.auth_token})
        if status == 403:
            raise ApiError("Received '403 - Forbidden' from the API. Maybe you have sumbitted the wrong credentials for this channel.")
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        if not 'streamKey' in data:
            raise ApiError("Bad response payload from api: key 'hosters' not found!")
        return data['streamKey']
    #-

    def commercial_break(self, channel, count=1):
        """
            Starts a commercial break. (Needs authentication)
            
            This command is at the moment not very good in usage. It blocks for a while an then returns a '504 - Gateway Time-out'
            
            :param str channel: Channel to run the commercial break on.
            :param int count: Number of spots to show.
        """
        self._check_auth_token()
        status, reason, data = ApiClient.http.POST('/ws/combreak/%s/%s' % (channel, count), {'authToken': self.auth_token})
        if status == 403:
            raise ApiError("Received '403 - Forbidden' from the API. Maybe you have sumbitted the wrong credentials for this channel.")
        if status != 200:
            raise ApiError('Wrong status response from api: %s - %s' % (status, reason))
        return data
    #-
#-