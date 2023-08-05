#!/usr/bin/env python
# md5: f89258bb6043eac96b17264408e5073e
# coding: utf-8

"""
JsObj is simple implementation JavaScript-Style Objects in Python.

Homepage and documentation: http://github.com/gkovacs/jsobj

Copyright (c) 2014, Geza Kovacs. Based on JsObject by Marcin Wierzbanowski.
License: MIT (see LICENSE for details)
"""
#from __future__ import with_statement
#import os
#try:
#  HERE = os.path.abspath(os.path.dirname(__file__))
#except:
#  HERE = os.path.abspath(os.getcwd())

__author__ = 'Geza Kovacs'
#__version__ = open(os.path.join(HERE, 'VERSION')).read()[:-1]
__version__ = '1.0.0'
__license__ = 'MIT'


def to_jsobj(v):
  if type(v) == dict:
    return Object(v)
  if type(v) == list:
    return [to_jsobj(x) for x in v]
  return v

class Object(object):
  """ This is a base class """

  def __init__(self, data={}):
    if type(data) not in (dict, Object):
      raise TypeError("argument must be dict, not %s"
              % type(data).__name__)

    for k, v in self.__get(data).items():
      self.__dict__[k] = self.__set(v)

  def __getattr__(self, k):
    if k not in self.__dict__:
      return None
    else:
      return self.__dict__[k]

  def __setattr__(self, k, v):
    self.__dict__[k] = Object(v) if type(v) == dict else v

  def get(self):
      return dict((k, self.__get(v)) for (k, v) in self.__dict__.items())

  def __get(self, v):
    #return v.get() if type(v) == Object else v
    return v

  def __set(self, v):
    #return Object(v) if type(v) == dict else v
    return to_jsobj(v)

  def __str__(self):
    #return str(self.get())
    return self.__dict__.__str__()

  def __repr__(self):
    #return str(self.get())
    return self.__dict__.__repr__()

  def __eq__(self, other):
    return str(self) == str(other)

  def __contains__(self, k):
    return k in self.__dict__

  def __len__(self):
    return len(self.__dict__)

  def __getitem__(self, k):
    if k not in self.__dict__:
      return None
    else:
      return self.__dict__[k]

  def __setitem__(self, k, v):
    #self.__dict__[k] = Object(v) if type(v) == dict else v
    self.__dict__[k] = to_jsobj(v)

  def __iter__(self):
    return self.__dict__.__iter__()

  def iteritems(self):
    return self.__dict__.iteritems()

  def items(self):
    return self.__dict__.items()

  def keys(self):
    return self.__dict__.keys()

  def iterkeys(self):
    return self.__dict__.iterkeys()

  def values(self):
    return self.__dict__.values()

  def itervalues(self):
    return self.__dict__.itervalues()


