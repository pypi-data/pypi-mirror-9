from abc import ABCMeta
from ConfigParser import NoOptionError, NoSectionError
from functools import partial
import logging

from lxml import etree, objectify
from lxml.builder import ElementMaker
import requests

from .config import production_config, sandbox_config, CONFIG_PATH
from . import namespaces
from .utils import parser_from_schema


logging.basicConfig()
log = logging.getLogger(__name__)

# I wish I didn't have to hard-code this but there's no service to query, see:
# http://developer.ebay.com/DevZone/merchandising/docs/Concepts/SiteIDToGlobalID.html
SITE_ID_TO_GLOBAL_ID = {
    0: 'EBAY-US',
    2: 'EBAY-ENCA',
    3: 'EBAY-GB',
    15: 'EBAY-AU',
    16: 'EBAY-AT',
    23: 'EBAY-FRBE',
    71: 'EBAY-FR',
    77: 'EBAY-DE',
    100: 'EBAY-MOTOR',
    101: 'EBAY-IT',
    123: 'EBAY-NLBE',
    146: 'EBAY-NL',
    186: 'EBAY-ES',
    193: 'EBAY-CH',
    201: 'EBAY-HK',
    203: 'EBAY-IN',
    205: 'EBAY-IE',
    207: 'EBAY-MY',
    210: 'EBAY-FRCA',
    211: 'EBAY-PH',
    212: 'EBAY-PL',
    216: 'EBAY-SG',
}


NSMAP = {
    'soap': namespaces.SOAP_1_2,
    'soapenv': namespaces.SOAP_1_1,
    'ebl': namespaces.EBAY,
    'xsi': namespaces.XSI,
}


def dicttoxml(obj, factory):
    elements = []
    for key, value in obj.items():
        if hasattr(value, 'items'):
            elements.append(dicttoxml(value, factory))
        elif isinstance(value, (list, tuple)):
            elements.append([
                dicttoxml(sub_val, factory)
                for sub_val in value
            ])
        else:
            el = getattr(factory, key)(unicode(value))
            elements.append(el)
    return elements


