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

import glob, os

from File       import File
from ..Makefile import Makefile

# class Folder
class Folder:
	IgnoreExtensions = [ '.nib', '.md', '.py', '.png', '.in', '.txt' ]

	# ctor
	def __init__( self, target, name = '', parent = None ):
		self._name      = name
		self._parent    = parent
		self._target    = target
		self._files     = []
		self._folders   = {}

	# name
	@property
	def name(self):
		return self._name

	# sourcePath
	@property
	def sourcePath( self ):
		return os.path.join( self._parent.sourcePath, self._name ) if self._parent else self._name

	# full_path
	@property
	def full_path(self):
		return os.path.join(self._target.sourcePath, self.sourcePath).replace('\\', '/')

	# parent
	@property
	def parent(self):
		return self._parent

	# addFile
	def addFile( self, fileName ):
		if self._find_file_by_name(fileName):
			print 'Warning: duplicated file reference', fileName
			return

		self._files.append( File( self._target, self, fileName ) )

	# addFileAtPath
	def addFileAtPath( self, path ):
		assert path.find( '\\' ) == -1

		# Check extension filter
		if self._should_skip_path(path):
			return

		self.resolve( path ).addFile( os.path.basename( path ) )

	# addFilesFromDirectory
	def addFilesFromDirectory( self, path ):
		assert path.find( '\\' ) == -1

		if path.endswith( '/*' ):
			return self.addFilesFromDirectoryRecursive( path )

		for fileName in Folder.glob( os.path.join( path, '*.*' ) ):
			self.addFileAtPath( Folder.relativeTo( fileName, self._target.sourcePath ) )

	# addFilesFromDirectoryRecursive
	def addFilesFromDirectoryRecursive( self, path ):
		assert path.find( '\\' ) == -1

		self.addFilesFromDirectory( path.replace( '/*', '/' ) )

		# Recursively add all nested folders
		for folder in Folder.glob( path ):
			if not os.path.isdir(folder):
				continue

			# Check folder extension
			if self._should_skip_path(folder):
				continue

			# Continue recursive add
			self.addFilesFromDirectoryRecursive( Folder.join( folder, '*' ) )

	# resolve
	def resolve( self, path ):
		items = path.split( '/' )
		name  = items[0]

		if len( items ) == 1:
			return self

		if not name in self._folders.keys():
			self._folders[name] = Folder( self._target, name, self )

		return self._folders[name].resolve( '/'.join( items[1:] ) )

	# filterFiles
	def filterFiles( self, filter ):
		result = [file for file in self._files if filter == None or filter( file )]

		for name, folder in self._folders.items():
			result = result + folder.filterFiles( filter )

		return result

	# filterFolders
	def filterFolders(self, filter):
		result = [folder for name, folder in self._folders.items() if filter == None or filter(folder)]

		for name, folder in self._folders.items():
			result = result + folder.filterFolders(filter)

		return result

	# _should_skip_path
	def _should_skip_path(self, path):
		name, ext = os.path.splitext(path)
		return ext in Folder.IgnoreExtensions

	# _find_file_by_name
	def _find_file_by_name(self, name):
		for file in self._files:
			if file.fileName == name:
				return file
		return None

	# relativeTo
	@staticmethod
	def relativeTo( path, start ):
		return os.path.relpath( path, start ).replace( '\\', '/' )

	# glob
	@staticmethod
	def glob( path ):
		return [item.replace( '\\', '/' ) for item in glob.glob( path )]

	# join
	@staticmethod
	def join( *items ):
		result = ''
		for item in items:
			result = os.path.join( result, item )

		return result.replace( '\\', '/' )