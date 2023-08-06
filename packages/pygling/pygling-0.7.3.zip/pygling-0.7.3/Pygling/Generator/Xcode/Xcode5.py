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

import os, shutil, plistlib, subprocess, glob, getpass

from ..Generator import Generator
from PBX         import Project
from ..Template  import Template

# class Xcode5
class Xcode5( Generator ):
	# ctor
	def __init__( self ):
		Generator.__init__( self )

		self.project  = None
		self.projects = {}

	# generate
	def generate( self ):
		Generator.generate( self )

		# Create project for each target
		self.forEachTarget( self.createProjects )

		# Setup projects
		for name, project in self.projects.items():
			target = project['target']
			pbx    = project['pbx']

			self.addTargetSources( target.name, target, pbx )
			self.addTargetLibraries( target.name, target, pbx )
			self.addTargetCommands( target.name, target, pbx )
			self.saveProject( project['project'], target )

		# Create workspace
		self.generateWorkspace()

	# commandLineToolsSupported
	@property
	def commandLineToolsSupported( self ):
		return False

	# generateWorkspace
	def generateWorkspace( self ):
		# Create the workspace folder
		workspace = os.path.join( self.projectpath, self.sourceProject.name + '.xcworkspace' )

		# Create folder
		if not os.path.exists( workspace ):
			os.mkdir( workspace )

		# Generate project list
		projects = ''

		for name, project in self.projects.items():
			folder    = self.getPathForTarget( project['target'] )
			path      = os.path.relpath( os.path.join( folder, name + '.xcodeproj' ), self.projectpath )
			projects += "<FileRef location='group:{0}'/>\n".format( path )

		# Dump workspace to file
		Template( Xcode5.Workspace ).compileToFile( os.path.join( workspace, 'contents.xcworkspacedata' ), { 'projects': projects } )

	# saveProject
	def saveProject( self, project, target ):
		# Create project folder
		folder   = os.path.join( self.getPathForTarget( target ), target.name + '.xcodeproj' )

		if not os.path.exists( folder ):
			os.mkdir( folder )

		# Create user data folder
		userdata = os.path.join( folder, 'xcuserdata', getpass.getuser() + '.xcuserdatad', 'xcschemes' )

		if not os.path.exists( userdata ):
			os.makedirs( userdata )

		userdata = os.path.join( userdata, target.name + '.xcscheme' )

		# Dump scheme to file
		productName = 'lib' + target.name + '.a' if target.type == 'static' else target.name + '.app'
		Template( Xcode5.Scheme ).compileToFile( userdata, { 'id': project.id, 'name': target.name, 'product.name': productName } )

		# Dump project to disk
		file = open( os.path.join( folder, 'project.pbxproj' ), 'wt' )
		file.write( project.generate() )
		file.close()

	# createProjects
	def createProjects( self, name, target ):
		settings = {
			'Debug':    self.generateConfiguration( target, 'Debug' ),
		    'Release':  self.generateConfiguration( target, 'Release' )
		}

		# Create project
		project = Project( target.name, self.getProjectSettings() )
		pbx     = None

		# Create target
		if target.type == 'executable':
			if (target.params and target.params['bundle']) or not self.commandLineToolsSupported:
				pbx = project.addApplicationBundle( name, name + '.app', settings, 'Debug', self.makefile.get( 'DEVELOPMENT_TEAM' ) )
				self.addInfoPlist( target, pbx )
				if target.resources:
					self.addResources( target, pbx )
			else:
				pbx = project.addApplication( name, name, settings, 'Debug' )
		else:
			pbx = project.addStaticLibrary( name, 'lib' + name + '.a', settings, 'Debug' )

		self.projects[name] = { 'project': project, 'target': target, 'pbx': pbx }

	# getProjectSettings
	def getProjectSettings( self ):
		return None

	# getPlatformId
	def getPlatformId( self ):
		return None

	# addInfoPlist
	def addInfoPlist( self, target, pbx ):
		pbx.addPlist( 'Info.plist' )
		Template( Xcode5.Plist ).compileToFile( os.path.join( self.getPathForTarget( target ), 'Info.plist' ), {
																										'identifier':       self.makefile.get( 'IDENTIFIER' ),
																										'version':          self.makefile.get( 'VERSION' ),
																										'short.version':    self.makefile.get( 'SHORT_VERSION' ),
		                                                                                                'facebook.app.id':  self.makefile.get( 'FACEBOOK_APP_ID' )
																									} )

	# addResources
	def addResources( self, target, pbx ):
		path   = os.path.join( target.sourcePath, target.resources[0] )
		icons  = os.path.join( path, 'images', 'icons.'  + self.getPlatformId() )
		launch = os.path.join( path, 'images', 'launch.' + self.getPlatformId() )
		assets = os.path.join( path, 'assets', 'assets.dpk' )

		# Root
		if os.path.exists( path ):
			pbx.addFolder( path )

		# Icons
		if os.path.exists( icons ):
			dst = os.path.join( self.getPathForTarget( target ), 'icons.xcassets' )
			if os.path.exists( dst ):
				shutil.rmtree( dst )

			shutil.copytree( icons, dst )

			pbx.addAssetCatalog( 'icons.xcassets' )
			pbx.setAppIcon( 'Icon' )

		# Launch images
		if os.path.exists( launch ):
			dst = os.path.join( self.getPathForTarget( target ), 'launch.xcassets' )
			if os.path.exists( dst ):
				shutil.rmtree( dst )

			shutil.copytree( launch, dst )

			pbx.addAssetCatalog( 'launch.xcassets' )
			pbx.setLaunchImage( 'Launch' )

		# Assets
		if os.path.exists( assets ):
			dst = os.path.join( self.getPathForTarget( target ), 'assets.dpk' )

			shutil.copyfile( assets, dst )

			pbx.addResourceFile( 'assets.dpk' )

	# addTargetCommands
	def addTargetCommands( self, name, target, pbx ):
		# No commands for target
		if len( target.commands ) == 0:
			return

		# Add shell script
		pbx.addShellScript( 'make -C {0} -f {1}.commands'.format( self.getPathForTarget( target ), name ) )

		# Generate makefile
		commands = self.processEachTargetCommand( target, self.compileCommand )
		depends  = self.processEachTargetCommand( target, self.compileDependency )
		Template( Xcode5.CodegenScript ).compileToFile( os.path.join( self.getPathForTarget( target ), name + '.commands' ), { 'depends': depends, 'commands': commands } )

	# addTargetSources
	def addTargetSources( self, name, target, pbx ):

		# addSourceFile
		def addSourceFile( file ):
			addSourceFile.target.addSourceFile( file.projectPath, file.folder.sourcePath )

		# Add source files to target
		addSourceFile.target = pbx
		self.forEachTargetSource( target, addSourceFile )
		
	# addTargetLibraries
	def addTargetLibraries( self, name, target, pbx ):
		if not target.shouldLinkLibraries:
			return

		for library in self.list_libraries(target):
			if library.type == 'local':
				if not library.name in self.projects.keys():
					print 'Error: unknown library', library.name
					continue

				pbx.addProjectLibrary( self.projects[library.name]['pbx'] )
			elif library.type == 'framework':
				pbx.addFramework(os.path.join(library.path, library.name + '.framework'))
			elif library.type == 'external':
				for location in [location for location in library.locations if location.path.islibraries]:
					pbx.addLibrary(os.path.join(location.path.full, location.filename))
			else:
				print 'Error: unknown library type', library.type

	# compileCommand
	def compileCommand( self, target, cmd ):
		output = ''
		for ext in cmd.generatedExtensions:
			output += cmd.output + ext + ' '

		input = ''
		for fileName in cmd.input:
			input += fileName + ' '

		return Template( Xcode5.CodegenCommand ).compile( { 'output': output, 'input': input, 'command': cmd.command, 'message': cmd.message } )

	# compileDependency
	def compileDependency( self, target, cmd ):
		result = ''

		for ext in cmd.generatedExtensions:
			result += '\\\n\t' + cmd.output + ext

		return result

	# generateConfiguration
	def generateConfiguration( self, target, name ):
		# generateLibrarySearchPaths
		def generateLibrarySearchPaths( library ):
			return ' ' + library.libs + ' ' if library.type == 'external' else None

		# generateDefines
		def generateDefines( target, define ):
			return ' ' + define + ' '

		headers = self.list_header_paths(target)
		defines = self.list_defines(target)
		libs    = []

		if target.shouldLinkLibraries:
			libs = self.list_library_paths( target )

		libs.append( '$(inherited)' )
		headers.append( '$(inherited)' )

		std                     = self.makefile.get( 'STD' )
		clangLanguageStarndard  = dict( cxx11 = '"c++0x"',  cxx98 = '"c++98"' )
		clangLibrary            = dict( cxx11 = '"libc++"', cxx98 = '"libstdc++"' )

		options = dict(
			  PRODUCT_NAME                  = '"$(TARGET_NAME)"'
			, HEADER_SEARCH_PATHS           = headers
			, LIBRARY_SEARCH_PATHS          = libs
		    , DEBUG_INFORMATION_FORMAT      = 'dwarf' if name == 'Debug' else 'dwarf-with-dsym'
			, GCC_PREPROCESSOR_DEFINITIONS  = defines
			, GCC_OPTIMIZATION_LEVEL        = 0 if name == 'Debug' else 's'
		    , CLANG_CXX_LANGUAGE_STANDARD   = clangLanguageStarndard[std] if std in clangLanguageStarndard.keys() else clangLanguageStarndard['cxx98']
		    , CLANG_CXX_LIBRARY             = clangLibrary[std] if std in clangLibrary.keys() else clangLibrary['cxx98']
		)

		return options

	CodegenCommand = """
{output}: {input}
	@echo '{message}'
	@{command}
	"""

	CodegenScript = """
all: {depends}

{commands}
"""

	Plist = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleIdentifier</key>
	<string>{identifier}</string>
	<key>CFBundleShortVersionString</key>
	<string>{short.version}</string>
	<key>CFBundleVersion</key>
	<string>{version}</string>
	<key>CFBundleVersion</key>
	<string>{version}</string>
	<key>CFBundleExecutable</key>
	<string>${PRODUCT_NAME}</string>
	<key>FacebookAppID</key>
	<string>{facebook.app.id}</string>
	<key>NSPrincipalClass</key>
	<string>NSApplication</string>
