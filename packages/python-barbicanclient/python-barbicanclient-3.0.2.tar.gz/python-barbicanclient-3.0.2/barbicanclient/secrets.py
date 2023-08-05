# Copyright (c) 2013 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import functools
import logging
import six

from oslo.utils.timeutils import parse_isotime

from barbicanclient import base
from barbicanclient import formatter


LOG = logging.getLogger(__name__)


def lazy(func):
    @functools.wraps(func)
    def wrapper(self, *args):
        self._fill_lazy_properties()
        return func(self, *args)
    return wrapper


def immutable_after_save(func):
    @functools.wraps(func)
    def wrapper(self, *args):
        if self._secret_ref:
            raise base.ImmutableException()
        return func(self, *args)
    return wrapper


class SecretFormatter(formatter.EntityFormatter):

    columns = ("Secret href",
               "Name",
               "Created",
               "Status",
               "Content types",
               "Algorithm",
               "Bit length",
               "Mode",
               "Expiration",
               )

    def _get_formatted_data(self):
        data = (self.secret_ref,
                self.name,
                self.created,
                self.status,
                self.content_types,
                self.algorithm,
                self.bit_length,
                self.mode,
                self.expiration,
                )
        return data


class Secret(SecretFormatter):
    """
    Secrets are used to keep track of the data stored in Barbican.
    """
    _entity = 'secrets'

    def __init__(self, api, name=None, expiration=None, algorithm=None,
                 bit_length=None, mode=None, payload=None,
                 payload_content_type=None, payload_content_encoding=None,
                 secret_ref=None, created=None, updated=None,
                 content_types=None, status=None):
        self._api = api
        self._secret_ref = secret_ref
        self._fill_from_data(
            name=name,
            expiration=expiration,
            algorithm=algorithm,
            bit_length=bit_length,
            mode=mode,
            payload=payload,
            payload_content_type=payload_content_type,
            payload_content_encoding=payload_content_encoding,
            created=created,
            updated=updated,
            content_types=content_types,
            status=status
        )

    @property
    def secret_ref(self):
        return self._secret_ref

    @property
    @lazy
    def name(self):
        return self._name

    @property
    @lazy
    def expiration(self):
        return self._expiration

    @property
    @lazy
    def algorithm(self):
        return self._algorithm

    @property
    @lazy
    def bit_length(self):
        return self._bit_length

    @property
    @lazy
    def mode(self):
        return self._mode

    @property
    @lazy
    def payload_content_encoding(self):
        return self._payload_content_encoding

    @property
    @lazy
    def created(self):
        return self._created

    @property
    @lazy
    def updated(self):
        return self._updated

    @property
    @lazy
    def content_types(self):
        if self._content_types:
            return self._content_types
        elif self._payload_content_type:
            return {u'default': six.u(self.payload_content_type)}
        return None

    @property
    @lazy
    def status(self):
        return self._status

    @property
    def payload_content_type(self):
        if not self._payload_content_type and self.content_types:
            self._payload_content_type = self.content_types.get('default')
        return self._payload_content_type

    @property
    def payload(self):
        if not self._payload:
            self._fetch_payload()
        return self._payload

    @name.setter
    @immutable_after_save
    def name(self, value):
        self._name = value

    @expiration.setter
    @immutable_after_save
    def expiration(self, value):
        self._expiration = value

    @algorithm.setter
    @immutable_after_save
    def algorithm(self, value):
        self._algorithm = value

    @bit_length.setter
    @immutable_after_save
    def bit_length(self, value):
        self._bit_length = value

    @mode.setter
    @immutable_after_save
    def mode(self, value):
        self._mode = value

    @payload.setter
    @immutable_after_save
    def payload(self, value):
        self._payload = value

    @payload_content_type.setter
    @immutable_after_save
    def payload_content_type(self, value):
        self._payload_content_type = value

    @payload_content_encoding.setter
    @immutable_after_save
    def payload_content_encoding(self, value):
        self._payload_content_encoding = value

    def _fetch_payload(self):
        if not self.payload_content_type and not self.content_types:
            raise ValueError('Secret has no encrypted data to decrypt.')
        elif not self.payload_content_type:
            raise ValueError("Must specify decrypt content-type as "
                             "secret does not specify a 'default' "
                             "content-type.")
        headers = {'Accept': self.payload_content_type}
        self._payload = self._api._get_raw(self._secret_ref, headers)

    @immutable_after_save
    def store(self):
        secret_dict = base.filter_empty_keys({
            'name': self.name,
            'payload': self.payload,
            'payload_content_type': self.payload_content_type,
            'payload_content_encoding': self.payload_content_encoding,
            'algorithm': self.algorithm,
            'mode': self.mode,
            'bit_length': self.bit_length,
            'expiration': self.expiration
        })

        LOG.debug("Request body: {0}".format(secret_dict))

        # Save, store secret_ref and return
        response = self._api._post(self._entity, secret_dict)
        if response:
            self._secret_ref = response.get('secret_ref')
        return self.secret_ref

    def delete(self):
        if self._secret_ref:
            self._api._delete(self._secret_ref)
            self._secret_ref = None
        else:
            raise LookupError("Secret is not yet stored.")

    def _fill_from_data(self, name=None, expiration=None, algorithm=None,
                        bit_length=None, mode=None, payload=None,
                        payload_content_type=None,
                        payload_content_encoding=None, created=None,
                        updated=None, content_types=None, status=None):
        self._name = name
        self._algorithm = algorithm
        self._bit_length = bit_length
        self._mode = mode
        self._payload = payload
        self._payload_content_encoding = payload_content_encoding
        self._expiration = expiration
        if self._expiration:
            self._expiration = parse_isotime(self._expiration)
        if self._secret_ref:
            self._content_types = content_types
            self._status = status
            self._created = created
            self._updated = updated
            if self._created:
                self._created = parse_isotime(self._created)
            if self._updated:
                self._updated = parse_isotime(self._updated)
        else:
            self._content_types = None
            self._status = None
            self._created = None
            self._updated = None

        if not self._content_types:
            self._payload_content_type = payload_content_type
        else:
            self._payload_content_type = self._content_types.get('default',
                                                                 None)

    def _fill_lazy_properties(self):
        if self._secret_ref and not self._name:
            result = self._api._get(self._secret_ref)
            self._fill_from_data(
                name=result.get('name'),
                expiration=result.get('expiration'),
                algorithm=result.get('algorithm'),
                bit_length=result.get('bit_length'),
                mode=result.get('mode'),
                payload_content_type=result.get('payload_content_type'),
                payload_content_encoding=result.get(
                    'payload_content_encoding'
                ),
                created=result.get('created'),
                updated=result.get('updated'),
                content_types=result.get('content_types'),
                status=result.get('status')
            )

    def __repr__(self):
        if self._secret_ref:
            return 'Secret(secret_ref="{0}")'.format(self._secret_ref)
        return 'Secret(name="{0}")'.format(self._name)


