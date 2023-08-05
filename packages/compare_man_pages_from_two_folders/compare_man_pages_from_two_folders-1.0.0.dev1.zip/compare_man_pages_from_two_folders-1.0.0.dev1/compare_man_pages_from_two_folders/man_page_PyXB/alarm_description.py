# .\alarm_description.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:acf72e8f9a9ecc4c5bd25f4200c0767ac58121b5
# Generated 2015-02-10 12:58:25.901000 by PyXB version 1.2.4 using Python 2.7.6.final.0
# Namespace http:///com/nokia/oss/fm/fmbasic.ecore

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
import com.nokia.oss.fm._types as _ImportedBinding_com_nokia_oss_fm__types
import pyxb.binding.datatypes
import pyxb.binding.xml_
import _base as _ImportedBinding__base

# NOTE: All namespace declarations are reserved within the binding
Namespace = pyxb.namespace.NamespaceForURI('http:///com/nokia/oss/fm/fmbasic.ecore', create_if_missing=True)
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


# Atomic simple type: {http:///com/nokia/oss/fm/fmbasic.ecore}EventType
class EventType (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """Re-declaration of EventType to add processing and indeterminate enums used in some man pages. Also there is no "communications" duplicate, use the "communication"."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'EventType')
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 85, 1)
    _Documentation = 'Re-declaration of EventType to add processing and indeterminate enums used in some man pages. Also there is no "communications" duplicate, use the "communication".'
EventType._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=EventType, enum_prefix=None)
EventType.communication = EventType._CF_enumeration.addEnumeration(unicode_value='communication', tag='communication')
EventType.environmental = EventType._CF_enumeration.addEnumeration(unicode_value='environmental', tag='environmental')
EventType.equipment = EventType._CF_enumeration.addEnumeration(unicode_value='equipment', tag='equipment')
EventType.processing = EventType._CF_enumeration.addEnumeration(unicode_value='processing', tag='processing')
EventType.processingError = EventType._CF_enumeration.addEnumeration(unicode_value='processingError', tag='processingError')
EventType.qualityOfService = EventType._CF_enumeration.addEnumeration(unicode_value='qualityOfService', tag='qualityOfService')
EventType.integrityViolation = EventType._CF_enumeration.addEnumeration(unicode_value='integrityViolation', tag='integrityViolation')
EventType.operationalViolation = EventType._CF_enumeration.addEnumeration(unicode_value='operationalViolation', tag='operationalViolation')
EventType.physicalViolation = EventType._CF_enumeration.addEnumeration(unicode_value='physicalViolation', tag='physicalViolation')
EventType.securityViolation = EventType._CF_enumeration.addEnumeration(unicode_value='securityViolation', tag='securityViolation')
EventType.timeDomainViolation = EventType._CF_enumeration.addEnumeration(unicode_value='timeDomainViolation', tag='timeDomainViolation')
EventType.indeterminate = EventType._CF_enumeration.addEnumeration(unicode_value='indeterminate', tag='indeterminate')
EventType._InitializeFacetMap(EventType._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'EventType', EventType)

# Atomic simple type: {http:///com/nokia/oss/fm/fmbasic.ecore}TextDocumentation
class TextDocumentation (pyxb.binding.datatypes.string):

    """Free text documentation type for Alarm Description text attributes."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TextDocumentation')
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 152, 1)
    _Documentation = 'Free text documentation type for Alarm Description text attributes.'
TextDocumentation._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(200000))
TextDocumentation._CF_pattern = pyxb.binding.facets.CF_pattern()
TextDocumentation._CF_pattern.addPattern(pattern='[\t\n\r -~\xa0-\ud7ff\uf900-\ufffd]*')
TextDocumentation._InitializeFacetMap(TextDocumentation._CF_maxLength,
   TextDocumentation._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'TextDocumentation', TextDocumentation)

