#################################################################################
#
# The MIT License (MIT)
#
# Copyright (c) 2015 Dmitry Sovetov
#
# https://github.com/dmsovetov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
#################################################################################


from Generator.Eclipse.Android      import Android
from Generator.Make.HTML5           import HTML5
from Generator.Make.Flash           import Flash
from Generator.Make.Make			import Make
from Generator.VisualStudio.Windows import Windows
from Generator.Xcode                import iOS
from Generator.Xcode                import MacOS

import Env

# class Makefile
class Makefile:
	Generators = {
		'iOS':      iOS,
	    'Android':  Android,
	    'MacOS':    MacOS,
	    'Windows':  Windows,
	    'Flash':    Flash,
		'HTML5':    HTML5,
		'Linux':	Make
	}

	platform    = None
	project     = None

	# set
	@staticmethod
	def set( name, value ):
		global _Env
		_Env.set( name, value )

	# get
	@staticmethod
	def get( name ):
		global _Env
		return _Env.get( name )

	# clear
	@staticmethod
	def clear():
		global  _Env
		_Env = Env.Env()

	# createProject
	@staticmethod
	def createProject( cls, name, platform, importer, generator ):
		return cls( name, platform, importer, generator )

	# initialize
	@staticmethod
	def initialize( cls, name, platform, importer ):
		global _Generator

		if platform in Makefile.Generators.keys():
			_Generator = Makefile.Generators[platform]()
		else:
			raise Exception( 'Unknown target platform {0}'.format( platform ) )

		Makefile.project = Makefile.createProject( cls, name, platform, importer, _Generator )
		_Generator.initialize( Makefile, Makefile.project )

	# substituteVars
	@staticmethod
	def substituteVars( input ):
		global _Env

		for k, v in _Env.vars.items():
			if isinstance(v, str):
				input = input.replace( '$(' + k + ')', v )

		return input

	# generate
	@staticmethod
	def generate():
		global _Generator
		_Generator.generate()

_Env       = Env.Env()
_Generator = None