class SecretManager(base.BaseEntityManager):

    def __init__(self, api):
        super(SecretManager, self).__init__(api, 'secrets')

    def get(self, secret_ref, payload_content_type=None):
        """
        Get a Secret

        :param secret_ref: Full HATEOAS reference to a Secret
        :param payload_content_type: Content type to use for payload decryption
        :returns: Secret
        """
        LOG.debug("Getting secret - Secret href: {0}".format(secret_ref))
        base.validate_ref(secret_ref, 'Secret')
        return Secret(
            api=self._api,
            payload_content_type=payload_content_type,
            secret_ref=secret_ref
        )

    def create(self, name=None, payload=None,
               payload_content_type=None, payload_content_encoding=None,
               algorithm=None, bit_length=None, mode=None, expiration=None):
        """
        Create a Secret

        :param name: A friendly name for the Secret
        :param payload: The unencrypted secret data
        :param payload_content_type: The format/type of the secret data
        :param payload_content_encoding: The encoding of the secret data
        :param algorithm: The algorithm associated with this secret key
        :param bit_length: The bit length of this secret key
        :param mode: The algorithm mode used with this secret key
        :param expiration: The expiration time of the secret in ISO 8601 format
        :returns: Secret
        """
        return Secret(api=self._api, name=name, payload=payload,
                      payload_content_type=payload_content_type,
                      payload_content_encoding=payload_content_encoding,
                      algorithm=algorithm, bit_length=bit_length, mode=mode,
                      expiration=expiration)

    def delete(self, secret_ref):
        """
        Delete a Secret

        :param secret_ref: The href for the secret
        """
        if not secret_ref:
            raise ValueError('secret_ref is required.')
        self._api._delete(secret_ref)

    def list(self, limit=10, offset=0, name=None, algorithm=None,
             mode=None, bits=0):
        """
        List all Secrets for the project

        :param limit: Max number of secrets returned
        :param offset: Offset secrets to begin list
        :param name: Name filter for the list
        :param algorithm: Algorithm filter for the list
        :param mode: Mode filter for the list
        :param bits: Bits filter for the list
        :returns: list of Secret metadata objects
        """
        LOG.debug('Listing secrets - offset {0} limit {1}'.format(offset,
                                                                  limit))
        href = '{0}/{1}'.format(self._api._base_url, self._entity)
        params = {'limit': limit, 'offset': offset}
        if name:
            params['name'] = name
        if algorithm:
            params['alg'] = algorithm
        if mode:
            params['mode'] = mode
        if bits > 0:
            params['bits'] = bits

        response = self._api._get(href, params)

        return [
            Secret(api=self._api, **s)
            for s in response.get('secrets', [])
        ]