# Atomic simple type: {http:///com/nokia/oss/fm/fmbasic.ecore}SchemaVersion
class SchemaVersion (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """Versioning type for this schema."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'SchemaVersion')
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 161, 1)
    _Documentation = 'Versioning type for this schema.'
SchemaVersion._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=SchemaVersion, enum_prefix=None)
SchemaVersion.n1_0 = SchemaVersion._CF_enumeration.addEnumeration(unicode_value='1.0', tag='n1_0')
SchemaVersion.n1_0_2 = SchemaVersion._CF_enumeration.addEnumeration(unicode_value='1.0-2', tag='n1_0_2')
SchemaVersion._InitializeFacetMap(SchemaVersion._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'SchemaVersion', SchemaVersion)

# Atomic simple type: {http:///com/nokia/oss/fm/fmbasic.ecore}InterfaceVersion
class InterfaceVersion (pyxb.binding.datatypes.string):

    """Interface specification versioning type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'InterfaceVersion')
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 170, 1)
    _Documentation = 'Interface specification versioning type.'
InterfaceVersion._CF_pattern = pyxb.binding.facets.CF_pattern()
InterfaceVersion._CF_pattern.addPattern(pattern='\\d{1,2}\\.\\d{1,2}(-\\d{1,2})?')
InterfaceVersion._InitializeFacetMap(InterfaceVersion._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'InterfaceVersion', InterfaceVersion)

