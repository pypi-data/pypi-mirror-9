import re

from appdirs import user_cache_dir
from lxml import etree, objectify
from dogpile.cache import make_region

from . import namespaces
from .version import __version__


region = make_region().configure(
    'dogpile.cache.dbm',
    expiration_time=1209600,  # 14 days
    arguments={
        "filename": "{dir}/{version}.dbm".format(
            dir=user_cache_dir('anentropic', 'dirtyebay'),
            version='dirtyebay_{}'.format(__version__)
        )
    }
)


VERSION_COMMENT = re.compile(r'\s*Version\s*(\d+)\s*')

NS_MAP = {
    'wsdl': namespaces.WSDL,
    'ebay': namespaces.EBAY,
    'xs': namespaces.XSD,
}


class VersionNotFound(Exception):
    pass


def version_from_schema(schema_el):
    """
    returns: API version number <str>
    raises: <VersionNotFound>

    NOTE:
    relies on presence of comment tags in the XSD, which are currently present
    for both ebaySvc.xsd (TradingAPI) and ShoppingService.xsd (ShoppingAPI)
    """
    vc_el = schema_el
    while True:
        vc_el = vc_el.getprevious()
        if vc_el is None:
            break
        if vc_el.tag is etree.Comment:
            match = VERSION_COMMENT.search(vc_el.text)
            if match:
                try:
                    return match.group(1)
                except IndexError:
                    pass
    raise VersionNotFound('Version comment not found preceeding schema node')


def _default_ns_prefix(nsmap):
    """
    XML doc may have several prefix:namespace_url pairs, can also specify
    a namespace_url as default, tags in that namespace don't need a prefix
    NOTE:
    we rely on default namespace also present in prefixed form, I'm not sure if
    this is an XML certainty or a quirk of the eBay WSDLs

    in our case the WSDL contains:
        <wsdl:documentation>
            <Version>1.0.0</Version>
        </wsdl:documentation>
    ...but our query needs to give a prefix to the path of `Version` so we need
    to determine the default namespace of the doc, find the matching prefix and
    return it
    """
    if None in nsmap:
        default_url = nsmap[None]
        prefix = None
        for key, val in nsmap.iteritems():
            if val == default_url and key is not None:
                prefix = key
                break
        else:
            raise ValueError(
                "Default namespace {url} not found as a prefix".format(
                    url=default_url
                )
            )
        return prefix
    raise ValueError("No default namespace found in map")


def version_from_wsdl(wsdl_tree):
    """
    returns: API version number <str>
    raises: <VersionNotFound>

    NOTE:
    relies on presence of documentation node in the WSDLs:
        <wsdl:documentation>
            <Version>1.0.0</Version>
        </wsdl:documentation>
    """
    prefix = _default_ns_prefix(wsdl_tree.nsmap)

    # XPath doesn't allow empty prefix:
    safe_map = wsdl_tree.nsmap.copy()
    try:
        del safe_map[None]
    except KeyError:
        pass

    try:
        # various eBay WSDLs are inconsistent - need case-insensitive matching
        version_el = wsdl_tree.xpath(
            'wsdl:service/wsdl:documentation/'
            '*[self::{p}:version or self::{p}:Version]'.format(p=prefix),
            namespaces=safe_map
        )[0]
    except IndexError:
        raise VersionNotFound(
            'Version not found in WSDL service documentation'
        )
    else:
        return version_el.text


def _make_safe(schema_el):
    """
    Workaround for segfault bug
    https://bugs.launchpad.net/lxml/+bug/1415907

    yes, tostring->fromstring roundtrip is ugly and inefficient
    """
    return etree.fromstring(etree.tostring(schema_el))


@region.cache_on_arguments()
def parser_from_schema(schema_url, require_version=True):
    """
    Returns an XSD-schema-enabled lxml parser from a WSDL or XSD

    `schema_url` can of course be local path via file:// url

    NOTE:
    currently we're not making use of the resulting parser(!) due to:
    https://bugs.launchpad.net/lxml/+bug/1416853
    """
    schema_tree = etree.parse(schema_url)

    def get_version(element, getter):
        try:
            return getter(element)
        except VersionNotFound:
            if require_version:
                raise
            else:
                return None

    root = schema_tree.getroot()
    if root.tag == '{%s}definitions' % namespaces.WSDL:
        # wsdl should contain an embedded schema
        schema_el = schema_tree.find('wsdl:types/xs:schema', namespaces=NS_MAP)
        # hack to avoid segfault:
        schema_el = _make_safe(schema_el)
        version = get_version(root, version_from_wsdl)
    else:
        schema_el = root
        version = get_version(schema_el, version_from_schema)

    schema = etree.XMLSchema(schema_el)
    return objectify.makeparser(schema=schema), version
