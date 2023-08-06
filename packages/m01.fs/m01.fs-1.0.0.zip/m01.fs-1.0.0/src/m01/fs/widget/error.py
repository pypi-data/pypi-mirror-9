###############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id: error.py 2798 2012-03-04 02:29:53Z roger.ineichen $
"""
__docformat__ = "reStructuredText"

import zope.component

import m01.fs.exceptions

import z3c.form.error


class FileErrorViewSnippet(z3c.form.error.ErrorViewSnippet):
    """An error view for ValueError."""

    zope.component.adapts(m01.fs.exceptions.FileError, None,
        None, None, None, None)

    def createMessage(self):
        return self.error.args[0]