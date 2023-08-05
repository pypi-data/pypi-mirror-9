# This client is designed to easily interact with Webmetrics' API.
# Copyright (C) 2014  Shane Barbetta
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
__author__ = 'Shane Barbetta'

import urllib, urllib2, base64, hashlib, time, json

# store the URL and signature as state

class ApiConnection:
    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key
        self.base_url = 'https://api.webmetrics.com/v2/?'
        
    # Authentication
    def _auth(self):
        timestamp = str(int(time.time()))
        return base64.b64encode(hashlib.sha1(self.username + self.api_key + timestamp).digest())

    # Requests
    # Methods for accessing the API using Python's native urllib2
    # libraries.
    def get(self, method, retry=True):
        return self._do_call(method, retry)
        
    def _refresh(self, method):
        return self._do_call(method, False)

    def _do_call(self, method, retry):
        base_query = { 'username' : self.username, 'sig' : self._auth(), 'format' : 'json' }
        base_query.update(method)
        request = self.base_url + urllib.urlencode(base_query, doseq=True)
        # For debugging if needed
        # print request
        response = urllib2.urlopen(request)
        data = json.load(response)
        time.sleep(3)
        # Retry once by default unless specified. Some methods
        # that return larger amounts of data have high rate limits.
        if data is not None and data['stat'] == 'fail' and retry is True:
            return self._refresh(method)
        else:
            return data