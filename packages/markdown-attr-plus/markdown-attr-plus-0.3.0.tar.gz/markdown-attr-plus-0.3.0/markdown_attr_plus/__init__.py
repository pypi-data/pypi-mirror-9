"""
Attribute+ Extension for Python-Markdown
========================================

Extend the behavior of the Attribute List extension to include
`{^ ... }`, `{o ... }`, and `{> ... }` syntax, which specifically only modify
lists, list items, and blockquotes respectively. This lets you add attributes
to certain elements when it was previously difficult or impossible.
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from markdown.extensions import Extension
from markdown.extensions.attr_list import AttrListTreeprocessor
from markdown.util import isBlockLevel
from itertools import chain, repeat
import re

class FakeDoc(object):
	__slots__ = ('doc', 'processor')
	def __init__(self, doc, processor):
		self.doc = doc
		self.processor = processor

	def _is_list(self, elem):
		return elem.tag in ('dl', 'ol', 'ul')
	def _is_bq(self, elem):
		return elem.tag == 'blockquote'
	def _is_li(self, elem):
		return elem.tag in ('li', 'dt', 'dd')

	def _try_attr(self, elem, pred, RE, li = False):
		# if this isn't the right type, stop now
		if not pred(elem): return False

		# keep track of elements in tree which match criteria
		tree = [elem]
		lc = elem if li else elem[-1]
		while len(lc) > 0:
			if pred(lc):
				tree.append(lc)
			lc = lc[-1]

		# keep track of if we've found a match
		match = None

		# grab part of tag which may contain attribute list regex
		attr = (
			lc.tail and lc.tail.strip() and 'tail' or
			lc.text and lc.text.strip() and 'text'
		)
		if attr:
			text = getattr(lc, attr)

			# for each element in the tree to which we can apply the
			# attributes, in depth-first order; if we have more matches than
			# elements, apply to outermost element
			for i in chain(range(len(tree) - 1, -1, -1), repeat(0)):
				# if we have a match, replace it
				match = RE.search(text)
				if match:
					self.processor.assign_attrs(tree[i], match.group(1))
					text = (text[:match.start()] + text[match.end():])
					setattr(lc, attr, text)
				# no match, stop
				else:
					break

		# things worked out only if we got a match
		return match is not None

	@staticmethod
	def ATTR_RE(s):
		return re.compile(r'\n[ ]*\{' + '\\' + s + r'([^\}]*)\}[ ]*')

	def getiterator(self):
		for elem in self.doc.getiterator():
			if not  self._try_attr(elem, self._is_list, FakeDoc.ATTR_RE('^')) \
			and not self._try_attr(elem, self._is_li,   FakeDoc.ATTR_RE('o'), True) \
			and not self._try_attr(elem, self._is_bq,   FakeDoc.ATTR_RE('>')):
				yield elem

class AttrPlusTreeprocessor(AttrListTreeprocessor):
	def run(self, doc):
		return super(AttrPlusTreeprocessor, self).run(
			doc if isinstance(doc, FakeDoc) else FakeDoc(doc, self)
		)

class AttrPlusExtension(Extension):
	def extendMarkdown(self, md, md_globals):
		md.treeprocessors.add('attr_plus', AttrPlusTreeprocessor(md), '>prettify')

def makeExtension(*args, **kwargs):
	return AttrPlusExtension(*args, **kwargs)
