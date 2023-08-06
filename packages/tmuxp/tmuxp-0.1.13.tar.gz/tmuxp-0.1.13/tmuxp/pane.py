# -*- coding: utf-8 -*-
"""Pythonization of the :ref:`tmux(1)` pane.

tmuxp.pane
~~~~~~~~~~

"""
from __future__ import absolute_import, division, print_function, \
    with_statement, unicode_literals

import logging

from . import util, formats, exc


logger = logging.getLogger(__name__)


class Pane(util.TmuxMappingObject, util.TmuxRelationalObject):

    """:term:`tmux(1)` :term:`pane`.

    :param window: :class:`Window`

    """

    def __init__(self, window=None, **kwargs):
        if not window:
            raise ValueError('Pane must have \
                             ``Window`` object')

        self.window = window
        self.session = self.window.session
        self.server = self.session.server

        self._pane_id = kwargs['pane_id']

        self.server._update_panes()

    @property
    def _TMUX(self, *args):

        attrs = {
            'pane_id': self._pane_id
        }

        # from https://github.com/serkanyersen/underscore.py
        def by(val, *args):
            for key, value in attrs.items():
                try:
                    if attrs[key] != val[key]:
                        return False
                except KeyError:
                    return False
                return True

        return list(filter(by, self.server._panes))[0]

    def tmux(self, cmd, *args, **kwargs):
        """Return :meth:`Server.tmux` defaulting to ``target_pane`` as target.

        Send command to tmux with :attr:`pane_id` as ``target-pane``.

        Specifying ``('-t', 'custom-target')`` or ``('-tcustom_target')`` in
        ``args`` will override using the object's ``pane_id`` as target.

        :rtype: :class:`Server.tmux`

        """
        if not any(arg.startswith('-t') for arg in args):
            args = ('-t', self.get('pane_id')) + args

        return self.server.tmux(cmd, *args, **kwargs)

    def send_keys(self, cmd, enter=True):
        """``$ tmux send-keys`` to the pane.

        A leading space character is added to cmd to avoid polluting the
        user's history.

        :param cmd: Text or input into pane
        :type cmd: str
        :param enter: Send enter after sending the input.
        :type enter: bool

        """
        self.tmux('send-keys', ' ' + cmd)

        if enter:
            self.enter()

    def clear(self):
        """Clear pane."""
        self.send_keys('reset')

    def reset(self):
        """Reset and clear pane history. """

        self.tmux('send-keys', '-R \; clear-history')

    def split_window(self, attach=False):
        """Split window at pane and return newly created :class:`Pane`.

        :param attach: Attach / select pane after creation.
        :type attach: bool
        :rtype: :class:`Pane`.

        """
        return self.window.split_window(
            target=self.get('pane_id'),
            attach=attach
        )

    def set_width(self, width):
        """Set width of pane.

        :param width: pane width, in cells.
        :type width: int

        """
        self.resize_pane(width=width)

    def set_height(self, height):
        """Set height of pane.

        :param height: pane height, in cells.
        :type height: int

        """
        self.resize_pane(height=height)

    def resize_pane(self, *args, **kwargs):
        """``$ tmux resize-pane`` of pane and return ``self``.

        :param target_pane: ``target_pane``, or ``-U``,``-D``, ``-L``, ``-R``.
        :type target_pane: string
        :rtype: :class:`Pane`

        """

        if 'height' in kwargs:
            proc = self.tmux('resize-pane', '-y%s' % int(kwargs['height']))
        elif 'width' in kwargs:
            proc = self.tmux('resize-pane', '-x%s' % int(kwargs['width']))
        else:
            proc = self.tmux('resize-pane', args[0])

        if proc.stderr:
            raise exc.TmuxpException(proc.stderr)

        self.server._update_panes()
        return self

    def enter(self):
        """Send carriage return to pane.

        ``$ tmux send-keys`` send Enter to the pane.

        """
        self.tmux('send-keys', 'Enter')

    def select_pane(self):
        """Select pane. Return ``self``.

        To select a window object asynchrously. If a ``pane`` object exists
        and is no longer longer the current window, ``w.select_pane()``
        will make ``p`` the current pane.

        :rtype: :class:`pane`

        """
        return self.window.select_pane(self.get('pane_id'))

    def __repr__(self):
        return "%s(%s %s)" % (
            self.__class__.__name__,
            self.get('pane_id'),
            self.window
        )
