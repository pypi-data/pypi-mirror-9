# -*- coding: utf8 -*-

import zlib
from hashlib import md5

import requests
import simplejson as json
from requests.exceptions import (ConnectionError, HTTPError, RequestException, Timeout,
                                 TooManyRedirects)

from whale_agent.core.exceptions import AgentException
from whale_agent.core.exceptions.check import CheckException
from whale_agent.emitter import BaseEmitter


class HttpEmitter(BaseEmitter):

    def emit(self, payload):
        url = self.config.get('emit_url')
        api_key = self.config.get('api_key')

        self.log.debug('attempting postback to %s.' % url)

        try:
            message = json.dumps(payload)
        except UnicodeDecodeError:
            payload = self.remove_control_chars(payload)
            message = json.dumps(payload)

        zipped = zlib.compress(message)

        self.log.debug('payload_size=%d, compressed_size=%d, compression_ratio=%.3f' %
                       (len(payload), len(zipped), float(len(payload))/float(len(zipped))))

        url = '%s/api/agent?api_key=%s' % (url, api_key)

        request = None

        try:
            request = requests.post(url, data=zipped, timeout=10,
                                    headers=self.post_headers(zipped))

            request.raise_for_status()

            if 200 <= request.status_code < 205:
                self.log.debug("Payload accepted")

        except ConnectionError:
            self.log.exception('Unable to post payload.')
        except TooManyRedirects:
            self.log.exception('To many redirects.')
        except HTTPError:
            self.log('Invalid request.')
        except Timeout:
            self.log.exception('Request timed out.')
        finally:
            try:
                self.log.error("Received status code: %s" % request.status_code)
            except AttributeError:
                pass

    def check(self):
        url = self.config.get('emit_url')
        api_key = self.config.get('api_key')

        try:
            url = '%s/api/agent/validate?api_key=%s' % (url, api_key)
            request = requests.post(url, data='', timeout=5, headers={
                'User-Agent': 'Whale Agent/%s' % self.config.get('version')
            })
            request.raise_for_status()
            self.log.info('Emit endpoint validation success.')
        except RequestException:
            raise CheckException('Could not connect to the emit endpoint %s' % url)

        return True

    def config_check(self):
        url = self.config.get('emit_url')

        if url is None:
            raise CheckException('Please set a emit_url in the config file.')

        api_key = self.config.get('api_key')

        if api_key is None:
            raise CheckException('Please set a api_key in the config file.')

    def post_headers(self, payload):
        return {
            'User-Agent': 'Whale Agent/%s' % self.config.get('version'),
            'Content-Type': 'application/json',
            'Content-Encoding': 'deflate',
            'Accept': 'text/html, */*',
            'Content-MD5': md5(payload).hexdigest()
        }


class HttpEmitterException(AgentException):
    pass
