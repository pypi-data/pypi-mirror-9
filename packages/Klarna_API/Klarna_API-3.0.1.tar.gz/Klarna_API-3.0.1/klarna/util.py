''' Klarna API

utility functions
'''
# Copyright 2011 KLARNA AB. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY KLARNA AB "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL KLARNA AB OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of KLARNA AB.

# python3k campatibility
from __future__ import print_function
import sys
if sys.version_info >= (3,):
    import xmlrpc.client as xmlrpc
    from html.entities import name2codepoint
    basestring = str
else:
    import htmlentitydefs
    import xmlrpclib as xmlrpc
    basestring = basestring

__all__ = ('xmlrpc', 'basestring', 'check_type', 'kstr', 'Tag')


def check_type(field, v, types, tag=None):
    ''' Raises TypeError unless v is a instance of any of the provided types '''

    if not isinstance(v, types):
        raise TypeError("%s not an %s (%s %r)" %
            (field, ' or '.join([t.__name__ for t in types]), type(v), v))

    if tag is not None:
        if isinstance(v, Tag) and not isinstance(v, tag):
            raise TypeError("Tagged value %r not of expected type %s (was %s)" %
                (v, tag, type(v)))

    return v


class Tag(str):
    ''' Used as base class for str subclasses used by Klarna API '''
    def __new__(cls, tostr, klarna=None):
        o = str.__new__(cls, tostr)
        o.klarna = klarna
        return o


if sys.version_info >= (3,):
    kstr = str
else:
    __sys_encoding = sys.getdefaultencoding()
    if __sys_encoding == 'ascii':
        # ascii is a mostly useless default, let's assume utf-8
        # as it's sane a superset of ascii
        __sys_encoding = 'utf-8'

    def kstr(s):
        if isinstance(s, str):
            s = s.decode(__sys_encoding)
        if isinstance(s, unicode):
            return s.encode('iso-8859-1')
        return str(s)
