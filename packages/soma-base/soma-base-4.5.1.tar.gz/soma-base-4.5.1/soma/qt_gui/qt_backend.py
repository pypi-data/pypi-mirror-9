##########################################################################
# Soma-base - Copyright (C) CEA, 2013
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

'''Compatibility module for PyQt and PySide. Currently supports PyQt4 and
PySide, not PyQt5.
This modules handles differences between PyQt and PySide APIs and behaviours,
and offers a few functions to make it easier to build neutral GUI code, which
can run using either backend.

The main funcion here is set_qt_backend() which must be called to initialize
the appropriate backend. Most functions of this module assume set_qt_backend()
has been called first to setup internal variables.

Note that such compatibility generally requires to use PyQt4 with SIP API
version 2, ie do not use QString, QVariant, QDate and similar classes, but
directly convert to/from python types, which is also PySide behaviour. The
qt_backend module switches to this API level 2, but this only works before the
PyQt modules are imported, thus it may fail if PyQt has already be imported
without such settings.

Qt submodules can be imported in two ways:

>>> from soma.qt_gui import qt_backend
>>> qt_backend.import_qt_submodule('QtWebKit')

or using the import statement:

>>> from soma.qt_gui.qt_backend import QtWebKit

in the latter case, set_qt_backend() will be called automatically to setup the
appropriate Qt backend, so that the use of the backend selection is more
transparent.
'''

import logging
import sys
import os
import imp
from soma.utils.functiontools import partial


# make qt_backend a fake module package, with Qt modules as sub-modules
__package__ = __name__
__path__ = [os.path.dirname(__file__)]

# internal variable to avoid warning several times
_sip_api_set = False

qt_backend = None


class QtImporter(object):
    def find_module(self, fullname, path=None):
        modsplit = fullname.split('.')
        modpath = '.'.join(modsplit[:-1])
        module_name = modsplit[-1]
        if modpath != __name__ or module_name == 'sip':
            return None
        set_qt_backend()
        qt_module = get_qt_module()
        found = imp.find_module(module_name, qt_module.__path__)
        return self

    def load_module(self, name):
        qt_backend = get_qt_backend()
        module_name = name.split('.')[-1]
        __import__('.'.join([qt_backend, module_name]))
        return sys.modules['.'.join([qt_backend, module_name])]

# tune the import statement to get Qt submodules in this one
sys.meta_path.append(QtImporter())


def get_qt_backend():
    '''get currently setup or loaded Qt backend name: "PyQt4" or "PySide"'''
    global qt_backend
    if qt_backend is None:
        pyside = sys.modules.get('PySide')
        if pyside is not None:
            qt_backend = 'PySide'
        else:
            pyqt = sys.modules.get('PyQt4')
            if pyqt is not None:
                qt_backend = 'PyQt4'
    return qt_backend


def set_qt_backend(backend=None):
    '''set the Qt backend.

    If a different backend has already setup or loaded, a warning is issued.
    If no backend is specified, try to guess which one is already loaded, or
    default to PySide.

    Moreover if using PyQt4, QtCore is patched to duplicate QtCore.pyqtSignal
    and QtCore.pyqtSlot as QtCore.Signal and QtCore.Slot.

    Parameters
    ----------
    backend: str (default: None)
        name of the backend to use

    Examples
    --------
        >>> from soma.qt_gui import qt_backend
        >>> qt_backend.set_qt_backend('PySide')
        >>> qt_backend.import_qt_submodule('QtCore')
        <module 'PySide.QtCore' from '/usr/lib/python2.7/dist-packages/PySide/QtCore.so'>
    '''
    global qt_backend
    get_qt_backend()
    if backend is None:
        if qt_backend is None:
            backend = 'PySide'
        else:
            backend = qt_backend
    if qt_backend is not None and qt_backend != backend:
        logging.warn('set_qt_backend: a different backend, %s, has already ' \
            'be set, and %s is now requested' % (qt_backend, backend))
    if backend == 'PyQt4': # and sys.modules.get('PyQt4') is None:
        import sip
        SIP_API = 2
        sip_classes = ['QString', 'QVariant', 'QDate', 'QDateTime',
            'QTextStream', 'QTime', 'QUrl']
        global _sip_api_set
        for sip_class in sip_classes:
            try:
                sip.setapi(sip_class, SIP_API)
            except ValueError, e:
                if not _sip_api_set:
                    logging.warning(e.message)
        _sip_api_set = True
    qt_module = __import__(backend)
    __import__(backend + '.QtCore')
    __import__(backend + '.QtGui')
    qt_backend = backend
    if backend == 'PyQt4':
        qt_module.QtCore.Signal = qt_module.QtCore.pyqtSignal
        qt_module.QtCore.Slot = qt_module.QtCore.pyqtSlot


