#!/usr/bin/env python 
# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------
# Copyright (c) 2013, NeXpy Development Team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file COPYING, distributed with this software.
#-----------------------------------------------------------------------------

""" A minimal application using the Qt console-style IPython frontend.

This is not a complete console app, as subprocess will not be able to receive
input, there is no real readline support, among other limitations.

Based on IPython module of the same name.

Authors:

* Evan Patterson
* Min RK
* Erik Tollerud
* Fernando Perez
* Bussonnier Matthias
* Thomas Kluyver
* Paul Ivanov

"""

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# stdlib imports
import logging
import logging.handlers
import pkg_resources
import os
import signal
import sys
import tempfile

# System library imports
from PySide import QtCore, QtGui

# Local imports
from mainwindow import MainWindow
from treeview import NXtree
from nexpy.api.nexus import nxclasses, nxload

# IPython imports
from IPython.config.application import catch_config_error
from IPython.core.application import BaseIPythonApplication
from IPython.lib import guisupport
from IPython.qt.console.ipython_widget import IPythonWidget
from IPython.qt.console.rich_ipython_widget import RichIPythonWidget
from IPython.qt.console import styles
from IPython.utils.traitlets import (
    Dict, Unicode, CBool, Any
)

from IPython.consoleapp import (
        IPythonConsoleApp, app_aliases, app_flags, flags, aliases
    )

#-----------------------------------------------------------------------------
# Network Constants
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Globals
#-----------------------------------------------------------------------------

_examples = """
ipython qtconsole                 # start the qtconsole
ipython qtconsole --pylab=inline  # start with pylab in inline plotting mode
"""
_tree = None
_shell = None
_mainwindow = None
_nexpy_dir = None

#-----------------------------------------------------------------------------
# Aliases and Flags
#-----------------------------------------------------------------------------

# start with copy of flags
flags = dict(flags)
qt_flags = {
    'plain' : ({'NXConsoleApp' : {'plain' : True}},
            "Disable rich text support."),
}

# and app_flags from the Console Mixin
qt_flags.update(app_flags)
# add frontend flags to the full set
flags.update(qt_flags)

# start with copy of front&backend aliases list
aliases = dict(aliases)
qt_aliases = dict(
    style = 'IPythonWidget.syntax_style',
    stylesheet = 'IPythonQtConsoleApp.stylesheet',
    colors = 'ZMQInteractiveShell.colors',

    editor = 'IPythonWidget.editor',
    paging = 'ConsoleWidget.paging',
)
# and app_aliases from the Console Mixin
qt_aliases.update(app_aliases)
qt_aliases.update({'gui-completion':'ConsoleWidget.gui_completion'})
# add frontend aliases to the full set
aliases.update(qt_aliases)

# get flags&aliases into sets, and remove a couple that
# shouldn't be scrubbed from backend flags:
qt_aliases = set(qt_aliases.keys())
qt_aliases.remove('colors')
qt_flags = set(qt_flags.keys())

#-----------------------------------------------------------------------------
# Classes
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# NXConsoleApp
#-----------------------------------------------------------------------------

