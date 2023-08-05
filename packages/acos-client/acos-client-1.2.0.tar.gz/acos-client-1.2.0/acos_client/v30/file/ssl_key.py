# Copyright 2015,  Tobit Raff,  A10 Networks.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import acos_client.errors as acos_errors
import acos_client.v30.base as base


class SSLKey(base.BaseV30):

    url_prefix = '/file/ssl-key/'

    def get(self, file):
        return self._get(self.url_prefix + file)

    def exists(self, file):
        try:
            self.get(file)
            return True
        except acos_errors.NotFound:
            return False

    def _set(self, file=None, cert=None, size=None, action=None, update=False,
             **kwargs):

        obj_params = {
            "file": file,
            "size": size,
            "file-handle": file,
            "action": action,
        }

        kwargs['params'] = {'ssl-key': {}}

        for key, val in obj_params.iteritems():
            if val is not None:
                kwargs['params']['ssl-key'][key] = val

        if not update:
            file = ''

        return self._post(self.url_prefix + file, file_name=obj_params["file"],
                          file_content=cert, **kwargs)

    def create(self, file=None, cert=None, size=None, action=None,
               update=False):
        if self.exists(file):
            raise acos_errors.Exists

        self._set(file, cert, size, action, update=False)

    def update(self, file=None, cert=None, size=None, action=None,
               update=False):
        self._set(file, cert, size, action, update=True)

    def delete(self, file):
        self._delete(self.url_prefix + file)
