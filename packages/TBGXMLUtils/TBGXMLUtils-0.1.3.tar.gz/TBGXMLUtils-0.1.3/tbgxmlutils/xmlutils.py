#!/usr/bin/env python

from xml.dom import minidom
import lxml.etree as ET
import xmltodict

def add(k, parent=None, txt=None, attrs=None):
  if parent is None:
    handle = ET.Element(k)
  else:
    handle = ET.SubElement(parent, k)
  if txt: handle.text = unicode(txt)
  try:
    for k, v in attrs.iteritems(): handle.attrib[k] = v
  except AttributeError:
    pass
  return handle

def etree2xml(e, encoding='UTF-8'): 
  return ET.tostring(e, encoding=encoding) if encoding else ET.tostring(e)

def pretty(xml=None, fn=None, encoding=None):
  if fn is not None:
    xml = minidom.parse(fn)
  elif not isinstance(xml, minidom.Document):
    xml = minidom.parseString(xml)
  return xml.toprettyxml(indent='  ', encoding=encoding)

def xml_fn_to_json(fn):
  fh = open(fn, 'r')
  json = xmltodict.parse(fh.read())
  return json

