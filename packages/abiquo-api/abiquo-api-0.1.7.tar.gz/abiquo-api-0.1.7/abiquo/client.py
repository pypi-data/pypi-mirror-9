# Copyright (C) 2008 Abiquo Holdings S.L.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests

class Abiquo(object):
    def __init__(self, url, auth=None, headers=None):
        self.url = url
        self.auth = auth
        self.headers = {url : headers}
        self.session = requests.session()

    def __getattr__(self, key):
        try:
            return self.__dict__[key]
        except:
            self.__dict__[key] = Abiquo(self._join(self.url, key), auth=self.auth)
            return self.__dict__[key]

    def __call__(self, *args):
        if not args:
            return self
        return Abiquo(self._join(self.url, *[str(i) for i in args]), auth=self.auth)

    def get(self, id=None, params=None, headers=None):
        return self._request('get', self._join(self.url, id), 
            params=params, headers=headers)

    def post(self, id=None, params=None, headers=None, data=None):
        return self._request('post', self._join(self.url, id), 
            params=params, headers=headers, data=data)

    def put(self, id=None, params=None, headers=None, data=None):
        return self._request('put', self._join(self.url, id), 
            params=params, headers=headers, data=data)

    def delete(self, id=None, params=None, headers=None):
        return self._request('delete', self._join(self.url, id), 
            params=params, headers=headers)        

    def _request(self, method, url, params=None, headers=None, data=None):
        parent_headers = self.headers[url] if url in self.headers else {}
        response = self.session.request(method, 
                                        url, 
                                        auth=self.auth, 
                                        params=params, 
                                        data=data,
                                        headers=self._merge_dicts(parent_headers, headers))
        response_dto = None
        if len(response.text) > 0:
            try:
                response_dto = ObjectDto(response.json(), auth=self.auth, 
                    content_type=response.headers.get('content-type', None))
            except ValueError:
                pass
        return response.status_code, response_dto

    def _merge_dicts(self, x, y):
        new_dict = {}
        if x:
            new_dict.update(x)
        if y:
            new_dict.update(y)
        return new_dict

    def _join(self, *args):
        return "/".join(filter(None, args))

class ObjectDto(object):
    def __init__(self, json, auth=None, content_type=None):
        self.json = json
        self.auth = auth
        self.content_type = content_type

    def __getattr__(self, key):
        try:
            return self.__dict__[key]
        except KeyError as ex:
            return self._find_or_raise(key, ex)
            
    def _find_or_raise(self, key, ex):
        try:
            return self.json[key]
        except KeyError:
            try:
                return self.follow(key)
            except:
                raise ex

    def follow(self, rel):
        link = self._extract_link(rel)
        if not link:
            raise KeyError("link with rel %s not found" % rel)
        return Abiquo(url=link['href'], auth=self.auth, headers={'accept' : link['type']})

    def __len__(self):
        try:
            if 'totalSize' in self.json:
                return self.json['totalSize']
            return len(self.json['collection'])
        except KeyError:
            raise TypeError('object has no len()')

    def __iter__(self):
        try:
            for json in self.json['collection']:
                yield ObjectDto(json, auth=self.auth)

            current_page = self
            while current_page._has_link('next'):
                link = self._extract_link('next')
                client = Abiquo(url=link['href'], 
                                auth=self.auth, 
                                headers={'Accept' : link.get('type', self.content_type)})
                sc, current_page = client.get()
                if sc == 200 and current_page:
                    for json in current_page.json['collection']:
                        yield ObjectDto(json, auth=self.auth)
        except KeyError:
            raise TypeError('object is not iterable')

    def __dir__(self):
        return dir(type(self)) + self.json.keys()

    def _extract_link(self, rel):
        return next((link for link in self.json['links'] if link['rel'] == rel), None)

    def _has_link(self, rel):
        return True if self._extract_link(rel) else False