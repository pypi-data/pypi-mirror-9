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
This module is useful whenever you need to be sure that a function (more
exactly anything that can be called by python) is executed in a particular
thread. 

For exemple, if you use PyMat (which is an interface between Python and a Matlab,
see U{http://claymore.engineer.gvsu.edu/~steriana/Python} for more information) 
it is necessary that all calls to pymat.eval are done by the same thread that
called pymat.open. If you want to use PyMat in a multi-threaded application,
you will have to build appropriate calling mechanism as the one proposed in
this module.

The main idea is to use a list containing functions to be called with their
parameters. A single thread is used to get entries from the list and execute
the corresponding functions. Any thread can put a call request on the list
either asynchonously (the requesting thread continues to run without waiting
for the call to be done) or synchronously (the requesting thread is stopped
until the call is done and the result available).

@author: Yann Cointepas
@organization: U{NeuroSpin<http://www.neurospin.org>} and U{IFR 49<http://www.ifr49.org>}
@license: U{CeCILL version 2<http://www.cecill.info/licences/Licence_CeCILL_V2-en.html>}
'''
__docformat__ = "epytext en"

import threading, time

class SingleThreadCalls:
  '''
  Allows the registration of functions that are going to be called from a single
  thread. This single thread must continuously call L{processFunctions}. 
  Registration can be blocking (see L{call}) or non blocking (see L{push}). 
  Blocking registration wait for the function to be processed and returns its 
  result (or raises its exception). Non blocking registration put the function
  in the list and return immediately, ignoring any return value or exception.
  
  Example::
    stc = SingleThreadCall()
    processingThread = threading.Thread( target=stc.processingLoop )
    stc.setProcessingThread( processingThread )
    processingThread.start()
  '''
  
  def __init__( self, thread=None ):
    '''
    The thread passed in parameter is the processing thread of this
    SingleThreadCalls. When started (which is not been done by 
    C{SingleThreadCall}) it must continuously call L{processFunctions} to 
    execute the functions that have been registered with L{call} and L{push}.
    @type  thread: C{threading.Thread} instance or C{None}
    @param thread: Processing thread. If C{None}, C{threading.currentThread()} 
    is used.
    '''
    self._queue = []
    if thread is None:
      thread = threading.currentThread()
    self._thread = thread
    self._condition = threading.Condition()
  
  
  def setProcessingThread( self, thread ):
    '''
    Define the thread that processes the functions. The behaviour of L{call}
    and L{push} is different if called from the processing thread or from
    another one.
    @type  thread: C{threading.Thread} instance
    @param thread: Processing thread
    '''
    self._condition.acquire()
    try:
      self._thread = thread
    finally:
      self._condition.release()
  
  
  def call( self, function, *args, **kwargs ):
    '''
    Register a function call and wait for the processing thread to call it. 
    Returns the result of the function. If an exception is raised during the
    execution of the function, this exception is also raised by C{call()}.
    Therefore C{call} behave like a direct call to the function.
    It is possible to use C{call} from the processing thread. In this case,
    no registration is done (the function is executed immedialey).
    @type  function: callable
    @param function: function to execute
    @param args: parameters of the function
    @param kwargs: keyword parameters of the function
    @return: the result of the function call
    '''
    if threading.currentThread() is self._thread:
      result = apply( function, args, kwargs )
    else:
      semaphore = threading.Semaphore( 0 )
      semaphore._result = None
      semaphore._exception = None
      self._condition.acquire()
      try:
        self._queue.append( ( self._executeAndNotify, (semaphore, function, args, kwargs), {} ) )
        self._condition.notify()
      finally:
        self._condition.release()
      semaphore.acquire()
      if semaphore._exception is not None:
        e = semaphore._exception
        semaphore.release()
        raise e
      result = semaphore._result
    return result

  
  def _executeAndNotify( semaphore, function, args, kwargs ):
    try:
      result = function( *args, **kwargs )
      semaphore._result = result
      semaphore._exception = None
      semaphore.release()
    except Exception, e:
      semaphore._exception = e
      semaphore.release()
  _executeAndNotify = staticmethod( _executeAndNotify )


  def push( self, function, *args, **kwargs ):
    '''
    Same as L{call} method but always put the function on the queue and
    returns immediatly. If C{push} is called from the processing thread,
    the function is called immediately (I{i.e.} synchronously).
    @type  function: callable
    @param function: function to execute
    @param args: parameters of the function
    @param kwargs: keyword parameters of the function
    @return: C{None}
    '''
    if threading.currentThread() is self._thread:
      apply( function, args, kwargs )
    else:
      self._condition.acquire()
      try:
        self._queue.append( ( function, args, kwargs ) )
        self._condition.notify()
      finally:
        self._condition.release()


  def stop( self ):
    '''
    Tells the processing thread to finish the processing of functions in the 
    queue and then stop all processing. This call pushes a special value on
    the function list. All functions that are on the list before this value
    will be processed but functions registered after the special value will be 
    ignored.
    '''
    self._condition.acquire()
    try:
      self._queue.append( None )
      self._condition.notify()
    finally:
      self._condition.release()
  

  def processFunctions( self, blocking=False ):
    '''
    This method extracts all functions (along with their parameters) from
    the queue and execute them. It returns the number of function executed
    C{None} if self.stop() has been called (in that case the processing loop 
    must end).
    
    The processing thread must continuoulsy call this method until C{None} is
    returned.
    
    @type  blocking: bool
    @param blocking: if C{blocking} is False (the default), C{processFunctions} 
    returns C{0} immediately if it cannot access the function list (for example 
    if it is locked by another thread that is registering a function). If 
    C{blocking} is True, C{processFunctions} waits until the function list is
    available.
  
    @see: L{processingLoop}
    '''
    if self._condition.acquire( blocking ):
      try:
        actions = self._queue
        self._queue = []
      finally:
        self._condition.release()
      result = 0
      for action in actions:
        if action is None:
          return None
        function, args, kwargs = action
        function( *args, **kwargs )
        result += 1
      return result 
    return 0


  def processingLoop( self ):
    '''
    Continuously execute L{processFunctions} until it returns C{None}
    @see: L{processFunctions}
    '''
    actionCount = 0
    self._condition.acquire()
    self.processFunctions()
    while actionCount is not None:
      self._condition.wait()
      actionCount = self.processFunctions()
    self._condition.release()
