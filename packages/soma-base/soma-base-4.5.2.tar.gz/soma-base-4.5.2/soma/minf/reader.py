# -*- coding: iso-8859-1 -*-

#  This software and supporting documentation are distributed by
#      Institut Federatif de Recherche 49
#      CEA/NeuroSpin, Batiment 145,
#      91191 Gif-sur-Yvette cedex
#      France
#
# This software is governed by the CeCILL-B license under
# French law and abiding by the rules of distribution of free software.
# You can  use, modify and/or redistribute the software under the 
# terms of the CeCILL-B license as circulated by CEA, CNRS
# and INRIA at the following URL "http://www.cecill.info". 
# 
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL-B license and that you accept its terms.


'''
Base classes for reading various minf formats (XML, HDF5, Python's pickle, etc.)

@author: Yann Cointepas
@organization: U{NeuroSpin<http://www.neurospin.org>} and U{IFR 49<http://www.ifr49.org>}
@license: U{CeCILL version 2<http://www.cecill.info/licences/Licence_CeCILL_V2-en.html>}
'''

__docformat__ = "epytext en"


from soma.translation import translate as _

#------------------------------------------------------------------------------
class RegisterMinfReaderClass( type ):
  '''
  RegisterMinfReaderClass is used as metaclass of L{MinfReader} to automatically
  register all classes derived from L{MinfReader}.
  '''
  def __init__( cls, name, bases, dict ):
    if cls.name is not None:
      MinfReader._allReaderClasses[ cls.name ] = cls


#------------------------------------------------------------------------------
class MinfReader( object ):
  '''
  Class derived from MinfReader are responsible of reading a specific format of
  minf file. This version only support XML format but other formats may be added
  later (such as HDF5).
  All classes derived from L{MinfReader} must define a L{name} class attribute
  and L{nodeIterator} method. The constructor of L{MinfReader} derived class
  must be callable without arguments (except C{self}), it does not have to be
  overloaded.
  '''
  __metaclass__ = RegisterMinfReaderClass
  
  #: all classes derived from L{MinfReader} are automatically stored in that
  #: dictionary (keys are formats name and values are class objects).
  _allReaderClasses = {}

  #: class derived from L{MinfReader} must set a format name in this attribute.
  name = None
  
  
  
  def createReader( format ):
    '''
    This static method create a L{MinfReader} instance by looking for a registered
    L{MinfReader} derived classes named C{format}.
    @param format: name of the minf format.
    @type  format: string
    @returns: L{MinfReader} derived class instance.
    '''
    reader = MinfReader._allReaderClasses.get( format )
    if reader is None:
      raise( _( 'No minf reader for format "%(format)s", possible formats are: %(possible)s' ) % \
             { 'format': format, 'possible': ', '.join( ['"' + i + '"' for i in MinfReader._allReaderClasses ] ) } )
    return reader()
  createReader = staticmethod( createReader )


  def reduction( self, source ):
    '''
    Return a pair C{( reduction, buffer )} where C{reduction} is the name of
    the L{MinfReducer<soma.minf.tree.MinfReducer} stored in the minf file and
    C{buffer} is the data that have been read from file.
    '''
  def nodeIterator( self, source ):
    '''
    Return an iterator on all the nodes of the minf tree corresponding to the content
    of the C{source} minf file.
    @param source: source of the minf file.
    @type  source: string of file object
    '''
