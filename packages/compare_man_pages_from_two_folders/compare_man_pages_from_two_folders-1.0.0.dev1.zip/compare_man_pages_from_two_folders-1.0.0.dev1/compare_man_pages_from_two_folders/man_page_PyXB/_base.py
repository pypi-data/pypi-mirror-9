# .\_base.py
# -*- coding: utf-8 -*-
# PyXB bindings for NM:a8c19d201cbc238105e8e5400b5083e1cfe981ef
# Generated 2015-02-10 12:58:25.899000 by PyXB version 1.2.4 using Python 2.7.6.final.0
# Namespace http:///com/nokia/oss/common.ecore [xmlns:base]

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
Namespace = pyxb.namespace.NamespaceForURI('http:///com/nokia/oss/common.ecore', create_if_missing=True)
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


# Atomic simple type: [anonymous]
class STD_ANON (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 19, 3)
    _Documentation = None
STD_ANON._CF_pattern = pyxb.binding.facets.CF_pattern()
STD_ANON._CF_pattern.addPattern(pattern='[0-9]{2}\\.[0-9]{3}')
STD_ANON._InitializeFacetMap(STD_ANON._CF_pattern)

# Atomic simple type: [anonymous]
class STD_ANON_ (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 50, 3)
    _Documentation = None
STD_ANON_._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(2000))
STD_ANON_._InitializeFacetMap(STD_ANON_._CF_maxLength)

# Atomic simple type: [anonymous]
class STD_ANON_2 (pyxb.binding.datatypes.normalizedString):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 65, 3)
    _Documentation = None
STD_ANON_2._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(100))
STD_ANON_2._InitializeFacetMap(STD_ANON_2._CF_maxLength)

# Atomic simple type: [anonymous]
class STD_ANON_3 (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = None
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 72, 3)
    _Documentation = None
STD_ANON_3._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(2000))
STD_ANON_3._InitializeFacetMap(STD_ANON_3._CF_maxLength)

# Atomic simple type: {http:///com/nokia/oss/common.ecore}id
class id (pyxb.binding.datatypes.string):

    """An atomic simple type."""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'id')
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 79, 1)
    _Documentation = None
id._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(30))
id._CF_pattern = pyxb.binding.facets.CF_pattern()
id._CF_pattern.addPattern(pattern='[a-zA-Z][_A-Za-z0-9]*')
id._InitializeFacetMap(id._CF_maxLength,
   id._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'id', id)

# Atomic simple type: {http:///com/nokia/oss/common.ecore}inverseDN
class inverseDN (pyxb.binding.datatypes.string):

    """
        Inverse domain name with one or more dot-separated sections and  has no more than 64 characters. Each section starts with an alphabetical character, followed by optional alphanumeric or underscore characters.
      """

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'inverseDN')
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 85, 1)
    _Documentation = '\n        Inverse domain name with one or more dot-separated sections and  has no more than 64 characters. Each section starts with an alphabetical character, followed by optional alphanumeric or underscore characters.\n      '
inverseDN._CF_maxLength = pyxb.binding.facets.CF_maxLength(value=pyxb.binding.datatypes.nonNegativeInteger(64))
inverseDN._CF_minLength = pyxb.binding.facets.CF_minLength(value=pyxb.binding.datatypes.nonNegativeInteger(1))
inverseDN._CF_pattern = pyxb.binding.facets.CF_pattern()
inverseDN._CF_pattern.addPattern(pattern='[a-zA-Z][_a-zA-Z0-9]*(\\.[a-zA-Z][_a-zA-Z0-9]*)*')
inverseDN._InitializeFacetMap(inverseDN._CF_maxLength,
   inverseDN._CF_minLength,
   inverseDN._CF_pattern)
Namespace.addCategoryObject('typeBinding', 'inverseDN', inverseDN)

# Atomic simple type: {http:///com/nokia/oss/common.ecore}TypeId
class TypeId (pyxb.binding.datatypes.string, pyxb.binding.basis.enumeration_mixin):

    """Primitive types used by adaptations"""

    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'TypeId')
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 97, 1)
    _Documentation = 'Primitive types used by adaptations'