</dict>
</plist>
"""

	Workspace = """<?xml version='1.0' encoding='UTF-8'?>
<Workspace version='1.0'>
{projects}
</Workspace>
"""

	Scheme = """<?xml version="1.0" encoding="UTF-8"?>
<Scheme
   LastUpgradeVersion = "0610"
   version = "1.3">
   <BuildAction
      parallelizeBuildables = "YES"
      buildImplicitDependencies = "YES">
      <BuildActionEntries>
         <BuildActionEntry
            buildForTesting = "YES"
            buildForRunning = "YES"
            buildForProfiling = "YES"
            buildForArchiving = "YES"
            buildForAnalyzing = "YES">
            <BuildableReference
		        BuildableIdentifier = "primary"
		        BlueprintIdentifier = "{id}"
		        BuildableName = "{product.name}"
		        BlueprintName = "{name}"
		        ReferencedContainer = "container:{name}.xcodeproj">
			</BuildableReference>
         </BuildActionEntry>
      </BuildActionEntries>
   </BuildAction>
      <TestAction
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      shouldUseLaunchSchemeArgsEnv = "YES"
      buildConfiguration = "Debug">
      <Testables>
      </Testables>
      <MacroExpansion>
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "{id}"
            BuildableName = "{product.name}"
            BlueprintName = "{name}"
            ReferencedContainer = "container:{name}.xcodeproj">
         </BuildableReference>
      </MacroExpansion>
   </TestAction>
   <LaunchAction
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      launchStyle = "0"
      useCustomWorkingDirectory = "NO"
      buildConfiguration = "Debug"
      ignoresPersistentStateOnLaunch = "NO"
      debugDocumentVersioning = "YES"
      allowLocationSimulation = "YES">
      <BuildableProductRunnable>
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "{id}"
            BuildableName = "{product.name}"
            BlueprintName = "{name}"
            ReferencedContainer = "container:{name}.xcodeproj">
         </BuildableReference>
      </BuildableProductRunnable>
      <AdditionalOptions>
      </AdditionalOptions>
   </LaunchAction>
   <ProfileAction
      shouldUseLaunchSchemeArgsEnv = "YES"
      savedToolIdentifier = ""
      useCustomWorkingDirectory = "NO"
      buildConfiguration = "Release"
      debugDocumentVersioning = "YES">
      <BuildableProductRunnable>
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "{id}"
            BuildableName = "{product.name}"
            BlueprintName = "{name}"
            ReferencedContainer = "container:{name}.xcodeproj">
         </BuildableReference>
      </BuildableProductRunnable>
   </ProfileAction>
   <AnalyzeAction
      buildConfiguration = "Debug">
   </AnalyzeAction>
   <ArchiveAction
      buildConfiguration = "Release"
      revealArchiveInOrganizer = "YES">
   </ArchiveAction>
</Scheme>"""