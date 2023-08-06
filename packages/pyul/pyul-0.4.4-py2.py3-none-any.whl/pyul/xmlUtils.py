from xml.parsers import expat
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl
from xml.dom.minidom import parseString
try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO
try:
    from collections import OrderedDict
except ImportError :
    OrderedDict = dict

try:
    _basestring = basestring
except NameError:
    _basestring = str
try:
    _unicode = unicode
except NameError:
    _unicode = str

__all__ = ['parseToDict','unparseFromDict',
           'removeWhitespaceNodes']


class ParsingInterrupted(Exception): pass


class _DictSAXHandler(object):
    """Written by: Martin Blech  -  Integrated by: Kyle Rockman"""
    def __init__(self,
                 item_depth=0,
                 item_callback=(lambda *args: True),
                 xml_attribs=True,
                 attr_prefix='@',
                 cdata_key='#text',
                 force_cdata=True,
                 cdata_separator='',
                 postprocessor=None,
                 dict_constructor=OrderedDict,
                 strip_whitespace=True):
        self.path = []
        self.stack = []
        self.data = None
        self.item = None
        self.item_depth = item_depth
        self.xml_attribs = xml_attribs
        self.item_callback = item_callback
        self.attr_prefix = attr_prefix
        self.cdata_key = cdata_key
        self.force_cdata = force_cdata
        self.cdata_separator = cdata_separator
        self.postprocessor = postprocessor
        self.dict_constructor = dict_constructor
        self.strip_whitespace = strip_whitespace

    def startElement(self, name, attrs):
        attrs = self.dict_constructor(zip(attrs[0::2], attrs[1::2]))
        self.path.append((name, attrs or None))
        if len(self.path) > self.item_depth:
            self.stack.append((self.item, self.data))
            if self.xml_attribs:
                attrs = self.dict_constructor(
                    (self.attr_prefix+key, value)
                    for (key, value) in attrs.items())
            else:
                attrs = None
            self.item = attrs or None
            self.data = None

    def endElement(self, name):
        if len(self.path) == self.item_depth:
            item = self.item
            if item is None:
                item = self.data
            should_continue = self.item_callback(self.path, item)
            if not should_continue:
                raise ParsingInterrupted()
        if len(self.stack):
            item, data = self.item, self.data
            self.item, self.data = self.stack.pop()
            if self.strip_whitespace and data is not None:
                data = data.strip() or None
            if data and self.force_cdata and item is None:
                item = self.dict_constructor()
            if item is not None:
                if data:
                    self.push_data(item, self.cdata_key, data)
                self.item = self.push_data(self.item, name, item)
            else:
                self.item = self.push_data(self.item, name, data)
        else:
            self.item = self.data = None
        self.path.pop()

    def characters(self, data):
        if not self.data:
            self.data = data
        else:
            self.data += self.cdata_separator + data

    def push_data(self, item, key, data):
        if self.postprocessor is not None:
            result = self.postprocessor(self.path, key, data)
            if result is None:
                return item
            key, data = result
        if item is None:
            item = self.dict_constructor()
        try:
            value = item[key]
            if isinstance(value, list):
                value.append(data)
            else:
                item[key] = [value, data]
        except KeyError:
            item[key] = data
        return item


def _emit(key, value, content_handler,
          attr_prefix='@',
          cdata_key='#text',
          root=True,
          preprocessor=None):
    if preprocessor is not None:
        result = preprocessor(key, value)
        if result is None:
            return
        key, value = result
    if not isinstance(value, (list, tuple)):
        value = [value]
    if root and len(value) > 1:
        raise ValueError('document with multiple roots')
    for v in value:
        if v is None:
            v = OrderedDict()
        elif not isinstance(v, dict):
            v = _unicode(v)
        if isinstance(v, _basestring):
            v = OrderedDict(((cdata_key, v),))
        cdata = None
        attrs = OrderedDict()
        children = []
        for ik, iv in v.items():
            if ik == cdata_key:
                cdata = iv
                continue
            if ik.startswith(attr_prefix):
                attrs[ik[len(attr_prefix):]] = iv
                continue
            children.append((ik, iv))
        content_handler.startElement(key, AttributesImpl(attrs))
        for child_key, child_value in children:
            _emit(child_key, child_value, content_handler,
                  attr_prefix, cdata_key, False, preprocessor)
        if cdata is not None:
            content_handler.characters(cdata)
        content_handler.endElement(key)


def parseToDict(data):
    handler = _DictSAXHandler()
    parser = expat.ParserCreate()
    parser.ordered_attributes = True
    parser.StartElementHandler = handler.startElement
    parser.EndElementHandler = handler.endElement
    parser.CharacterDataHandler = handler.characters
    try:
        parser.ParseFile(data)
    except (TypeError, AttributeError):
        if isinstance(data, _unicode):
            data = data.encode('utf-8')
        parser.Parse(data, True)
    return handler.item


def unparseFromDict(data):
    ((key, value),) = data.items()
    output = StringIO()
    content_handler = XMLGenerator(output, 'utf-8')
    content_handler.startDocument()
    _emit(key, value, content_handler)
    content_handler.endDocument()
    value = output.getvalue()
    try:
        value = value.decode('utf-8')
    except AttributeError:
        pass
    return parseString(value).toprettyxml(indent="\t")


def removeWhitespaceNodes(node, unlink=False):
    """Removes all of the whitespace-only text decendants of a DOM node.

    When creating a DOM from an XML source, XML parsers are required to
    consider several conditions when deciding whether to include
    whitespace-only text nodes. This function ignores all of those
    conditions and removes all whitespace-only text decendants of the
    specified node. If the unlink flag is specified, the removed text
    nodes are unlinked so that their storage can be reclaimed. If the
    specified node is a whitespace-only text node then it is left
    unmodified."""

    remove_list = []
    for child in node.childNodes:
        if child.nodeType == Node.TEXT_NODE and \
           not child.data.strip():
            remove_list.append(child)
        elif child.hasChildNodes():
            remove_whilespace_nodes(child, unlink)
    for node in remove_list:
        node.parentNode.removeChild(node)
        if unlink:
            node.unlink()