TypeId._CF_enumeration = pyxb.binding.facets.CF_enumeration(value_datatype=TypeId, enum_prefix=None)
TypeId.TID_NONE = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_NONE', tag='TID_NONE')
TypeId.TID_STRING = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_STRING', tag='TID_STRING')
TypeId.TID_SHORT = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_SHORT', tag='TID_SHORT')
TypeId.TID_INT = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_INT', tag='TID_INT')
TypeId.TID_LONG = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_LONG', tag='TID_LONG')
TypeId.TID_OCTET = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_OCTET', tag='TID_OCTET')
TypeId.TID_BOOL = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_BOOL', tag='TID_BOOL')
TypeId.TID_DOUBLE = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_DOUBLE', tag='TID_DOUBLE')
TypeId.TID_CHAR = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_CHAR', tag='TID_CHAR')
TypeId.TID_USHORT = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_USHORT', tag='TID_USHORT')
TypeId.TID_UINT = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_UINT', tag='TID_UINT')
TypeId.TID_ULONG = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_ULONG', tag='TID_ULONG')
TypeId.TID_DATETIME = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_DATETIME', tag='TID_DATETIME')
TypeId.TID_INTEGER = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_INTEGER', tag='TID_INTEGER')
TypeId.TID_DECIMAL = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_DECIMAL', tag='TID_DECIMAL')
TypeId.TID_ENCRYPTED_STRING = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_ENCRYPTED_STRING', tag='TID_ENCRYPTED_STRING')
TypeId.TID_OBJ_REF = TypeId._CF_enumeration.addEnumeration(unicode_value='TID_OBJ_REF', tag='TID_OBJ_REF')
TypeId.MTID_MODEL_ELEMENT = TypeId._CF_enumeration.addEnumeration(unicode_value='MTID_MODEL_ELEMENT', tag='MTID_MODEL_ELEMENT')
TypeId.MTID_CLASS_DEF = TypeId._CF_enumeration.addEnumeration(unicode_value='MTID_CLASS_DEF', tag='MTID_CLASS_DEF')
TypeId.MTID_CONTEXT_ELEMENT = TypeId._CF_enumeration.addEnumeration(unicode_value='MTID_CONTEXT_ELEMENT', tag='MTID_CONTEXT_ELEMENT')
TypeId._InitializeFacetMap(TypeId._CF_enumeration)
Namespace.addCategoryObject('typeBinding', 'TypeId', TypeId)

# Complex type {http:///com/nokia/oss/common.ecore}reference with content type EMPTY
class reference (pyxb.binding.basis.complexTypeDefinition):
    """
        Used to generate elements with only one attribute, which is an
        reference to another adaptation element.
      """
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'reference')
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 27, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute href uses Python identifier href
    __href = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'href'), 'href', '__httpcomnokiaosscommon_ecore_reference_href', pyxb.binding.datatypes.anyURI, required=True)
    __href._DeclarationLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 34, 2)
    __href._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 34, 2)
    
    href = property(__href.value, __href.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __href.name() : __href
    })
Namespace.addCategoryObject('typeBinding', 'reference', reference)


# Complex type {http:///com/nokia/oss/common.ecore}annotation with content type ELEMENT_ONLY
class annotation (pyxb.binding.basis.complexTypeDefinition):
    """
        Used to add annotation cabability for elements
      """
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'annotation')
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 36, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element elements uses Python identifier elements
    __elements = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'elements'), 'elements', '__httpcomnokiaosscommon_ecore_annotation_elements', True, pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 43, 3), )

    
    elements = property(__elements.value, __elements.set, None, None)

    
    # Element type uses Python identifier type
    __type = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'type'), 'type', '__httpcomnokiaosscommon_ecore_annotation_type', False, pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 44, 3), )

    
    type = property(__type.value, __type.set, None, None)

    _ElementMap.update({
        __elements.name() : __elements,
        __type.name() : __type
    })
    _AttributeMap.update({
        
    })
Namespace.addCategoryObject('typeBinding', 'annotation', annotation)


# Complex type {http:///com/nokia/oss/common.ecore}AdaptationFragment with content type ELEMENT_ONLY
class AdaptationFragment (pyxb.binding.basis.complexTypeDefinition):
    """
        Used as a base for new adaptation fragments
      """
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_ELEMENT_ONLY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'AdaptationFragment')
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 8, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Element annotations uses Python identifier annotations
    __annotations = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'annotations'), 'annotations', '__httpcomnokiaosscommon_ecore_AdaptationFragment_annotations', True, pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 15, 3), )

    
    annotations = property(__annotations.value, __annotations.set, None, None)

    
    # Element Adaptation uses Python identifier Adaptation
    __Adaptation = pyxb.binding.content.ElementDeclaration(pyxb.namespace.ExpandedName(None, 'Adaptation'), 'Adaptation', '__httpcomnokiaosscommon_ecore_AdaptationFragment_Adaptation', False, pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 16, 3), )

    
    Adaptation = property(__Adaptation.value, __Adaptation.set, None, None)

    
    # Attribute patchLevel uses Python identifier patchLevel
    __patchLevel = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'patchLevel'), 'patchLevel', '__httpcomnokiaosscommon_ecore_AdaptationFragment_patchLevel', STD_ANON)
    __patchLevel._DeclarationLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 18, 2)
    __patchLevel._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 18, 2)
    
    patchLevel = property(__patchLevel.value, __patchLevel.set, None, None)

    _AttributeWildcard = pyxb.binding.content.Wildcard(process_contents=pyxb.binding.content.Wildcard.PC_lax, namespace_constraint=set(['http://www.omg.org/XMI']))
    _ElementMap.update({
        __annotations.name() : __annotations,
        __Adaptation.name() : __Adaptation
    })
    _AttributeMap.update({
        __patchLevel.name() : __patchLevel
    })
