from cgi import escape
from contextlib import contextmanager
from keyword import iskeyword

from .parse_ic import parce_ic


class Element(object):
	
	def __init__(self, name, document, args, attrs):
		self.name = name
		self.document = document
		self.content = ''
		
		for arg in args:
			if isinstance(arg, basestring) and arg and arg[0] in '.#':
				id, classes = parce_ic(arg)
				
				if id is not None:
					attrs['id'] = id
				
				if classes:
					attrs['class'] = ' '.join(classes)
			elif isinstance(arg, dict):
				attrs.update(arg)
			else:
				self.content = unicode(arg)
		
		for attr in attrs:
			if attr[:5] == 'data_':
				attrs['data-' + attr[5:]] = attrs[attr]
				del attrs[attr]
		
		self.attributes = attrs
	
	@property
	def open(self):
		attributes_string = u''
		for key, value in self.attributes.items():
			if not isinstance(value, basestring):
				value = unicode(value)
			attributes_string += ' ' + key + '="' + escape(value, quote = True) + '"'
		
		return (
			'<' +
			self.name +
			attributes_string +
			('/' if self.is_void else '') +
			'>'
		)
	
	@property
	def close(self):
		if self.is_void:
			return ''
		else:
			return '</' + self.name + '>'
	
	@property
	def is_void(self):
		return self.name in self.document.void_element_names
	
	def __enter__(self):
		if self.is_void:
			raise ValueError("Void elements cannot be used with the context manager syntax.")
		
		self._popped = self.document.pop()
	
	def __exit__(self, *args):
		self.document += self._popped


class Document(object):
	
	Element = Element
	
	# All valid HTML5 elements, according to https://developer.mozilla.org/en-US/docs/HTML/HTML5/HTML5_element_list .
	element_names = (
		{'html', 'head', 'title', 'base', 'link', 'meta', 'style'} |
		{'script', 'noscript'} |
		{'body', 'section', 'nav', 'article', 'aside', 'hgroup', 'header', 'footer', 'address', 'main'} |
		{'h' + str(n) for n in range(1, 6 + 1)} |
		{'p', 'hr', 'blockquote', 'ol', 'ul', 'li', 'dl', 'dt', 'dd', 'figure', 'figcaption', 'div'} |
		{'a', 'em', 'strong', 'small', 's', 'cite', 'q', 'dfn', 'abbr', 'data', 'time', 'code', 'var', 'samp'} |
		{'kbd', 'sub', 'sup', 'i', 'b', 'u', 'mark', 'ruby', 'rt', 'rp', 'bdi', 'bdo', 'span', 'br', 'wbr'} |
		{'ins', 'del'} |
		{'img', 'iframe', 'embed', 'object', 'param', 'video', 'audio'} |
		{'source', 'track', 'canvas', 'map', 'area', 'svg', 'math'} |
		{'table', 'caption', 'colgroup', 'col', 'tbody', 'thead', 'tfoot', 'tr', 'td', 'th'} |
		{'form', 'fieldset', 'legend', 'label', 'input', 'button', 'select', 'datalist'} |
		{'optgroup', 'option', 'textarea', 'keygen', 'output', 'progress', 'meter'} |
		{'details', 'summary', 'command', 'menu'}
	)
	void_element_names = {
		'wbr', 'br', 'img', 'area', 'hr', 'param', 'keygen', 'source', 'meta',
		'command', 'base', 'track', 'link', 'embed', 'col', 'input'
	}
	
	def __init__(self, autoescape_mode = True):
		self._autoescape_mode = autoescape_mode
		self._pieces = []
	
	@contextmanager
	def autoescape_mode(self, mode):
		old_autoescape_mode = self._autoescape_mode
		self._autoescape_mode = bool(mode)
		yield
		self._autoescape_mode = old_autoescape_mode
	
	@contextmanager
	def autoescape_off(self):
		with self.autoescape_mode(False):
			yield
	
	@contextmanager
	def autoescape_on(self):
		with self.autoescape_mode(True):
			yield
	
	def render(self):
		return u''.join(self._pieces)
	
	def __getattr__(self, name):
		
		# Elements that are also Python keywords like <del> need to be prefixed with an underscore.
		if name[0] == '_' and iskeyword(name[1:]):
			name = name[1:]
		
		if name in self.element_names:
			def make_element(*args, **attrs):
				element = self.Element(name, self, args, attrs)
				content = element.content
				if self._autoescape_mode:
					content = escape(content)
				self._pieces += [element.open, content, element.close]
				return element
			return make_element
		else:
			raise AttributeError("No such element or attribute: " + name)
	
	def __iadd__(self, content):
		# Add text without considering autoescape.
		self._pieces.append(content)
		return self
	
	def __call__(self, content):
		if self._autoescape_mode:
			content = escape(content)
		self._pieces.append(content)
	
	def doctype(self):
		self += '<!DOCTYPE html>'
	
	def pop(self):
		return self._pieces.pop()
