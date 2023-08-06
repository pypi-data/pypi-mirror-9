# Copyright (c) 2015, OLogN Technologies AG. All rights reserved.
#
# Redistribution and use of this file in source and compiled
# forms, with or without modification, are permitted
# provided that the following conditions are met:
#     * Redistributions in source form must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in compiled form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the OLogN Technologies AG nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL OLogN Technologies AG BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE

import json
import os.path
from copy import deepcopy

from twisted.python.filepath import FilePath
from twisted.python.util import sibpath

from smartanthill.exception import ConfigKeyError
from smartanthill.util import load_config, merge_nested_dicts, singleton


def get_baseconf():
    return load_config(sibpath(__file__, "config_base.json"))


@singleton
class ConfigProcessor(object):

    def __init__(self, wsdir, user_options):
        self.wsconfp = FilePath(os.path.join(wsdir, "smartanthill.json"))

        self._data = get_baseconf()
        self._wsdata = {}
        self._process_workspace_conf()
        self._process_user_options(user_options)

    def _process_workspace_conf(self):
        if (not self.wsconfp.exists() or not
                self.wsconfp.isfile()):  # pragma: no cover
            return
        self._wsdata = load_config(self.wsconfp.path)
        self._data = merge_nested_dicts(self._data, deepcopy(self._wsdata))

    def _process_user_options(self, options):
        assert isinstance(options, dict)
        for k, v in options.iteritems():
            _dyndict = v
            for p in reversed(k.split(".")):
                _dyndict = {p: _dyndict}
            self._data = merge_nested_dicts(self._data, _dyndict)

    def _write_wsconf(self):
        with open(self.wsconfp.path, "w") as f:
            json.dump(self._wsdata, f, sort_keys=True, indent=2)

    def __contains__(self, key):
        try:
            self.get(key)
            return True
        except:
            return False

    def get(self, key_path, default=None):
        try:
            value = self._data
            for k in key_path.split("."):
                value = value[k]
            return value
        except KeyError:
            if default is not None:
                return default
            else:
                raise ConfigKeyError(key_path)

    def update(self, key_path, data, write_wsconf=True):
        newdata = data
        for k in reversed(key_path.split(".")):
            newdata = {k: newdata}

        self._data = merge_nested_dicts(self._data, deepcopy(newdata))
        self._wsdata = merge_nested_dicts(self._wsdata, newdata)

        if write_wsconf:
            self._write_wsconf()

    def delete(self, key_path, write_wsconf=True):
        if "." in key_path:
            _parts = key_path.split(".")
            _parent = ".".join(_parts[:-1])
            _delkey = _parts[-1]

            # del from current session
            del self.get(_parent)[_delkey]

            # del from workspace
            _tmpwsd = self._wsdata
            for k in _parent.split("."):
                _tmpwsd = _tmpwsd[k]
            del _tmpwsd[_delkey]
        else:
            del self._data[key_path]
            del self._wsdata[key_path]

        if write_wsconf:
            self._write_wsconf()
