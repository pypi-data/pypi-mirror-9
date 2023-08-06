# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys

if sys.version < '3': # python 2.7
	text_type = unicode
	binary_type = str
	native_type = binary_type
	unicode_type = unicode
	def to_native(x):
		return to_binary(x)
else: # python 3
	text_type = str
	binary_type = bytes
	native_type = text_type
	unicode_type = str
	def to_native(x):
		return to_unicode(x)


def to_binary(x):
	if isinstance(x, text_type):
		#return codecs.utf_8_encode(x)[0]
		return x.encode("utf-8")
	else:
		return x


def to_unicode(x):
	if isinstance(x, binary_type):
		#return codecs.unicode_escape_decode(x)[0]
		if x == b'\\':
			return u"\\"
		return x.decode("utf-8")
	else:
		return x

