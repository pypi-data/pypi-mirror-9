# .\com\nokia\oss\fm\_types.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:8174fb386f5fbf00da8199a7f594a1c5a6d48505
# Generated 2015-02-10 12:58:25.896000 by PyXB version 1.2.4 using Python 2.7.6.final.0
# Namespace http:///com/nokia/oss/fm/types.ecore [xmlns:com.nokia.oss.fm.types]

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
_GenerationUID = pyxb.utils.utility.UniqueIdentifier('urn:uuid:71e9b7b0-b0e1-11e4-8c57-8056f2d32e8a')

# Version of PyXB used to generate the bindings
_PyXBVersion = '1.2.4'
# Generated bindings are not compatible across PyXB versions
if pyxb.__version__ != _PyXBVersion:
    raise pyxb.PyXBVersionError(_PyXBVersion)

# Import bindings for namespaces imported into schema
import pyxb.binding.datatypes

# NOTE: All namespace declarations are reserved within the binding
Namespace = pyxb.namespace.NamespaceForURI('http:///com/nokia/oss/fm/types.ecore', create_if_missing=True)
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


# Atomic simple type: {http:///com/nokia/oss/fm/types.ecore}AlarmType
class AlarmType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """The event type determines the type of the alarm event. See ITU-T recommendations X.733 and X.736."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'AlarmType')
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\fmTypes_1.0-2.xsd', 4, 1)
    _Documentation = 'The event type determines the type of the alarm event. See ITU-T recommendations X.733 and X.736.'
AlarmType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=AlarmType, enum_prefix=None)
AlarmType.communication = AlarmType._CF_enumeration.addEnumeration(unicode_value='communication', tag='communication')
AlarmType.communications = AlarmType._CF_enumeration.addEnumeration(unicode_value='communications', tag='communications')
AlarmType.environmental = AlarmType._CF_enumeration.addEnumeration(unicode_value='environmental', tag='environmental')
AlarmType.equipment = AlarmType._CF_enumeration.addEnumeration(unicode_value='equipment', tag='equipment')
AlarmType.processingError = AlarmType._CF_enumeration.addEnumeration(unicode_value='processingError', tag='processingError')
AlarmType.qualityOfService = AlarmType._CF_enumeration.addEnumeration(unicode_value='qualityOfService', tag='qualityOfService')
AlarmType.integrityViolation = AlarmType._CF_enumeration.addEnumeration(unicode_value='integrityViolation', tag='integrityViolation')
AlarmType.operationalViolation = AlarmType._CF_enumeration.addEnumeration(unicode_value='operationalViolation', tag='operationalViolation')
AlarmType.physicalViolation = AlarmType._CF_enumeration.addEnumeration(unicode_value='physicalViolation', tag='physicalViolation')
AlarmType.securityViolation = AlarmType._CF_enumeration.addEnumeration(unicode_value='securityViolation', tag='securityViolation')
AlarmType.timeDomainViolation = AlarmType._CF_enumeration.addEnumeration(unicode_value='timeDomainViolation', tag='timeDomainViolation')
AlarmType._InitializeFacetMap(AlarmType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'AlarmType', AlarmType)

# Atomic simple type: {http:///com/nokia/oss/fm/types.ecore}AlarmText
class AlarmText (pyxb.binding.datatypes.string):

    """A common text field type used in FM OFaS and Alarm Description specifications."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'AlarmText')
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\fmTypes_1.0-2.xsd', 66, 1)
    _Documentation = 'A common text field type used in FM OFaS and Alarm Description specifications.'
AlarmText._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(1024))
AlarmText._CF_minLength = pyxb.binding.facets.CF_minLength(value=pyxb.binding.datatypes.nonNegativeInteger(1))
AlarmText._CF_pattern = pyxb.binding.facets.CF_pattern()
AlarmText._CF_pattern.addPattern(pattern='[ -~\xa0-\ufffd]*')
AlarmText._InitializeFacetMap(AlarmText._CF_maxLength,
   AlarmText._CF_minLength,
   AlarmText._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'AlarmText', AlarmText)

# Atomic simple type: {http:///com/nokia/oss/fm/types.ecore}SpecificProblem
class SpecificProblem (pyxb.binding.datatypes.positiveInteger):

    """The specific problem classifies the fault situation in the agent. The specific problem provides classification of finer granularity for the alarms than ‘Probable Cause’. See ITU-T recommendations X.733,X.736 and 3GPP TS 32.111-2 and TS 32.111-3."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'SpecificProblem')
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\fmTypes_1.0-2.xsd', 76, 1)
    _Documentation = 'The specific problem classifies the fault situation in the agent. The specific problem provides classification of finer granularity for the alarms than \u2018Probable Cause\u2019. See ITU-T recommendations X.733,X.736 and 3GPP TS 32.111-2 and TS 32.111-3.'
SpecificProblem._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive(value_datatype=SpecificProblem, value=pyxb.binding.datatypes.positiveInteger(2147483647))
SpecificProblem._CF_pattern = pyxb.binding.facets.CF_pattern()
SpecificProblem._CF_pattern.addPattern(pattern='[1-9][0-9]*')
SpecificProblem._InitializeFacetMap(SpecificProblem._CF_maxInclusive,
   SpecificProblem._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'SpecificProblem', SpecificProblem)

# Atomic simple type: {http:///com/nokia/oss/fm/types.ecore}ProbableCause
class ProbableCause (pyxb.binding.datatypes.nonNegativeInteger):

    """ProbableCause qualifies the probable cause of the alarm. See NSN OFaS specification, IETF RFC-3877, ITU-T X.733, ITU-T X.736 and 3GPP TS 32.111-3."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'ProbableCause')
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\fmTypes_1.0-2.xsd', 85, 1)
    _Documentation = 'ProbableCause qualifies the probable cause of the alarm. See NSN OFaS specification, IETF RFC-3877, ITU-T X.733, ITU-T X.736 and 3GPP TS 32.111-3.'
ProbableCause._CF_maxInclusive = pyxb.binding.facets.CF_maxInclusive(value_datatype=ProbableCause, value=pyxb.binding.datatypes.nonNegativeInteger(2147483647))
ProbableCause._InitializeFacetMap(ProbableCause._CF_maxInclusive)
Namespace.addCategoryObject('typeBinding', 'ProbableCause', ProbableCause)