Namespace.addCategoryObject('typeBinding', 'AdaptationFragment', AdaptationFragment)


# Complex type {http:///com/nokia/oss/common.ecore}annotationElement with content type EMPTY
class annotationElement (pyxb.binding.basis.complexTypeDefinition):
    """Complex type {http:///com/nokia/oss/common.ecore}annotationElement with content type EMPTY"""
    _TypeDefinition = None
    _ContentTypeTag = pyxb.binding.basis.complexTypeDefinition._CT_EMPTY
    _Abstract = False
    _ExpandedName = pyxb.namespace.ExpandedName(Namespace, 'annotationElement')
    _XSDLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 47, 1)
    _ElementMap = {}
    _AttributeMap = {}
    # Base type is pyxb.binding.datatypes.anyType
    
    # Attribute name uses Python identifier name
    __name = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'name'), 'name', '__httpcomnokiaosscommon_ecore_annotationElement_name', id, required=True)
    __name._DeclarationLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 48, 2)
    __name._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 48, 2)
    
    name = property(__name.value, __name.set, None, None)

    
    # Attribute value uses Python identifier value_
    __value = pyxb.binding.content.AttributeUse(pyxb.namespace.ExpandedName(None, 'value'), 'value_', '__httpcomnokiaosscommon_ecore_annotationElement_value', STD_ANON_)
    __value._DeclarationLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 49, 2)
    __value._UseLocation = pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 49, 2)
    
    value_ = property(__value.value, __value.set, None, None)

    _ElementMap.update({
        
    })
    _AttributeMap.update({
        __name.name() : __name,
        __value.name() : __value
    })
Namespace.addCategoryObject('typeBinding', 'annotationElement', annotationElement)




annotation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'elements'), annotationElement, scope=annotation, location=pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 43, 3)))

annotation._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'type'), reference, scope=annotation, location=pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 44, 3)))

def _BuildAutomaton ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton
    del _BuildAutomaton
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 43, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(annotation._UseForTag(pyxb.namespace.ExpandedName(None, 'elements')), pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 43, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(annotation._UseForTag(pyxb.namespace.ExpandedName(None, 'type')), pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 44, 3))
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
annotation._Automaton = _BuildAutomaton()




AdaptationFragment._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'annotations'), annotation, scope=AdaptationFragment, location=pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 15, 3)))

AdaptationFragment._AddElement(pyxb.binding.basis.element(pyxb.namespace.ExpandedName(None, 'Adaptation'), reference, scope=AdaptationFragment, location=pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 16, 3)))

def _BuildAutomaton_ ():
    # Remove this helper function from the namespace after it is invoked
    global _BuildAutomaton_
    del _BuildAutomaton_
    import pyxb.utils.fac as fac

    counters = set()
    cc_0 = fac.CounterCondition(min=0, max=None, metadata=pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 15, 3))
    counters.add(cc_0)
    states = []
    final_update = None
    symbol = pyxb.binding.content.ElementUse(AdaptationFragment._UseForTag(pyxb.namespace.ExpandedName(None, 'annotations')), pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 15, 3))
    st_0 = fac.State(symbol, is_initial=True, final_update=final_update, is_unordered_catenation=False)
    states.append(st_0)
    final_update = set()
    symbol = pyxb.binding.content.ElementUse(AdaptationFragment._UseForTag(pyxb.namespace.ExpandedName(None, 'Adaptation')), pyxb.utils.utility.Location('D:\\userdata\\k2lin\\PycharmProjects\\compare_man_pages_from_two_folders\\man_page_PyXB\\base_1.0.xsd', 16, 3))
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
AdaptationFragment._Automaton = _BuildAutomaton_()