class APIBase:
    """
    Abstract: make a concrete sub-class (some APIs are provided below)
    """
    __metaclass__ = ABCMeta

    SCHEMA_URL = None

    PRODUCTION_ENDPOINT = None
    SANDBOX_ENDPOINT = None

    SOAP_VERSION = None

    DEFAULT_NAMESPACE = namespaces.EBAY

    def __init__(self, schema_url=None, sandbox=False, **kwargs):
        # eBay API methods are all CamelCase so it should be safe to set
        # lowercase (or all-caps) attributes on self (see __getattr__)

        self.CONF_PREFIX = self._get_conf_prefix()
        self.sandbox = sandbox
        if sandbox:
            self.config = sandbox_config
        else:
            self.config = production_config

        # use passed in schema first, else try config file,
        # else use class default
        if schema_url is not None:
            self._schema = schema_url
        else:
            try:
                self._schema = self.config.get('soap',
                                               '%s_schema' % self.CONF_PREFIX)
            except (NoOptionError, NoSectionError):
                if self.SCHEMA_URL is None:
                    raise NotImplementedError(
                        'You must give a value for SCHEMA_URL on a sub-class,'
                        ' or define <api name>_schema in the conf file'
                    )
                self._schema = self.SCHEMA_URL

        # make a schema-aware parser (for deserializing responses into objects)
        self.parser, self.version = parser_from_schema(self._schema)

        # determine the service endpoint URI
        try:
            self._endpoint = self.config.get('soap',
                                             '%s_api' % self.CONF_PREFIX)
        except (NoOptionError, NoSectionError):
            if sandbox:
                if self.SANDBOX_ENDPOINT is None:
                    raise NotImplementedError(
                        'You must give a value for SANDBOX_ENDPOINT on a sub-'
                        'class, or define <api name>_api in the conf file'
                    )
                self._endpoint = self.SANDBOX_ENDPOINT
            else:
                if self.SANDBOX_ENDPOINT is None:
                    raise NotImplementedError(
                        'You must give a value for PRODUCTION_ENDPOINT on a '
                        'sub-class, or define <api name>_api in the conf file'
                    )
                self._endpoint = self.PRODUCTION_ENDPOINT

        if self.SOAP_VERSION is None:
            raise NotImplementedError(
                'You must give a value for SOAP_VERSION on a sub-class'
            )

        self.client = requests.Session()
        self.client.headers.update({
            'Content-Type': 'application/soap+xml; charset=utf-8',
            'SOAPAction': '',
        })

        log.info('CONFIG_PATH: %s', CONFIG_PATH)
        self.site_id = (
            kwargs.get('site_id') or self.config.get('site', 'site_id')
        )
        self.app_id = (
            kwargs.get('app_id') or self.config.get('keys', 'app_id')
        )
        self.dev_id = (
            kwargs.get('dev_id') or self.config.get('keys', 'dev_id')
        )
        self.cert_id = (
            kwargs.get('cert_id') or self.config.get('keys', 'cert_id')
        )
        self.token = (
            kwargs.get('token') or self.config.get('auth', 'token')
        )

        self._last_response = None

    def __getattr__(self, name):
        """
        make a SOAP request

        Note:
        eBay API methods are all CamelCase, or otherCamelCase
        """
        if name.lower() == name or name.startswith('_'):
            # avoid accidental API calls in ipython..!
            return super(APIBase, self).__getattr(name)
        return partial(self._execute, name=name)

    def _get_conf_prefix(self):
        # assume the class name ends in 'API'
        return self.__class__.__name__[:-3].lower()

    def _nsmap(self):
        nsmap = NSMAP.copy()
        nsmap[None] = self.DEFAULT_NAMESPACE
        return nsmap

    def get_soap_el_factory(self):
        if self.SOAP_VERSION == '1.1':
            return ElementMaker(
                namespace=namespaces.SOAP_1_1,
                nsmap=self._nsmap()
            )
        elif self.SOAP_VERSION == '1.2':
            return ElementMaker(
                namespace=namespaces.SOAP_1_2,
                nsmap=self._nsmap()
            )
        else:
            raise ValueError(
                "Invalid SOAP_VERSION: {}".format(self.SOAP_VERSION)
            )

    def get_msg_el_factory(self):
        return ElementMaker(nsmap=self._nsmap())

    def get_http_headers(self, name):
        return {}

    def _request(self, name, envelope):
        response = self.client.post(
            url=self._endpoint,
            data=etree.tostring(envelope),
            params=self.get_query_params(name),
            headers=self.get_http_headers(name),
        )
        response.raise_for_status()
        self._last_response = response
        return response

    def _execute(self, name, **kwargs):
        """
        this indirection gives us the same call signature as used by
        ebaysdk-python, i.e. `api.execute('GetUser', {})`

        (our __init__ signature and conf are different still at the moment)
        """
        return self.execute(name, kwargs)

    def execute(self, name, params):
        request_name = '{}Request'.format(name)  # can we rely on this?
        factory = self.get_msg_el_factory()
        body_el = getattr(factory, request_name)
        envelope = self.make_envelope([
            body_el(*dicttoxml(params, factory))
        ])

        log.debug(etree.tostring(envelope, pretty_print=True))

        response = self._request(name, envelope)
        return self.objectify_response(name, response)

    def objectify_response(self, name, response):
        soap_response = etree.fromstring(
            response.text.encode(response.encoding)
        )
        response_name = '{}Response'.format(name)  # can we rely on this?
        body_root = soap_response.xpath(
            "//*[local-name() = '%s']" % response_name
        )[0]

        # tostring->fromstring roundtrip is ugly but otherwise the objectified
        # tree is spoiled by namespaces (would have to use getattr everywhere)
        return objectify.fromstring(
            etree.tostring(body_root),
            parser=self.parser
        )

    def get_soap_header(self):
        return None

    def get_query_params(self, name):
        return {}

    def make_envelope(self, body_elements=None):
        """
        body_elements: <list> of etree.Elements or <None>
        """
        soap = self.get_soap_el_factory()
        body_elements = body_elements or []
        body = soap.Body(*body_elements)
        header = self.get_soap_header()
        if header is not None:
            elements = [header, body]
        else:
            elements = [body]
        return soap.Envelope(
            #{
            #    '{%s}encodingStyle' % namespaces.SOAP_1_2: (
            #        'http://www.w3.org/2001/12/soap-encoding')
            #},
            *elements
        )


