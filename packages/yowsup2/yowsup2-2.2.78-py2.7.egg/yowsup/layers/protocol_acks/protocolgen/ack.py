# ./ack.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:e92452c8d3e28a9e27abfc9994d2007779e7f4c9
# Generated 2015-01-19 03:36:14.978135 by PyXB version 1.2.4 using Python 3.3.5.final.0
# Namespace AbsentNamespace0

from __future__ import unicode_literals
import pyxb
import pyxb.binding
import pyxb.binding.saxer
import io
import pyxb.utils.utility
import pyxb.utils.domutils
import sys
import pyxb.utils.six as _six

# Unique identifier for bindings created at the same time
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:f04d7c3c-9f83-11e4-925d-8c705ae92fc0')

# Version of PyXB used to generate the bindings
_PyXBVersion = '1.2.4'
# Generated bindings are not compatible across PyXB versions
if pyxb.__version__ != _PyXBVersion:
    raise pyxb.PyXBVersionError(_PyXBVersion)

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

# NOTE: All namespace declarations are reserved within the binding
Namespace = pyxb.namespace.CreateAbsentNamespace()
Namespace.configureCategories(['typeBinding', 'elementBinding'])

def CreateFromDocument (xml_text, default_namespace=None, location_base=None):
    """Parse the given XML and use the document element to create a
    Python instance.

    @param xml_text An XML document.  This should be data (Python 2
    str or Python 3 bytes), or a text (Python 2 unicode or Python 3
    str) in the L{pyxb._InputEncoding} encoding.

    @keyword default_namespace The L{pyxb.Namespace} instance to use as the
    default namespace where there is no default namespace in scope.
    If unspecified or C{None}, the namespace of the module containing
    this function will be used.

    @keyword location_base: An object to be recorded as the base of all
    L{pyxb.utils.utility.Location} instances associated with events and
    objects handled by the parser.  You might pass the URI from which
    the document was obtained.
    """

    if pyxb.XMLStyle_saxer != pyxb._XMLStyle:
        dom = pyxb.utils.domutils.StringToDOM(xml_text)
        return CreateFromDOM(dom.documentElement, default_namespace=default_namespace)
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    saxer = pyxb.binding.saxer.make_parser(fallback_namespace=default_namespace, location_base=location_base)
    handler = saxer.getContentHandler()
    xmld = xml_text
    if isinstance(xmld, _six.text_type):
        xmld = xmld.encode(pyxb._InputEncoding)
    saxer.parse(io.BytesIO(xmld))
    instance = handler.rootObject()
    return instance

def CreateFromDOM (node, default_namespace=None):
    """Create a Python instance from the given DOM node.
    The node tag must correspond to an element declaration in this module.

    @deprecated: Forcing use of DOM interface is unnecessary; use L{CreateFromDocument}."""
    if default_namespace is None:
        default_namespace = Namespace.fallbackNamespace()
    return pyxb.binding.basis.element.AnyCreateFromDOM(node, default_namespace)


# Atomic simple type: ack_names
class ack_names (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ack_names')
    _XSDLocation = pyxb.utils.utility.Location('/home/tarek/Projects.LinuxOnly/yowsup/yowsup/layers/protocol_acks/protocolgen/xsd/ack.xsd', 4, 4)
    _Documentation = None
ack_names._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=ack_names, enum_prefix=None)
ack_names.receipt = ack_names._CF_enumeration.addEnumeration(unicode_value='receipt', tag='receipt')
ack_names.message = ack_names._CF_enumeration.addEnumeration(unicode_value='message', tag='message')
ack_names._InitializeFacetMap(ack_names._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'ack_names', ack_names)

# Complex type [anonymous] with content type EMPTY
class CTD_ANON (pyxb.binding.basis.complexTypeDefinition):
    """Complex type [anonymous] with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('/home/tarek/Projects.LinuxOnly/yowsup/yowsup/layers/protocol_acks/protocolgen/xsd/ack.xsd', 12, 8)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute class uses Python identifier class_
    __class = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'class'), 'class_', '__AbsentNamespace0_CTD_ANON_class', ack_names)
    __class._DeclarationLocation = pyxb.utils.utility.Location('/home/tarek/Projects.LinuxOnly/yowsup/yowsup/layers/protocol_acks/protocolgen/xsd/ack.xsd', 13, 12)
    __class._UseLocation = pyxb.utils.utility.Location('/home/tarek/Projects.LinuxOnly/yowsup/yowsup/layers/protocol_acks/protocolgen/xsd/ack.xsd', 13, 12)
    
    class_ = property(__class.value, __class.set, None, None)

    
    # Attribute id uses Python identifier id
    __id = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'id'), 'id', '__AbsentNamespace0_CTD_ANON_id', pyxb.binding.datatypes.string)
    __id._DeclarationLocation = pyxb.utils.utility.Location('/home/tarek/Projects.LinuxOnly/yowsup/yowsup/layers/protocol_acks/protocolgen/xsd/ack.xsd', 14, 12)
    __id._UseLocation = pyxb.utils.utility.Location('/home/tarek/Projects.LinuxOnly/yowsup/yowsup/layers/protocol_acks/protocolgen/xsd/ack.xsd', 14, 12)
    
    id = property(__id.value, __id.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __class.name() : __class,
        __id.name() : __id
    })



ack = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'ack'), CTD_ANON, location=pyxb.utils.utility.Location('/home/tarek/Projects.LinuxOnly/yowsup/yowsup/layers/protocol_acks/protocolgen/xsd/ack.xsd', 11, 4))
Namespace.addCategoryObject('elementBinding', ack.name().localName(), ack)