def get_qt_module():
    '''Get the main Qt module (PyQt4 or PySide)'''
    global qt_backend
    return sys.modules.get(qt_backend)


def import_qt_submodule(submodule):
    '''Import a specified Qt submodule.
    An alternative to the standard statement:

    >>> from soma.qt_gui.qt_backend import <submodule>

    The main differences is that it forces loading the module from the 
    appropriate backend, whereas the import statement will reuse the already
    loaded one. Moreover it returns the module.

    For instance,

    >>> from soma.qt_gui import qt_backend
    >>> qt_backend.set_qt_backend('PyQt4')
    >>> from soma.qt_gui.qt_backend import QtWebKit
    >>> QtWebKit
    <module 'PyQt4.QtWebKit' from '/usr/lib/python2.7/dist-packages/PyQt4/QtWebKit.so'>
    >>> qt_backend.set_qt_backend('PySide') # changing backend
    WARNING:root:set_qt_backend: a different backend, PyQt4, has already be set, and PySide is now requested
    >>> from soma.qt_gui.qt_backend import QtWebKit
    >>> QtWebKit
    <module 'PyQt4.QtWebKit' from '/usr/lib/python2.7/dist-packages/PyQt4/QtWebKit.so'>

    In the above example, we are still using the QtWebKit from PyQt4.
    Now:

    >>> QtWebKit = qt_backend.import_qt_submodule('QtWebKit')
    >>> QtWebKit
    <module 'PySide.QtWebKit' from '/usr/lib/python2.7/dist-packages/PySide/QtWebKit.so'>

    We are now actually using PySide.
    Note that it is generally a bad idea to mix both...

    Parameters
    ----------
        submodule: str (mandatory)
            submodule name, ex: QtWebKit

    Returns
    -------
        the loaded submodule
    '''
    __import__(qt_backend + '.' + submodule)
    mod = sys.modules[qt_backend + '.' + submodule]
    return mod


def _iconset(self, prop):
    return QtGui.QIcon(os.path.join(self._basedirectory,
        prop.text).replace("\\", "\\\\"))

def _pixmap(self, prop):
    return QtGui.QPixmap(os.path.join(self._basedirectory,
        prop.text).replace("\\", "\\\\"))


def loadUi(ui_file, *args, **kwargs):
    '''Load a .ui file and returns the widget instance.

    This function is a replacement of PyQt4.uic.loadUi. The only difference is 
    that relative icon or pixmap file names that are stored in the *.ui file 
    are considered to be relative to the directory containing the ui file. With
    PyQt4.uic.loadUi, relative file names are considered relative to the 
    current working directory therefore if this directory is not the one 
    containing the ui file, icons cannot be loaded.
    '''
    if get_qt_backend() == 'PyQt4':
        # the problem is corrected in version > 4.7.2,
        from PyQt4 import QtCore
        if QtCore.PYQT_VERSION > 0x040702:
            from PyQt4 import uic
            return uic.loadUi(ui_file, *args, **kwargs)
        else:
            # needed import and def
            from PyQt4.uic.Loader import loader
            if not hasattr(globals(), 'partial') :
                from soma.functiontools import partial
            def _iconset(self, prop):
                return QtGui.QIcon( os.path.join( self._basedirectory, prop.text ).replace("\\", "\\\\") )
            def _pixmap(self, prop):
                return QtGui.QPixmap(os.path.join( self._basedirectory, prop.text ).replace("\\", "\\\\"))
            uiLoader = loader.DynamicUILoader()
            uiLoader.wprops._basedirectory = os.path.dirname(
                os.path.abspath(ui_file)) 
            uiLoader.wprops._iconset = partial(_iconset, uiLoader.wprops)
            uiLoader.wprops._pixmap = partial(_pixmap, uiLoader.wprops)
            return uiLoader.loadUi(ui_file, *args, **kwargs)
    else:
        from PySide.QtUiTools import QUiLoader
        return QUiLoader().load(ui_file) #, *args, **kwargs )