class TradingAPI(APIBase):
    SCHEMA_URL = 'http://developer.ebay.com/webservices/latest/ebaySvc.xsd'

    PRODUCTION_ENDPOINT = 'https://api.ebay.com/wsapi'
    SANDBOX_ENDPOINT = 'https://api.sandbox.ebay.com/wsapi'

    SOAP_VERSION = '1.1'

    def __getattr__(self, name):
        method = super(TradingAPI, self).__getattr__(name=name)
        # the method call has to include the API version in the body
        # even though it's also provided on the querystring...
        return partial(method, Version=self.version)

    def get_soap_header(self):
        soap = self.get_soap_el_factory()
        payload = self.get_msg_el_factory()
        return soap.Header(
            payload.RequesterCredentials(
                payload.Credentials(
                    payload.AppID(self.app_id),
                    payload.DevId(self.dev_id),
                    payload.AuthCert(self.cert_id),
                ),
                payload.eBayAuthToken(self.token)
            )
        )

    def get_query_params(self, name):
        # for some reason ebay require some fields from the SOAP request to be
        # repeated as querystring args appended to the service url
        return {
            'callname': name,
            'siteid': self.site_id,
            'appid': self.app_id,
            'version': self.version,
            'routing': 'default',
        }


class PlatformNotificationsAPI(TradingAPI):
    """
    The calls to get and set platform notification preferences are actually
    part of the TradingAPI.

    The notifications received at your callback url can be decoded using the
    `objectify_response` method.
    """
    pass


class ShoppingAPI(APIBase):
    SCHEMA_URL = (
        'http://developer.ebay.com/webservices/latest/ShoppingService.xsd'
    )

    PRODUCTION_ENDPOINT = 'http://open.api.ebay.com/shopping'
    SANDBOX_ENDPOINT = 'http://open.api.sandbox.ebay.com/shopping'

    SOAP_VERSION = '1.1'

    def get_query_params(self, name):
        # for some reason ebay require some fields from the SOAP request to be
        # repeated as querystring args appended to the service url
        return {
            'callname': name,
            'siteid': self.site_id,
            'appid': self.app_id,
            'version': self.version,
            'responseencoding': 'SOAP',
            'requestencoding': 'SOAP',
        }


class FindingAPI(APIBase):
    SCHEMA_URL = (
        'http://developer.ebay.com/webservices/Finding/latest/'
        'FindingService.wsdl'
    )

    PRODUCTION_ENDPOINT = (
        'http://svcs.ebay.com/services/search/FindingService/v1'
    )
    SANDBOX_ENDPOINT = (
        'http://svcs.sandbox.ebay.com/services/search/FindingService/v1'
    )

    SOAP_VERSION = '1.2'

    DEFAULT_NAMESPACE = namespaces.EBAY_SEARCH

    def get_http_headers(self, name):
        site_id = int(self.site_id, 10)
        return {
            'X-EBAY-SOA-OPERATION-NAME': name,
            'X-EBAY-SOA-SERVICE-NAME': 'FindingService',  # this one is genius
            'X-EBAY-SOA-SERVICE-VERSION': self.version,
            'X-EBAY-SOA-GLOBAL-ID': SITE_ID_TO_GLOBAL_ID[site_id],
            'X-EBAY-SOA-SECURITY-APPNAME': self.app_id,
            'X-EBAY-SOA-REQUEST-DATA-FORMAT': 'SOAP',
            'X-EBAY-SOA-MESSAGE-PROTOCOL': 'SOAP12',
        }


class BusinessPoliciesAPI(APIBase):
    SCHEMA_URL = (
        'http://developer.ebay.com/webservices/business-policies/'
        'latest/SellerProfilesManagementService.wsdl'
    )

    PRODUCTION_ENDPOINT = (
        'https://svcs.ebay.com/services/selling/v1/'
        'SellerProfilesManagementService'
    )
    SANDBOX_ENDPOINT = (
        'http://svcs.sandbox.ebay.com/services/selling/v1/'
        'SellerProfilesManagementService'
    )

    SOAP_VERSION = '1.2'

    def get_http_headers(self, name):
        site_id = int(self.site_id, 10)
        return {
            'X-EBAY-SOA-OPERATION-NAME': name,
            'X-EBAY-SOA-SERVICE-VERSION': self.version,
            'X-EBAY-SOA-GLOBAL-ID': SITE_ID_TO_GLOBAL_ID[site_id],
            'X-EBAY-SOA-REQUEST-DATA-FORMAT': 'SOAP',
            'X-EBAY-SOA-MESSAGE-PROTOCOL': 'SOAP12',
            'X-EBAY-SOA-SECURITY-TOKEN': self.token,
        }