# Complex type {http:///com/nokia/oss/fm/fmbasic.ecore}AlarmDescription with content type ELEMENT_ONLY
class AlarmDescription_ (_ImportedBinding__base.AdaptationFragment):
    """Type definition for the Alarm Description."""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'AlarmDescription')
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 12, 1)
    _ElementMap = _ImportedBinding__base.AdaptationFragment._ElementMap.copy()
    _AttributeMap = _ImportedBinding__base.AdaptationFragment._AttributeMap.copy()
    # Base type is _ImportedBinding__base.AdaptationFragment
    
    # Element annotations (annotations) inherited from {http:///com/nokia/oss/common.ecore}AdaptationFragment
    
    # Element Adaptation (Adaptation) inherited from {http:///com/nokia/oss/common.ecore}AdaptationFragment
    
    # Attribute patchLevel inherited from {http:///com/nokia/oss/common.ecore}AdaptationFragment
    
    # Attribute {http://www.w3.org/XML/1998/namespace}lang uses Python identifier lang
    __lang = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(pyxb.namespace.XML, 'lang'), 'lang', '__httpcomnokiaossfmfmbasic_ecore_AlarmDescription__httpwww_w3_orgXML1998namespacelang', pyxb.binding.xml_.STD_ANON_lang, unicode_default='en')
    __lang._DeclarationLocation = None
    __lang._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 18, 4)
    
    lang = property(__lang.value, __lang.set, None, None)

    
    # Attribute schemaVersion uses Python identifier schemaVersion
    __schemaVersion = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'schemaVersion'), 'schemaVersion', '__httpcomnokiaossfmfmbasic_ecore_AlarmDescription__schemaVersion', SchemaVersion)
    __schemaVersion._DeclarationLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 19, 4)
    __schemaVersion._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 19, 4)
    
    schemaVersion = property(__schemaVersion.value, __schemaVersion.set, None, 'AlarmDescription schema version used for implementing this alarm description instance. \nAlarm Description schema version format is R.V[-C] where R=Release, V=Version, C=Correction. The correction part is optional (2.0 equals 2.0-0). Version and Correction increases are backward/forward compatible, meaning a parser generated from schema version 2.3 can parse any 2.V[-C] document, even newer versions like 2.4 (ignoring new parts). Release increases MAY NOT be backward or future compatible.')

    
    # Attribute interfaceVersion uses Python identifier interfaceVersion
    __interfaceVersion = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'interfaceVersion'), 'interfaceVersion', '__httpcomnokiaossfmfmbasic_ecore_AlarmDescription__interfaceVersion', InterfaceVersion)
    __interfaceVersion._DeclarationLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 25, 4)
    __interfaceVersion._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 25, 4)
    
    interfaceVersion = property(__interfaceVersion.value, __interfaceVersion.set, None, 'Alarm Description interface specification version (version of this word document) used for implementing this alarm description instance. Format is R.V[-C] where R=Release, V=Version, C=Correction. The correction part is optional (1.0 equals to 1.0-0).\nNetAct MUST NOT implement any functionality using this attribute.\n')

    
    # Attribute specificProblem uses Python identifier specificProblem
    __specificProblem = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'specificProblem'), 'specificProblem', '__httpcomnokiaossfmfmbasic_ecore_AlarmDescription__specificProblem', _ImportedBinding_com_nokia_oss_fm__types.SpecificProblem, required=True)
    __specificProblem._DeclarationLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 32, 4)
    __specificProblem._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 32, 4)
    
    specificProblem = property(__specificProblem.value, __specificProblem.set, None, 'This attribute is used as a key between alarm event and alarm description. It shall be unique within the scope of adaptation Id. ')

    
    # Attribute alarmText uses Python identifier alarmText
    __alarmText = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alarmText'), 'alarmText', '__httpcomnokiaossfmfmbasic_ecore_AlarmDescription__alarmText', _ImportedBinding_com_nokia_oss_fm__types.AlarmText, required=True)
    __alarmText._DeclarationLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 37, 4)
    __alarmText._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 37, 4)
    
    alarmText = property(__alarmText.value, __alarmText.set, None, 'This attribute should be equal to the alarmText in alarm notification.')

    
    # Attribute probableCause uses Python identifier probableCause
    __probableCause = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'probableCause'), 'probableCause', '__httpcomnokiaossfmfmbasic_ecore_AlarmDescription__probableCause', _ImportedBinding_com_nokia_oss_fm__types.ProbableCause)
    __probableCause._DeclarationLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 42, 4)
    __probableCause._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 42, 4)
    
    probableCause = property(__probableCause.value, __probableCause.set, None, 'This attribute should be equal to the probableCause in alarm notification. See OFaS specification for list of supported values. If the probableCause is not constant for the specificProblem, this attribute should be omitted.')

    
    # Attribute alarmType uses Python identifier alarmType
    __alarmType = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'alarmType'), 'alarmType', '__httpcomnokiaossfmfmbasic_ecore_AlarmDescription__alarmType', EventType)
    __alarmType._DeclarationLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 47, 4)
    __alarmType._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 47, 4)
    
    alarmType = property(__alarmType.value, __alarmType.set, None, 'This attribute should be equal to the EventType in alarm notification. See documentation of the datatype for more details. If the alarmType/eventType is not constant for the specificProblem, this attribute should be omitted.')

    
    # Attribute meaning uses Python identifier meaning
    __meaning = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'meaning'), 'meaning', '__httpcomnokiaossfmfmbasic_ecore_AlarmDescription__meaning', TextDocumentation)
    __meaning._DeclarationLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 52, 4)
    __meaning._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 52, 4)
    
    meaning = property(__meaning.value, __meaning.set, None, 'Free text field for documenting the meaning of the alarm.')

    
    # Attribute effect uses Python identifier effect
    __effect = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'effect'), 'effect', '__httpcomnokiaossfmfmbasic_ecore_AlarmDescription__effect', TextDocumentation)
    __effect._DeclarationLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 57, 4)
    __effect._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 57, 4)
    
    effect = property(__effect.value, __effect.set, None, 'Free text field for documenting the effects of the alarm.')

    
    # Attribute supplementaryInformationFields uses Python identifier supplementaryInformationFields
    __supplementaryInformationFields = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'supplementaryInformationFields'), 'supplementaryInformationFields', '__httpcomnokiaossfmfmbasic_ecore_AlarmDescription__supplementaryInformationFields', TextDocumentation)
    __supplementaryInformationFields._DeclarationLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 62, 4)
    __supplementaryInformationFields._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 62, 4)
    
    supplementaryInformationFields = property(__supplementaryInformationFields.value, __supplementaryInformationFields.set, None, 'Free text field for documenting any supplementary information about the alarm.')

    
    # Attribute instructions uses Python identifier instructions
    __instructions = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'instructions'), 'instructions', '__httpcomnokiaossfmfmbasic_ecore_AlarmDescription__instructions', TextDocumentation)
    __instructions._DeclarationLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 67, 4)
    __instructions._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 67, 4)
    
    instructions = property(__instructions.value, __instructions.set, None, 'Free text field for documenting instructions for the alarm.')

    
    # Attribute cancelling uses Python identifier cancelling
    __cancelling = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'cancelling'), 'cancelling', '__httpcomnokiaossfmfmbasic_ecore_AlarmDescription__cancelling', TextDocumentation)
    __cancelling._DeclarationLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 72, 4)
    __cancelling._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 72, 4)
    
    cancelling = property(__cancelling.value, __cancelling.set, None, 'Free text field for documenting cancelling of the alarm.')

    
    # Attribute perceivedSeverityInfo uses Python identifier perceivedSeverityInfo
    __perceivedSeverityInfo = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'perceivedSeverityInfo'), 'perceivedSeverityInfo', '__httpcomnokiaossfmfmbasic_ecore_AlarmDescription__perceivedSeverityInfo', TextDocumentation)
    __perceivedSeverityInfo._DeclarationLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 77, 4)
    __perceivedSeverityInfo._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 77, 4)
    
    perceivedSeverityInfo = property(__perceivedSeverityInfo.value, __perceivedSeverityInfo.set, None, 'Free text field for documenting alarm severity information. (If alarm always has constant severity, or if alarm severity is a variable based on some threshold (like disk fill ratio percentage (70-80% minor, 80-90% major, 90-100% critical). ')

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=set(['http://www.omg.org/XMI']))
    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __lang.name() : __lang,
        __schemaVersion.name() : __schemaVersion,
        __interfaceVersion.name() : __interfaceVersion,
        __specificProblem.name() : __specificProblem,
        __alarmText.name() : __alarmText,
        __probableCause.name() : __probableCause,
        __alarmType.name() : __alarmType,
        __meaning.name() : __meaning,
        __effect.name() : __effect,
        __supplementaryInformationFields.name() : __supplementaryInformationFields,
        __instructions.name() : __instructions,
        __cancelling.name() : __cancelling,
        __perceivedSeverityInfo.name() : __perceivedSeverityInfo
    })