class NXConsoleApp(BaseIPythonApplication, IPythonConsoleApp):
    name = 'ipython-qtconsole'

    description = """
        The NeXpy Console.
        
        This launches a Console-style application using Qt. 
        
        The console is embedded in a GUI that contains a tree view of
        all NXroot groups and a matplotlib plotting pane. It also has all
        the added benefits of an IPython Qt Console with multiline editing,
        autocompletion, tooltips, command line histories and the ability to 
        save your session as HTML or print the output.
        
    """

    classes = [IPythonWidget] + IPythonConsoleApp.classes
    flags = Dict(flags)
    aliases = Dict(aliases)
    frontend_flags = Any(qt_flags)
    frontend_aliases = Any(qt_aliases)

    stylesheet = Unicode('', config=True,
        help="path to a custom CSS stylesheet")

    plain = CBool(False, config=True,
        help="Use a plaintext widget instead of rich text (plain can't print/save).")

    def _plain_changed(self, name, old, new):
        kind = 'plain' if new else 'rich'
        self.config.ConsoleWidget.kind = kind
        if new:
            self.widget_factory = IPythonWidget
        else:
            self.widget_factory = RichIPythonWidget

    # the factory for creating a widget
    widget_factory = Any(RichIPythonWidget)

    def parse_command_line(self, argv=None):
        super(NXConsoleApp, self).parse_command_line(argv)
        self.build_kernel_argv(argv)

    def init_dir(self):
        """Initialize NeXpy home directory"""
        home_dir = os.path.realpath(os.path.expanduser('~'))
        nexpy_dir = os.path.join(home_dir, '.nexpy')
        if not os.path.exists(nexpy_dir):
            parent = os.path.dirname(nexpy_dir)
            if not os.access(parent, os.W_OK):
                nexpy_dir = tempfile.mkdtemp()
            else:
                os.mkdir(nexpy_dir)
        for subdirectory in ['functions', 'plugins', 'readers', 'scripts']:
            directory = os.path.join(nexpy_dir, subdirectory)
            if not os.path.exists(directory):
                os.mkdir(directory)
        global _nexpy_dir
        _nexpy_dir = nexpy_dir

    def init_log(self):
        log_file = os.path.join(_nexpy_dir, 'nexpy.log')
        hdlr = logging.handlers.RotatingFileHandler(log_file, maxBytes=50000, 
                                                    backupCount=5)
        fmt = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", None)
        hdlr.setFormatter(fmt)
        logging.root.addHandler(hdlr)
        logging.root.setLevel(logging.INFO)
        logging.info('NeXpy launched')

    def init_tree(self):
        """Initialize the NeXus tree used in the tree view."""
        global _tree
        self.tree = NXtree()
        _tree = self.tree
        
    def init_gui(self):
        """Initialize the GUI."""
        self.app = guisupport.get_app_qt4()
        self.window = MainWindow(self.app, self.tree, config=self.config)
        self.window.log = self.log
        global _mainwindow
        _mainwindow = self.window
        self.app.icon = QtGui.QIcon(
            pkg_resources.resource_filename('nexpy.gui',
                                            'resources/icon/NeXpy.svg'))
        QtGui.QApplication.setWindowIcon(self.app.icon)

    def init_shell(self):
        """Initialize imports in the shell."""
        global _shell
        _shell = self.window.user_ns
        s = ("import nexpy\n"
             "import nexpy.api.nexus as nx\n"
             "from nexpy.api.nexus import NXgroup, NXfield, NXattr, NXlink\n"
             "from nexpy.api.nexus import NXFile\n"
             "from nexpy.gui.plotview import NXPlotView")
        exec s in self.window.user_ns
        
        s = ""
        for _class in nxclasses:
            s = "%s=nx.%s\n" % (_class,_class) + s
        exec s in self.window.user_ns

        try:
            f = open(os.path.join(os.path.expanduser('~'), '.nexpy', 
                                  'config.py'))
            s = ''.join(f.readlines())
            exec s in self.window.user_ns
        except:
            s = ("import sys\n"
                 "import os\n"
                 "import h5py as h5\n"
                 "import numpy as np\n"
                 "import numpy.ma as ma\n"
                 "import scipy as sp\n"
                 "import matplotlib as mpl\n"
                 "from matplotlib import pylab, mlab, pyplot\n"
                 "plt = pyplot")
            exec s in self.window.user_ns
        try:
            print sys.argv[1]
            fname = os.path.expanduser(sys.argv[1])
            name = _mainwindow.treeview.tree.get_name(fname)
            _mainwindow.treeview.tree[name] = self.window.user_ns[name] = nxload(fname)
            _mainwindow.treeview.select_node(_mainwindow.treeview.tree[name])
            logging.info("NeXus file '%s' opened as workspace '%s'" 
                          % (fname, name))
            self.window.user_ns[name].plot()
        except:
            pass

    def init_colors(self):
        """Configure the coloring of the widget"""
        # Note: This will be dramatically simplified when colors
        # are removed from the backend.

        # Configure the style.
        self.window.console.set_default_style()

    def init_signal(self):
        """allow clean shutdown on sigint"""
        signal.signal(signal.SIGINT, lambda sig, frame: self.exit(-2))
        # need a timer, so that QApplication doesn't block until a real
        # Qt event fires (can require mouse movement)
        # timer trick from http://stackoverflow.com/q/4938723/938949
        timer = QtCore.QTimer()
        # Let the interpreter run each 200 ms:
        timer.timeout.connect(lambda: None)
        timer.start(200)
        # hold onto ref, so the timer doesn't get cleaned up
        self._sigint_timer = timer

    @catch_config_error
    def initialize(self, argv=None):
        super(NXConsoleApp, self).initialize(argv)
        self.init_dir()
        self.init_log()
        self.init_tree()
        self.init_gui()
        self.init_shell()
        self.init_colors()
        self.init_signal()

    def start(self):

        # draw the window
        self.window.show()
        self.window.raise_()

        # Start the application main loop.
        guisupport.start_event_loop_qt4(self.app)
#       self.app.exec_()

#-----------------------------------------------------------------------------
# Main entry point
#-----------------------------------------------------------------------------

def main():
    app = NXConsoleApp()
    app.initialize()
    app.start()


if __name__ == '__main__':
    main()