def loadUiType(uifile, from_imports=False):
    '''PyQt4 / PySide abstraction to uic.loadUiType.
    Not implemented for PySide, actually, because PySide does not have this 
    feature.
    '''
    if get_qt_backend() == 'PyQt4':
        # the parameter from_imports doesn't exist in our version of PyQt
        from PyQt4 import uic
        return uic.loadUiType(uifile)
    else:
        raise NotImplementedError('loadUiType does not work with PySide')
        #ui = loadUi(uifile)
        #return ui.__class__, QtGui.QWidget # FIXME


def getOpenFileName(parent=None, caption='', directory='', filter='',
        selectedFilter=None, options=0):
    '''PyQt4 / PySide compatible call to QFileDialog.getOpenFileName'''
    if get_qt_backend() == 'PyQt4':
        kwargs = {}
        # kwargs are used because passing None or '' as selectedFilter
        # does not work, at least in PyQt 4.10
        # On the other side I don't know if this kwargs works with older
        # sip/PyQt versions.
        if selectedFilter:
            kwargs['selectedFilter'] = selectedFilter
        if options:
            kwargs['options'] = QtGui.QFileDialog.Options(options)
        return get_qt_module().QtGui.QFileDialog.getOpenFileName(parent,
            caption, directory, filter, **kwargs )
    else:
        return get_qt_module().QtGui.QFileDialog.getOpenFileName(parent,
            caption, directory, filter, selectedFilter,
            QtGui.QFileDialog.Options(options))[0]


def getSaveFileName(parent=None, caption='', directory='', filter='',
        selectedFilter=None, options=0):
    '''PyQt4 / PySide compatible call to QFileDialog.getSaveFileName'''
    if get_qt_backend() == 'PyQt4':
        kwargs = {}
        # kwargs are used because passing None or '' as selectedFilter
        # does not work, at least in PyQt 4.10
        # On the other side I don't know if this kwargs works with older
        # sip/PyQt versions.
        if selectedFilter:
            kwargs['selectedFilter'] = selectedFilter
        if options:
            kwargs['options'] = QtGui.QFileDialog.Options(options)
        return get_qt_module().QtGui.QFileDialog.getSaveFileName(parent,
            caption, directory, filter, **kwargs)
    else:
        return get_qt_module().QtGui.QFileDialog.getSaveFileName(parent,
            caption, directory, filter, selectedFilter, options)[0]


def getExistingDirectory(parent=None, caption='', directory='', options=None):
    '''PyQt4 / PySide compatible call to QFileDialog.getExistingDirectory'''
    if get_qt_backend() == 'PyQt4':
        kwargs = {}
        if options is not None:
            kwargs['options'] = QtGui.QFileDialog.Options(options)
        return get_qt_module().QtGui.QFileDialog.getExistingDirectory(parent,
            caption, directory, **kwargs )
    else:
        if options is not None:
            return get_qt_module().QtGui.QFileDialog.getExistingDirectory(
                parent, caption, directory,
                QtGui.QFileDialog.Options(options))[0]
        else:
            return get_qt_module().QtGui.QFileDialog.getExistingDirectory(
                parent, caption, directory)[0]


def init_matplotlib_backend():
    '''Initialize Matplotlib to use Qt, and the appropriate Qt/Python binding
    (PySide or PyQt) according to the configured/loaded toolkit.
    Moreover, the appropriate FigureCanvas type is set in the current module,
    and returned by this function.
    '''
    import matplotlib
    mpl_ver = [int(x) for x in matplotlib.__version__.split('.')[:2]]
    guiBackend = 'Qt4Agg'
    if 'matplotlib.backends' not in sys.modules:
        matplotlib.use(guiBackend)
    elif matplotlib.get_backend() != guiBackend:
        raise RuntimeError( 
            'Mismatch between Qt version and matplotlib backend: '
            'matplotlib uses ' + matplotlib.get_backend() + ' but '
            + guiBackend + ' is required.')
    if get_qt_backend() == 'PySide':
        if 'backend.qt4' in matplotlib.rcParams.keys():
            matplotlib.rcParams['backend.qt4'] = 'PySide'
        else:
            raise RuntimeError("Could not use Matplotlib, the backend using " \
                "PySide is missing.")
    else:
        if 'backend.qt4' in matplotlib.rcParams.keys():
            matplotlib.rcParams['backend.qt4'] = 'PyQt4'
        else:
            # older versions of matplotlib used only PyQt4.
            if mpl_ver >= [1,1]:
                raise RuntimeError("Could not use Matplotlib, the backend " \
                    "using PyQt4 is missing.")
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg \
        as FigureCanvas
    sys.modules[__name__].FigureCanvas = FigureCanvas
    return FigureCanvas

