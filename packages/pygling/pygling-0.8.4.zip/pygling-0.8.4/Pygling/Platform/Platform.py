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

import os

from collections import namedtuple
from ..Makefile  import Makefile
from ..Location  import Path

# class Platform
class Platform:
	ExternalLibrary = namedtuple('ExternalLibrary', 'type, name, locations')
	Location        = namedtuple('Location', 'filename, path')
	FindLibrary     = namedtuple('FindLibrary', 'name, headers, libraries')

	# ctor
	def __init__( self ):
		self._headerSearchPaths  = []
		self._librarySearchPaths = []
		self._libraries          = {}

		self.register_library('vorbis',  headers=['vorbis/codec.h', 'vorbis/vorbisfile.h'],     libraries=['vorbis', 'vorbisfile', 'ogg'])
		self.register_library('fbx',     headers=['fbxsdk.h'],                                  libraries=['fbxsdk'])
		self.register_library('yaml',    headers=['yaml/yaml.h'],                               libraries=['yaml'])
		self.register_library('embree2', headers=['embree2/rtcore.h', 'embree2/rtcore_ray.h'],  libraries=['embree', 'sys', 'simd', 'embree_sse41', 'embree_sse42'])
		self.register_library('jsoncpp', headers=['json/json.h'],                               libraries=['jsoncpp'])
		self.register_library('gtest',   headers=['gtest/gtest.h'],                             libraries=['gtest'])
		self.register_library('pthread', headers=['pthread.h'],									libraries=['pthread'])

	# userpaths
	@property
	def userpaths(self):
		return []

	# headers
	@property
	def headers(self):
		return Makefile.project.headerSearchPaths + self._headerSearchPaths + self.userpaths

	# libraries
	@property
	def libraries(self):
		return Makefile.project.librarySearchPaths + self._librarySearchPaths + self.userpaths

	# find_library
	def find_library(self, name):
		if name in self._libraries.keys():
			library = self._find_library_by_items(self._libraries[name])

			if library:
				return library

		return self._find_library_by_name(name)

	# library_file_names
	def library_file_names(self, name):
		return [name]

	# header_file_names
	def header_file_names(self, name, filename):
		return [filename]

	# add_header_search_paths
	def add_header_search_paths(self, *paths):
		for path in paths:
			if not os.path.exists(path):
				print 'Warning: header search path doesnt exist', path
				continue

			self._headerSearchPaths.append(path)

	# add_library_search_paths
	def add_library_search_paths(self, *paths):
		for path in paths:
			if not os.path.exists(path):
				print 'Warning: library search path doesnt exist', path
				continue

			self._librarySearchPaths.append(path)

	# register_library
	def register_library(self, identifier, name = None, headers = [], libraries = []):
		self._libraries[identifier] = Platform.FindLibrary(name=name if name else identifier, headers=headers, libraries=libraries)

	# exists
	@staticmethod
	def exists(filename, paths):
		for path in paths:
			if os.path.exists(os.path.join(path, filename)):
				return path

		return None

	# _find_headers
	def _find_headers(self, name, headers):
		locations = []

		for header in headers:
			for filename in self.header_file_names(name, header):
				path = Platform.exists(filename, self.headers)
				if path: locations.append(Platform.Location(filename=filename, path=Path(Path.Headers, path)))

		return locations

	# _find_libraries
	def _find_libraries(self, name, libraries):
		locations = []

		for library in libraries:
			for filename in self.library_file_names(library):
				path = Platform.exists(filename, self.libraries)
				if path: locations.append(Platform.Location(filename=filename, path=Path(Path.Libraries, path)))

		return locations

	# _find_library_by_items
	def _find_library_by_items(self, library):
		# Locate library
		librarySearchPath = self._find_libraries(library.name, library.libraries)
		if not librarySearchPath:
			print 'Warning: no libraries found for ' + library.name
			return None

		# Locate headers
		headerSearchPath = self._find_headers(library.name, library.headers)
		if not headerSearchPath:
			print 'Warning: no headers found for ' + library.name
			return None

		return Platform.ExternalLibrary(type='external', name=library.name, locations=headerSearchPath + librarySearchPath)

	# _find_library_by_name
	def _find_library_by_name(self, library):
		return None