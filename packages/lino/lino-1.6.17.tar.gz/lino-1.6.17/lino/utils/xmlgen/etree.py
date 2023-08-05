"""
Based on Amaury's adaption of Eli Golovinsky's post
http://stackoverflow.com/questions/174890/how-to-output-cdata-using-elementtree

Gooli's original snippet didn't work in Python 2.7

Added by LS:
- support for _serialize_xml having different number of args depending on Python version
- register_namespace is not in __all__

"""
import xml.etree.ElementTree as etree

if hasattr(etree, '_serialize_xml'):

    def CDATA(text=None):
        element = etree.Element('![CDATA[')
        element.text = text
        return element

    _original_serialize_xml = etree._serialize_xml

    def _serialize_xml(write, elem, *args):
        if elem.tag == '![CDATA[':
            write("\n<%s%s]]>\n" % (
                elem.tag, elem.text))
            return
        return _original_serialize_xml(write, elem, *args)
    etree._serialize_xml = etree._serialize['xml'] = _serialize_xml

    register_namespace = etree.register_namespace

else:
    def register_namespace(*args, **kw):
        pass

from xml.etree.ElementTree import *
