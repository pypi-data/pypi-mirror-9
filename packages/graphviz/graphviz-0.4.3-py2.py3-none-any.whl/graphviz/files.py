# files.py - save, render, view

"""Save DOT code objects, render with Graphviz dot, and open in viewer."""

import sys
import os
import io
import errno
import codecs
import subprocess

from ._compat import text_type

from . import tools

__all__ = ['File']

FORMATS = {  # http://www.graphviz.org/doc/info/output.html
    'bmp',
    'canon', 'dot', 'gv', 'xdot', 'xdot1.2', 'xdot1.4',
    'cgimage',
    'cmap',
    'eps',
    'exr',
    'fig',
    'gd', 'gd2',
    'gif',
    'gtk',
    'ico',
    'imap', 'cmapx',
    'imap_np', 'cmapx_np',
    'ismap',
    'jp2',
    'jpg', 'jpeg', 'jpe',
    'pct', 'pict',
    'pdf',
    'pic',
    'plain', 'plain-ext',
    'png',
    'pov',
    'ps',
    'ps2',
    'psd',
    'sgi',
    'svg', 'svgz',
    'tga',
    'tif', 'tiff',
    'tk',
    'vml', 'vmlz',
    'vrml',
    'wbmp',
    'webp',
    'xlib',
    'x11',
}

ENGINES = {'dot', 'neato', 'twopi', 'circo', 'fdp', 'sfdp', 'osage'}

PLATFORM = sys.platform


class Base(object):

    _format = 'pdf'
    _engine = 'dot'
    _encoding = 'utf8'

    @property
    def format(self):
        """The output format used for rendering ('pdf', 'png', etc.)."""
        return self._format

    @format.setter
    def format(self, format):
        format = format.lower()
        if format not in FORMATS:
            raise ValueError('unknown format: %r' % format)
        self._format = format

    @property
    def engine(self):
        """The layout commmand used for rendering ('dot', 'neato', ...)"""
        return self._engine

    @engine.setter
    def engine(self, engine):
        engine = engine.lower()
        if engine not in ENGINES:
            raise ValueError('unknown engine: %r' % engine)
        self._engine = engine

    @property
    def encoding(self):
        """The encoding for the saved source file."""
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        if encoding is not None:
            codecs.lookup(encoding)
        self._encoding = encoding


class File(Base):

    directory = ''

    _default_extension = 'gv'

    @staticmethod
    def _cmd(engine, format, filepath):
        return [engine, '-T%s' % format, '-O', filepath]

    def __init__(self, filename=None, directory=None, format=None, engine=None, encoding=None):
        if filename is None:
            name = getattr(self, 'name', None) or self.__class__.__name__
            filename = '%s.%s' % (name, self._default_extension)
        self.filename = filename

        if directory is not None:
            self.directory = directory

        if format is not None:
            self.format = format

        if engine is not None:
            self.engine = engine

        if encoding is not None:
            self.encoding = encoding

    @property
    def filepath(self):
        return os.path.join(self.directory, self.filename)

    def save(self, filename=None, directory=None):
        """Save the DOT source to file.

        Returns:
            The (possibly relative) path of the saved source file.
        """
        if filename is not None:
            self.filename = filename
        if directory is not None:
            self.directory = directory

        filepath = self.filepath
        tools.mkdirs(filepath)

        data = text_type(self.source)

        with io.open(filepath, 'w', encoding=self.encoding) as fd:
            fd.write(data)

        return filepath

    def render(self, filename=None, directory=None, view=False, cleanup=False):
        """Save the source to file and render with the Graphviz engine.

        Returns:
            The (possibly relative) path of the rendered file.
        """
        filepath = self.save(filename, directory)

        cmd = self._cmd(self._engine, self._format, filepath)

        try:
            returncode = subprocess.Popen(cmd).wait()
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise RuntimeError('failed to execute %r, '
                    'make sure the Graphviz executables '
                    'are on your systems\' path' % cmd)
            else:
                raise

        if cleanup:
            os.remove(filepath)

        rendered = '%s.%s' % (filepath, self._format)

        if view:
            self._view(rendered, self._format)

        return rendered

    def view(self):
        """Save the source to file, open the rendered result in a viewer.

        Returns:
            The (possibly relative) path of the rendered file.
        """
        rendered = self.render()
        self._view(rendered, self._format)
        return rendered

    def _view(self, filepath, format):
        """Start the right viewer based on file format and platform."""
        methods = [
            '_view_%s_%s' % (format, PLATFORM),
            '_view_%s' % PLATFORM,
        ]
        for name in methods:
            method = getattr(self, name, None)
            if method is not None:
                method(filepath)
                break
        else:
            raise RuntimeError('%r has no built-in viewer support for %r '
                'on %r platform' % (self.__class__, format, PLATFORM))

    @staticmethod
    def _view_linux2(filepath):
        """Open filepath in the user's preferred application (linux)."""
        subprocess.Popen(['xdg-open', filepath], shell=True)

    @staticmethod
    def _view_win32(filepath):
        """Start filepath with its associated application (windows)."""
        os.startfile(os.path.normpath(filepath))

    @staticmethod
    def _view_darwin(filepath):
        """Open filepath with its default application (mac)."""
        subprocess.Popen(['open', filepath], shell=True)
