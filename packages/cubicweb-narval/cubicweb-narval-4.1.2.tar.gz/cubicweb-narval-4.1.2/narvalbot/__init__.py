# copyright 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""narval bot configuration"""

__docformat__ = "restructuredtext en"

import sys
import os, os.path as osp
import logging
from ConfigParser import ConfigParser
import hmac
try:
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    pass
import requests
from datetime import datetime
from hashlib import md5
from urlparse import urlparse

from logilab.common.configuration import Configuration, Method
from logilab.common.logging_ext import set_log_methods
from logilab.common.textutils import (splitstrip, apply_units, text_to_dict,
                                      TIME_UNITS, BYTE_UNITS)

NARVAL_SOFTWARE_ROOT = __path__[0]

if 'cubes.narval' in __name__:
    MODE = 'dev'
else:
    MODE = 'installed'

def _find_prefix(start_path=NARVAL_SOFTWARE_ROOT):
    """Runs along the parent directories of *start_path* (default to
    narval source directory) looking for one containing a
    'share/narval' directory.

    The first matching directory is assumed as the prefix installation
    of the narval bot

    Returns the matching prefix or None.
    """
    prefix = start_path
    old_prefix = None
    if not osp.isdir(start_path):
        prefix = osp.dirname(start_path)
    while (not osp.isdir(osp.join(prefix, 'share', 'narval'))
          or prefix.endswith('.egg')) and prefix != old_prefix:
        old_prefix = prefix
        prefix = osp.dirname(prefix)
    if osp.isdir(osp.join(prefix, 'share', 'narval')):
        return prefix
    return sys.prefix

try:
    INSTALL_PREFIX = os.environ['NARVAL_INSTALL_PREFIX']
except KeyError:
    INSTALL_PREFIX = _find_prefix()

class ConfigurationError(Exception):
    """a misconfiguration error"""

def options_dict(strvalue):
    options = text_to_dict(strvalue)
    for option in (u'max-cpu-time', u'max-reprieve', u'max-time'):
        if option in options:
            options[option] = apply_units(options[option], TIME_UNITS)
    if u'max-memory' in options:
        options[u'max-memory'] = apply_units(options[u'max-memory'],
                                             BYTE_UNITS)
    return options

class NarvalConfiguration(Configuration):
    options = (
        # main options
        ('uid',
         {'type' : 'string',
          'default': None,
          'help': 'if this option is set, use the specified user to start \
the daemon rather than the user running the command',
          'group': 'main', 'level': 1,
          }),

        # process control
        ('threads',
         {'type' : 'int', 'short': 'T',
          'default': 2,
          'help': 'number of plans which may be run in parallel',
          'group': 'process-control', 'level': 2,
          }),
        ('max-cpu-time',
         {'type' : 'time',
          'default': None,
          'help': 'maximum CPU Time in second that may be used to execute a test.',
          'group': 'process-control', 'level': 2,
          }),
        ('max-time',
         {'type' : 'time',
          'default': None,
          'help': 'maximum Real Time in second that may be used to execute a test.',
          'group': 'process-control', 'level': 2,
          }),
        ('max-memory',
         {'type' : 'bytes',
          'default': None,
          'help': 'maximum Memory in bytes the test can allocate.',
          'group': 'process-control', 'level': 2,
          }),
        ('max-reprieve',
         {'type' : 'time',
          'default': 60,
          'help': 'delay in second while the test try to abort nicely (reporting '
          'the error and cleaning up the environement before it\'s killed).',
          'group': 'process-control', 'level': 2,
          }),

        # server control
        ('log-file',
         {'type' : 'string',
          'default': Method('_log_file'),
          'help': 'file where output logs should be written',
          'group': 'daemon', 'level': 2,
          }),
        ('log-threshold',
         {'type' : 'string', # XXX use a dedicated type?
          'default': 'INFO',
          'help': 'narval bot\'s log level',
          'group': 'daemon', 'level': 1,
          }),
        ('poll-delay',
         {'type' : 'time',
          'default': 60,
          'help': 'delay in seconds while the server waits before looking for '
          'new pending plans ',
          'group': 'daemon', 'level': 2,
          }),
        )

    def __init__(self):
        Configuration.__init__(self)
        self.load_file_configuration(self.configuration_file)
        self.cnx_infos = connection_infos()

    if MODE == 'dev':
        _default_conf_file = osp.expanduser('~/etc/narval/narval.ini')
        _default_pid_file = '/tmp/narval.pid'
        _default_log_file = '/tmp/narval.log'
    else:
        _default_conf_file = '/etc/narval/narval.ini'
        _default_pid_file = '/var/run/narval/narval.pid'
        _default_log_file = '/var/log/narval/narval.log'

    @property
    def configuration_file(self):
        return os.environ.get('NARVALRC', self._default_conf_file)

    def _pid_file(self):
        return self._default_pid_file

    def _log_file(self):
        return self._default_log_file

    def cnxh(self, instance_id):
        return HTTPConnectionHandler(instance_id)


