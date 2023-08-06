import sys

"""
parses command-line options, not the same as GNU getopt because getopt is honestly pretty gay
.
--name=arg is the syntax used here
--name whatever is not a fucking option, = is mandatory, because that's a good idea. Get aids if you don't believe in it.

-name=arg is the same as --n --a --m --e=arg

example with sys.argv being ['gaynigger.py', '-zO=1,3', 'a', 'male',  'only', 'world']

import sopts

opts = sopts.Sopts([
	['z', 'zero'] ,
	['o', optimization-level'],
	])

'zero' in opt # true
opt['zero'] # None
'0' in opt # true
opt['0'] # 1,3
opt.__getitems__('0') # ['1', '3']
"""

class Opt:

	def __init__ ( self, name, arg = None, parent = None ):
		self._name    = name
		self._arg     = arg
		self._parent  = parent

	def name ( self ):
		return self._name

	def args ( self, separator = ','):
		"""
		all the arguments of the option
		
		separator may be provided, defaults to comma
		"""
		if self.arg() is None:
			return []
		else:
			return self.arg().split(separator)

	def arg ( self ):
		return self._arg

	def parent ( self ):
		"""
		the SOpts parsing object this option belongs to
		may be None
		"""
		return self._parent

	def __str__ ( self ):
		if self.name().__len__() <= 1:
			ret = '-' + self.name()
		else:
			ret = '--' + self.name()
		if self.arg() is not None:
			ret += '=' + self.arg()
		return ret

	def __eq__ ( self, other ):
		"""
		check the equality of options
		
		both the name and arguments of two options must be the same
		
		if an option belongs to a parent then its alias list is used as well
		an alias in an option may end on an '=' character, this is simply ignored
		
		an option can also be compared to a string, in which case the string is interpreted
		as the name of its option and the arguments are ignored
		"""
		if isinstance(other, Opt):
			return self == other.name() and  self.arg() == other.arg()
		if isinstance(other, str):
			other = other.rstrip('=')
			if self.name() == other:
				return True
			if self.parent() is not None:
				for row in self.parent()._aliases:
					row = [el.rstrip('=') for el in row]
					if self.name() in row and other in row:
						return True

		return False


class SOpts:

	"""the SOpts command line parsing object
	
	takes 5 arguments:
	
	1/aliases: a list of lists, this is a list of command line aliases which are considered identical.
	Do not praefix these with dashes yourself, any one of more than 1 character is interpreted as a long opt
	A trailing = may be provided, this is simply ignored but is allowed for certain conveniences
	
	
	2/argv: the argv to handle, this defaults to sys.argv but you can provide your own
	
	3/recognized: all recognized options as a list of strings,
	when set to None (default) this is simply all options given in aliases
	
	4/onset_only: When this is false, command line arguments starting with a dash
	will still considered to be options even after the first positional argument is encountered
	defaults to True
	
	5/positional_boundary: The "hard seperator" command line argument.
	Any command line argument after this one will be considered positional
	defaults to '--'
	
	if it's an integer then any argument starting from this index on will be considered positional
	
	set to None to consider any argument that starts with a dash to be an opt
	"""

	def __init__ ( self, aliases = [], argv = sys.argv, recognized = None, onset_only = True, positional_boundary = '--' ):
		self._aliases    = list(aliases)
		self._argv       = list(argv)

		if recognized is None:
			self._recognized = []
			for row in aliases:
				self._recognized.extend(row)
		else:
			self._recognized = list(recognized)

		self.parse_argv(positional_boundary=positional_boundary, onset_only=onset_only)

	def add_alias ( self, *row ):
		"""
		simply adds its arguments to the alias list
		"""
		for x in row:
			assert isinstance(x, str)
		self._aliases.append(row)

	def aliases ( self ):
		"""
		returns its own alias list as a deep copy
		"""
		import copy
		return copy.deepcopy(self._aliases)

	def args ( self ):
		"""
		returns all positional arguments
		"""
		return self._args

	def unrecognized ( self ):
		"""
		all options given that are not recognized
		"""
		ret = []
		for opt in self:
			for recog in self._recognized:
				if opt == recog:
					break
			else:
				ret.append(opt)

		return ret

	def getopt ( self, key ):
		"""
		get an option
		"""
		for opt in self._opts:
			if opt == key:
				return opt
		else:
			raise KeyError

	def getargs ( self, key, separator = ','):
		"""
		get the arguments of an option separated by a separator
		returns None if the option is not given
		returns [] if the option is given but has no arguments
		"""
		try:
			return self.getopt(key).args(separator = separator)
		except KeyError:
			return None


	def getarg ( self, key ):
		"""
		get one argument, do not perform separation
		returns None if the option has no argument or if the option isn't there
		Note that --opt= is an argument of the empty string
		
		same as opts[key]
		"""
		try:
			return self.getopt(key).arg()
		except KeyError:
			return None

	__getitem__ = getarg

	def __contains__ ( self, key ):
		try:
			self.getopt(key)
			return True
		except KeyError:
			return False

	def __iter__ ( self ):
		return self._opts.__iter__()

	def __len__ ( self ):
		return self._opts.__len__()

	def get_opts ( self, string ):
		assert isinstance(string, str)

		if string == '' or string == '-' or string[0] != '-':
			return []

		if string.__len__() >  2 and string[0:2] == '--':
			if '=' in string[2:]:
				return [Opt(*(string[2:].split('=', 1)), parent = self)]
			else:
				return [Opt(string[2:], parent = self)]

		elif string.__len__() > 1 and string[0:1] == '-':
			if '=' in string[1:]:
				names, arg = string[1:].split('=',1)
			else:
				names = string[1:]
				arg   = None
			return ([
				Opt(c, parent = self) for c in names[:-1]
				]
				+ [Opt(names[-1], arg, parent = self)])


		raise AssertionError("This should never happen")

	def parse_argv ( self, positional_boundary = '--', onset_only = True ):
		argv = self._argv

		opts = []
		args = []
		for i,arg in enumerate(argv[1:]):
			if isinstance(positional_boundary, str) and arg == positional_boundary:
				args.extend(argv[i+2:])
				break
				
			if isinstance(positional_boundary, int) and i-1 == positional_boundary:
				args.extend(argv[i+1:])
				break

			opts_ = self.get_opts(arg)
			if opts_:
				opts.extend(opts_)
			else:
				args.append(arg)
				if onset_only:
					args.extend(argv[i+2:])
					break

		self._opts, self._args = opts, args
