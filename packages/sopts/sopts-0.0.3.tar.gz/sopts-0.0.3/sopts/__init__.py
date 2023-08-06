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

	def args ( self ):
		if self.arg() is None:
			return []
		else:
			return self.arg().split(',')

	def arg ( self ):
		return self._arg

	def parent ( self ):
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
		if isinstance(other, Opt):
			return self == other.name() and  self.arg() == other.arg()
		if isinstance(other, str):
			if self.name() == other:
				return True
			if self.parent() is not None:
				for row in self.parent()._aliases:
					if self.name() in row and other in row:
						return True

		return False


class SOpts:

	def __init__ ( self, aliases = [], argv = sys.argv, recognized = None, onset_only = True, positional_boundary = '--' ):
		self._aliases    = list(aliases)
		self._argv       = list(argv)

		if recognized is None:
			self._recognized = []
			for row in aliases:
				self._recognized.extend(row)
		else:
			self._recognized = list(recognized)

		if onset_only and self._argv.__len__() > 1 and not self.get_opts(self._argv[1]):
			self._opts = []
			self._args = self._argv[1:]
		else:
			self._opts, self._args = self.parse_argv(positional_boundary)

	def add_alias ( self, *row ):
		for x in row:
			assert isinstance(x, str)
		self._aliases.append(row)

	def aliases ( self ):
		import copy
		return copy.deepcopy(self._aliases)

	def args ( self ):
		return self._args

	def unrecognized ( self ):
		ret = []
		for opt in self:
			for recog in self._recognized:
				if self.opt_eq(opt.name(), recog):
					break
			else:
				ret.append(opt)

		return ret

	def getopt ( self, key ):
		for opt in self._opts:
			if isinstance(key, str):
				if self.opt_eq(opt.name(), key):
					return opt
			else:
				if opt == key:
					return opt
		else:
			raise KeyError

	def getargs ( self, key ):
		try:
			return self.getopt(key).args()
		except KeyError:
			return None


	def getarg ( self, key ):
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

	def opt_eq ( self, str1, str2 ):
		if str1 == str2:
			return True
		for row in self._aliases:
			if str1 in row and str2 in row:
				return True

		return False

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

	def parse_argv ( self, positional_boundary = '--' ):
		argv = self._argv

		assert isinstance(positional_boundary, str) or positional_boundary is None
		opts = []
		args = []
		for i,arg in enumerate(argv[1:]):
			if positional_boundary and arg == positional_boundary:
				args.extend(argv[i+2:])
				break

			opts_ = self.get_opts(arg)
			if opts_:
				opts.extend(opts_)
			else:
				args.append(arg)

		return opts, args

def al_eq(str1, str2, als):
	if str1 == str2:
		return True
	for row in als:
		if str1 in row and str2 in row:
			return True

	return False