if MODE == 'dev':
    _DEFAULT_SOURCES_FILE = osp.expanduser('~/etc/narval/narval-cw-sources.ini')
else:
    _DEFAULT_SOURCES_FILE = '/etc/narval/narval-cw-sources.ini'

_CW_SOURCES_FILE = os.environ.get('NARVALSOURCES', _DEFAULT_SOURCES_FILE)

def connection_infos():
    if osp.exists(_CW_SOURCES_FILE):
        config = ConfigParser()
        config.read(_CW_SOURCES_FILE)
        data_sources = {}
        for section in config.sections():
            data_sources[section] = dict(config.items(section))
        return data_sources
    return {}



class HTTPConnectionHandler(object):
    """handle connection to a cubicweb repository"""
    check_ssl = None

    def __init__(self, instance_id):
        if not instance_id:
            raise ConfigurationError('you must specify main cubicweb instance '
                                     'identifier in the configuration file or using '
                                     'the --cw-inst-id option')
        self.instance_id = instance_id
        self.cnxinfo = connection_infos().get(instance_id, {})
        self.instance_url = self.cnxinfo['url']
        if not self.instance_url.endswith('/'):
            self.instance_url += '/'
        self.token_id = self.cnxinfo.get('token_id')
        self.token = self.cnxinfo.get('secret')
        if self.cnxinfo.get('verify_ssl', '').lower() in ('false', 'no', '0'):
            self.check_ssl = False

    def http_get(self, url, **params):
        """GET the url and return interpreted json data"""
        return self.http_post(url, method='get', **params)

    def http_post(self, url, method='post', files=None, data=None, **params):
        """POST the url with given form parameters and files
        Keyword arguments:
        url -- url to connect to
        data -- raw data or dict containing form parameters {'key': 'value'}
        files -- files to upload {'formparam': ('filename', file_object )}
        params -- url encoded key/values pairs

        data can be raw if no file is provided otherwise it must be a
        dictionary, which will be appended as multipart content to the body.
        """
        self.debug('send HTTP %s %s params=%s, data=%s'%(method.upper(), url, params, data))
        _cw_fields = params.keys()
        if files:
            _cw_fields += files.keys()
        headers = {
                 'Accept': 'application/json',
                 'Date': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}
        if 'vid' in _cw_fields:
            _cw_fields.remove('vid')
        if _cw_fields:
            params['_cw_fields'] = ','.join(_cw_fields)
        try:
            r = requests.request(method, url, headers=headers,
                                 params=params, data=data, files=files, auth=self.auth,
                                 verify=self.check_ssl)
            r.raise_for_status()
        except requests.ConnectionError as e:
            self.warning('Cannot perform HTTP request: %s', e)
            return None
        try:
            return r.json()
        except ValueError as e:
            self.warning('Cannot perform HTTP request %s' % (e, ))
            self.warning('Request was url=%s, method=%s, header=%s, params=%s' %
                         (url, method, r.request.headers, params,))
            self.debug('HTTP Response: %s' % (repr(r.content),))
            return None
        except TypeError:
            # Response.json is a property in old python-requests
            return r.json

    def auth(self, req):
        if req.method in ('PUT', 'POST'):
            req.headers['Content-MD5'] = md5(req.body or '').hexdigest()
        req.headers['Authorization'] = 'Cubicweb %s:%s' % (self.token_id, self.sign(req))
        return req

    def sign(self, req):
        """Compute and return a signature for req using our secret token
        Sign the request data as expected by the signedrequest cube.
        """
        headers_to_sign = ('Content-MD5', 'Content-Type', 'Date')
        method = req.method
        url = req.url
        get_header = lambda field: req.headers.get(field, '')
        to_sign = method + url + ''.join(map(get_header, headers_to_sign))
        return hmac.new(self.token, to_sign).hexdigest()

    def pending_plans(self):
        return self.http_get(self.instance_url, vid='narval.pending-plans') or ()

    def plan(self, eid):
        url = self.instance_url + str(eid)
        data = self.http_get(url, vid='ejsonexport')
        if not len(data) == 1:
            raise Exception('expected one plan, got %s' % len(data))
        plan = data[0] # you get a list of plan of size 1
        return plan

LOGGER = logging.getLogger('narval.bot')
set_log_methods(HTTPConnectionHandler, LOGGER)

