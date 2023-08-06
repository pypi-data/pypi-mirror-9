# -*- coding: utf-8 -*-

import re
from inspect import isfunction, isclass, ismethod
from weakref import WeakKeyDictionary

from soma.singleton import Singleton

class GlobalNaming( Singleton ):
  def __singleton_init__( self ):
    super( GlobalNaming, self ).__singleton_init__()
    self._global_name_re = re.compile( r'(([A-Za-z][A-Za-z0-9_.]*)\.([A-Za-z0-9_]+))(\(\))?((\.)([A-Za-z][A-Za-z0-9_.]+))?' )
    self._names = WeakKeyDictionary()


  def parse_global_name( self, global_name ):
    m = self._global_name_re.match( global_name )
    if m:
      # return module, name, args, attributes
      return m.group(2), m.group(3), ( () if m.group(4) else None ), m.group(7)
    raise ValueError( 'Invalid global name syntax: ' + global_name )


  def get_object( self, global_name ):
    module, name, args, attributes = self.parse_global_name( global_name )
    module = __import__( module, fromlist=[ name ], level=0 )
    try:
      value = getattr( module, name )
    except AttributeError, e:
      raise ImportError( str( e ) )
    if args is not None:
      value = value( *args )
    if attributes:
      for a in attributes.split( '.' ):
        value = getattr( value, a )
      self._names[ value ] = global_name
    return value

  
  def get_name( self, obj ):
    result = self._names.get( obj )
    if result is not None:
      return result
    if isfunction( obj ) or isclass( obj ):
      return obj.__module__ + '.' + obj.__name__
    elif ismethod( obj ):
      if obj.im_self is not None:
        return obj.im_class.__module__ + '.' + obj.im_class.__name__ + '().' + obj.im_func.__name__
    elif isinstance( obj, object ):
      return obj.__class__.__module__ + '.' + obj.__class__.__name__ + '()'
    raise ValueError( 'Cannot find global name for %s' % repr( obj ) )

    
def get_object( global_name ):
  return GlobalNaming().get_object( global_name )

  
def get_name( obj ):
  return GlobalNaming().get_name( obj )
