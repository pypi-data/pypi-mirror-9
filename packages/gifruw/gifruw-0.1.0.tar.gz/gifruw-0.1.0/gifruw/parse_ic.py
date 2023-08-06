import re


# According to http://www.w3.org/TR/CSS21/grammar.html#scanner .
_ic_regex = re.compile(r'[\.#]-?[_a-z][_a-z0-9-]*')

def parce_ic(string):
	
	id = None
	classes = set()
	
	matches = _ic_regex.findall(string)
	
	if not ''.join(matches) == string:
		raise ValueError("Invalid ID and classes string: " + string)
	
	for match in matches:
		type, name =  match[0], match[1:]
		if type == '.':
			classes.add(name)
		elif type == '#':
			id = name
	
	return id, classes
