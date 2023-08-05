# This file is part of python-markups module
# License: BSD
# Copyright: (C) Dmitry Shachnev, 2013

from __future__ import absolute_import

import markups.common as common
from markups.abstract import AbstractMarkup

class TextileMarkup(AbstractMarkup):
	"""Markup class for Textile language.
	Inherits :class:`~markups.abstract.AbstractMarkup`.
	"""
	name = 'Textile'
	attributes = {
		common.LANGUAGE_HOME_PAGE: 'http://textile.sitemonks.com/',
		common.MODULE_HOME_PAGE: 'https://github.com/sebix/python-textile',
		common.SYNTAX_DOCUMENTATION: 'http://movabletype.org/documentation/author/textile-2-syntax.html'
	}

	file_extensions = ('.textile',)
	default_extension = '.textile'

	@staticmethod
	def available():
		try:
			import textile
		except ImportError:
			return False
		return True

	def __init__(self, filename=None):
		AbstractMarkup.__init__(self, filename)
		from textile import Textile
		self.parser = Textile()

	def get_document_body(self, text):
		return self.parser.textile(text)
