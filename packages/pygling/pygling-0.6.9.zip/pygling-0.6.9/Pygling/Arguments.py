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

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

# class Arguments
class Arguments:
	current = None
	unknown = None

	# ctor
	def __init__(self):
		args = ArgumentParser(description = 'Pygling C++ workspace generator.', prefix_chars = '--', formatter_class = ArgumentDefaultsHelpFormatter)

		actions = args.add_subparsers(help = 'Pygling action')

		# Build action
		build = actions.add_parser('build', help='Build a workspace')
		self._add_platforms(build)
		self._add_default(build)

		# Configure action
		configure = actions.add_parser('configure', help='Configure a workspace')
		self._add_platforms(configure)
		self._add_default(configure)

		# Install action
		install = actions.add_parser('install', help='Install workspace products')
		self._add_platforms(install)
		self._add_default(install)

		Arguments.current, Arguments.unknown = args.parse_known_args()

		print Arguments.current
		print Arguments.unknown

	# _add_platforms
	def _add_platforms(self, arg):
		platforms = arg.add_subparsers(help='Target platforms')

		platforms.add_parser('all')

		android = platforms.add_parser('android')
		android.add_argument('--package', type = str, help = "Application package identifier" )
		android.add_argument('--sdk',	  type = int, help = "Android SDK identifier" )

		mac = platforms.add_parser('mac')
		mac.add_argument( "--team", type = str, help = "Xcode team profile to be used" )

		ios = platforms.add_parser('ios')
		ios.add_argument( "--team", type = str, help = "Xcode team profile to be used" )

		platforms.add_parser('windows')

	# _add_default
	def _add_default(self, arg):
		arg.add_argument( "-a", "--arch",   default = 'default',    type = str, help = "Target build architecture" )
		arg.add_argument( "-s", "--source", default = '.',          type = str, help = "Project source path" )
		arg.add_argument( "-o", "--output", default = 'projects',   type = str, help = "Output path" )
		arg.add_argument( "-n", "--name",   default = 'noname',     type = str, help = "Workspace (solution) name" )
		arg.add_argument( "-x", "--std",    default = 'cxx98',      type = str, help = "C++ standard", choices = ['cxx99', 'cxx11'] )