Namespace.addCategoryObject('typeBinding', 'AlarmDescription', AlarmDescription_)


AlarmDescription = pyxb.binding.basis.element(pyxb.namespace.ExpandedName(Namespace, 'AlarmDescription'), AlarmDescription_, documentation='Alarm manual page root element. There can be only one element in a file. ', location=pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\ad_1.0-2.xsd', 7, 1))
Namespace.addCategoryObject('elementBinding', AlarmDescription.name().localName(), AlarmDescription)



def _BuildAutomaton ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton
    del _BuildAutomaton
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 15, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AlarmDescription_._UseForTag(pyxb.namespace.ExpandedName(None, 'annotations')), pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 15, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(AlarmDescription_._UseForTag(pyxb.namespace.ExpandedName(None, 'Adaptation')), pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 16, 3))
    st_1 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_1)
    transitions = []
    transitions.append(fac.Transition(st_0, [
        fac.UpdateInstruction(cc_0, True) ]))
    transitions.append(fac.Transition(st_1, [
        fac.UpdateInstruction(cc_0, False) ]))
    st_0._set_transitionSet(transitions)
    transitions = []
    st_1._set_transitionSet(transitions)
    return fac.Automaton(states, counters, False, containing_state=None)
AlarmDescription_._Automaton = _BuildAutomaton()

