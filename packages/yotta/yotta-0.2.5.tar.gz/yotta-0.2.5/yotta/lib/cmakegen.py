# Copyright 2014 ARM Limited
#
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

# standard library modules, , ,
import string
import os
import logging
import re
import itertools
from collections import defaultdict

# bsd licensed - pip install jinja2
from jinja2 import Environment, FileSystemLoader

# fsutils, , misc filesystem utils, internal
import fsutils
# validate, , validate various things, internal
import validate

Template_Dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')

logger = logging.getLogger('cmakegen')

Ignore_Subdirs = set(('build','yotta_modules', 'yotta_targets', 'CMake'))

jinja_environment = Environment(loader=FileSystemLoader(Template_Dir), trim_blocks=True, lstrip_blocks=True)

def replaceBackslashes(s):
    return s.replace('\\', '/')
jinja_environment.filters['replaceBackslashes'] = replaceBackslashes

class SourceFile(object):
    def __init__(self, fullpath, relpath, lang):
        super(SourceFile, self).__init__()
        self.fullpath = fullpath
        self.relpath = relpath
        self.lang = lang
    def __repr__(self):
        return self.fullpath

class CMakeGen(object):
    def __init__(self, directory, target):
        super(CMakeGen, self).__init__()
        self.buildroot = directory
        logger.info("generate for target: %s" % target)
        self.target = target

    def _writeFile(self, path, contents):
        dirname = os.path.dirname(path)
        fsutils.mkDirP(dirname)
        self.writeIfDifferent(path, contents)

    def generateRecursive(self, component, all_components, builddir=None, modbuilddir=None, processed_components=None):
        ''' generate top-level CMakeLists for this component and its
            dependencies: the CMakeLists are all generated in self.buildroot,
            which MUST be out-of-source

            !!! NOTE: experimenting with a slightly different way of doing
            things here, this function is a generator that yields any errors
            produced, so the correct use is:

            for error in gen.generateRecursive(...):
                print(error)
        '''
        if builddir is None:
            builddir = self.buildroot
        if modbuilddir is None:
            modbuilddir = os.path.join(builddir, 'ym')
        if processed_components is None:
            processed_components = dict()
        if not self.target:
            yield 'Target "%s" is not a valid build target' % self.target

        toplevel = not len(processed_components)

        logger.debug('generate build files: %s (target=%s)' % (component, self.target))
        # because of the way c-family language includes work we need to put the
        # public header directories of all components that this component
        # depends on (directly OR indirectly) into the search path, which means
        # we need to first enumerate all the direct and indirect dependencies
        recursive_deps = component.getDependenciesRecursive(
            available_components = all_components,
                          target = self.target,
                  available_only = True
        )
        dependencies = component.getDependencies(
                  all_components,
                          target = self.target,
                  available_only = True
        )

        for name, dep in dependencies.items():
            if not dep:
                yield 'Required dependency "%s" of "%s" is not installed.' % (name, component)
        # ensure this component is assumed to have been installed before we
        # check for its dependencies, in case it has a circular dependency on
        # itself
        processed_components[component.getName()] = component
        new_dependencies = {name:c for name,c in dependencies.items() if c and not name in processed_components}
        self.generate(builddir, modbuilddir, component, new_dependencies, dependencies, recursive_deps, toplevel)

        logger.debug('recursive deps of %s:' % component)
        for d in recursive_deps.values():
            logger.debug('    %s' % d)

        processed_components.update(new_dependencies)
        for name, c in new_dependencies.items():
            for error in self.generateRecursive(
                c, all_components, os.path.join(modbuilddir, name), modbuilddir, processed_components
            ):
                yield error

    def checkStandardSourceDir(self, dirname, component):
        err = validate.sourceDirValidationError(dirname, component.getName())
        if err:
            logger.warn(err)

    def _sanitizeTarget(self, targetname):
        return re.sub('[^a-zA-Z0-9]', '_', targetname).upper()

    def _sanitizeSymbol(self, sym):
        return re.sub('[^a-zA-Z0-9]', '_', sym)

    def _listSubDirectories(self, component):
        ''' return: {
                manual: [list of subdirectories with manual CMakeLists],
                  auto: [list of pairs: (subdirectories name to autogenerate, a list of source files in that dir)],
                   bin: {dictionary of subdirectory name to binary name},
                  test: [list of directories that build tests]
              resource: [list of directories that contain resources]
            }
        '''
        manual_subdirs = []
        auto_subdirs = []
        bin_subdirs = {os.path.normpath(x) : y for x,y in component.getBinaries().items()};
        test_subdirs = []
        resource_subdirs = []
        for f in os.listdir(component.path):
            if f in Ignore_Subdirs or f.startswith('.') or f.startswith('_'):
                continue
            if os.path.isfile(os.path.join(component.path, f, 'CMakeLists.txt')):
                self.checkStandardSourceDir(f, component)
                # if the subdirectory has a CMakeLists.txt in it, then use that
                manual_subdirs.append(f)
                # tests only supported in the `test` directory for now
                if f in ('test',):
                    test_subdirs.append(f)
            elif f in ('source', 'test') or os.path.normpath(f) in bin_subdirs:
                # otherwise, if the directory has source files, generate a
                # CMakeLists in the corresponding temporary directory, and add
                # that.
                # For now we only do this for the source and test directories -
                # in theory we could do others
                sources = self.containsSourceFiles(os.path.join(component.path, f), component)
                if sources:
                    auto_subdirs.append((f, sources))
                    # tests only supported in the `test` directory for now
                    if f in ('test',):
                        test_subdirs.append(f)
            elif f in ('resource'):
                resource_subdirs.append(os.path.join(component.path, f))
            elif f.lower() in ('source', 'src', 'test', 'resource'):
                self.checkStandardSourceDir(f, component)
        return {
            "manual": manual_subdirs,
              "auto": auto_subdirs,
               "bin": bin_subdirs,
              "test": test_subdirs,
          "resource": resource_subdirs
        }

    def generate(
            self, builddir, modbuilddir, component, active_dependencies, immediate_dependencies, all_dependencies, toplevel
        ):
        ''' active_dependencies is the dictionary of components that need to be
            built for this component, but will not already have been built for
            another component.
        '''

        include_own_dir = 'include_directories("%s")\n' % component.path

        include_root_dirs = ''
        include_sys_dirs = ''
        include_other_dirs = ''
        for name, c in itertools.chain(((component.getName(), component),), all_dependencies.items()):
            include_root_dirs += 'include_directories("%s")\n' % replaceBackslashes(c.path)
            dep_sys_include_dirs = c.getExtraSysIncludes()
            for d in dep_sys_include_dirs:
                include_sys_dirs += 'include_directories(SYSTEM "%s")\n' % replaceBackslashes(os.path.join(c.path, d))
            dep_extra_include_dirs = c.getExtraIncludes()
            for d in dep_extra_include_dirs:
                include_other_dirs += 'include_directories("%s")\n' % replaceBackslashes(os.path.join(c.path, d))

        add_depend_subdirs = ''
        for name, c in active_dependencies.items():
            depend_subdir = replaceBackslashes(os.path.join(modbuilddir, name))
            add_depend_subdirs += 'add_subdirectory("%s" "%s")\n' % (
                depend_subdir, depend_subdir
            )

        delegate_to_existing = None
        delegate_build_dir = None

        if os.path.isfile(os.path.join(component.path, 'CMakeLists.txt')):
            delegate_to_existing = component.path
            add_own_subdirs = []
            logger.debug("delegate to build dir: %s", builddir)
            delegate_build_dir = os.path.join(builddir, 'existing')
        else:
            subdirs = self._listSubDirectories(component)
            manual_subdirs      = subdirs['manual']
            autogen_subdirs     = subdirs['auto']
            binary_subdirs      = subdirs['bin']
            test_subdirs        = subdirs['test']
            resource_subdirs    = subdirs['resource']

            add_own_subdirs = []
            for f in manual_subdirs:
                if os.path.isfile(os.path.join(component.path, f, 'CMakeLists.txt')):
                    add_own_subdirs.append(
                        (os.path.join(component.path, f), os.path.join(builddir, f))
                    )

            # names of all directories at this level with stuff in: used to figure
            # out what to link automatically
            all_subdirs = manual_subdirs + [x[0] for x in autogen_subdirs]
            for f, source_files in autogen_subdirs:
                if f in binary_subdirs:
                    exe_name = binary_subdirs[f]
                else:
                    exe_name = None
                if f in test_subdirs:
                    self.generateTestDirList(
                        builddir, f, source_files, component, immediate_dependencies, toplevel=toplevel
                    )
                else:
                    self.generateSubDirList(
                        builddir, f, source_files, component, all_subdirs,
                        immediate_dependencies, exe_name, resource_subdirs
                    )
                add_own_subdirs.append(
                    (os.path.join(builddir, f), os.path.join(builddir, f))
                )

            # if we're not building anything other than tests, then we need to
            # generate a dummy library so that this component can still be linked
            # against
            if len(add_own_subdirs) <= len(test_subdirs):
                add_own_subdirs.append(self.createDummyLib(
                    component, builddir, [x for x in immediate_dependencies]
                ))


        target_definitions = '-DTARGET=' + self._sanitizeTarget(self.target.getName())  + ' '
        set_targets_like = 'set(TARGET_LIKE_' + self._sanitizeTarget(self.target.getName()) + ' TRUE)\n'
        for target in self.target.dependencyResolutionOrder():
            if '*' not in target:
                target_definitions += '-DTARGET_LIKE_' + self._sanitizeTarget(target) + ' '
                set_targets_like += 'set(TARGET_LIKE_' + self._sanitizeTarget(target) + ' TRUE)\n'

        template = jinja_environment.get_template('base_CMakeLists.txt')

        file_contents = template.render({
                            "toplevel": toplevel,
                         "target_name": self.target.getName(),
                    "set_targets_like": set_targets_like,
                      "toolchain_file": self.target.getToolchainFile(),
                      "component_name": component.getName(),
                     "include_own_dir": include_own_dir,
                   "include_root_dirs": include_root_dirs,
                    "include_sys_dirs": include_sys_dirs,
                  "include_other_dirs": include_other_dirs,
                  "add_depend_subdirs": add_depend_subdirs,
                     "add_own_subdirs": add_own_subdirs,
            "yotta_target_definitions": target_definitions,
                   "component_version": component.getVersion(),
                         "delegate_to": delegate_to_existing,
                  "delegate_build_dir": delegate_build_dir
        })
        self._writeFile(os.path.join(builddir, 'CMakeLists.txt'), file_contents)
    
    def createDummyLib(self, component, builddir, link_dependencies):
        safe_name        = self._sanitizeSymbol(component.getName())
        dummy_dirname    = 'yotta_dummy_lib_%s' % safe_name
        dummy_cfile_name = 'dummy.c'
        logger.debug("create dummy lib: %s, %s, %s" % (safe_name, dummy_dirname, dummy_cfile_name))


        dummy_template = jinja_environment.get_template('dummy_CMakeLists.txt')

        dummy_cmakelists = dummy_template.render({
                   "cfile_name": dummy_cfile_name,
                      "libname": component.getName(),
            "link_dependencies": link_dependencies
        })
        self._writeFile(os.path.join(builddir, dummy_dirname, "CMakeLists.txt"), dummy_cmakelists)
        dummy_cfile = "void __yotta_dummy_lib_symbol_%s(){}\n" % safe_name
        self._writeFile(os.path.join(builddir, dummy_dirname, dummy_cfile_name), dummy_cfile)
        return (os.path.join(builddir, dummy_dirname), os.path.join(builddir, dummy_dirname))

    def writeIfDifferent(self, fname, contents):
        try:
            with open(fname, "r+") as f:
                current_contents = f.read()
                if current_contents != contents:
                    f.seek(0)
                    f.write(contents)
                    f.truncate()
        except IOError:
            with open(fname, "w") as f:
                f.write(contents)

    def generateTestDirList(self, builddir, dirname, source_files, component, immediate_dependencies, toplevel=False):
        logger.debug('generate CMakeLists.txt for directory: %s' % os.path.join(component.path, dirname))

        link_dependencies = [x for x in immediate_dependencies]
        fname = os.path.join(builddir, dirname, 'CMakeLists.txt')

        # group the list of source files by subdirectory: generate one test for
        # each subdirectory, and one test for each file at the top level
        subdirs = defaultdict(list)
        toplevel_srcs = []
        for f in source_files:
            if f.lang in ('c', 'cpp', 'objc'):
                subrelpath = os.path.relpath(f.relpath, dirname)
                subdir = os.path.split(subrelpath)[0]
                if subdir:
                    subdirs[subdir].append(f)
                else:
                    toplevel_srcs.append(f)

        tests = []
        for f in toplevel_srcs:
            object_name = '%s-test-%s' % (
                component.getName(), os.path.basename(os.path.splitext(str(f))[0]).lower()
            )
            tests.append([[str(f)], object_name, [f.lang]])
        for subdirname, sources in subdirs.items():
            object_name = '%s-test-%s' % (
                component.getName(), fsutils.fullySplitPath(subdirname)[0].lower()
            )
            tests.append([[str(f) for f in sources], object_name, [f.lang for f in sources]])

        # link tests against the main executable
        link_dependencies.append(component.getName())

        # Find cmake files
        cmake_files = []
        for root, dires, files in os.walk(os.path.join(component.path, dirname)):
            for f in files:
                name, ext = os.path.splitext(f)
                if ext.lower() == '.cmake':
                    cmake_files.append(os.path.join(root, f))

        test_template = jinja_environment.get_template('test_CMakeLists.txt')

        file_contents = test_template.render({
             'source_directory':os.path.join(component.path, dirname),
                        'tests':tests,
            'link_dependencies':link_dependencies,
                  'cmake_files': cmake_files,
             'exclude_from_all': (not toplevel),
        })

        self._writeFile(fname, file_contents)

    def generateSubDirList(self, builddir, dirname, source_files, component, all_subdirs, immediate_dependencies, executable_name, resource_subdirs):
        logger.debug('generate CMakeLists.txt for directory: %s' % os.path.join(component.path, dirname))

        link_dependencies = [x for x in immediate_dependencies]
        fname = os.path.join(builddir, dirname, 'CMakeLists.txt')

        if dirname == 'source' or executable_name:
            if executable_name:
                object_name = executable_name
                executable  = True
            else:
                object_name = component.getName()
                executable  = False
            # if we're building the main library, or an executable for this
            # component, then we should link against all the other directories
            # containing cmakelists:
            link_dependencies += [x for x in all_subdirs if x not in ('source', 'test', dirname)]

            # Find resource files
            resource_files = []
            for f in resource_subdirs:
                for root, dires, files in os.walk(f):
                    if root.endswith(".xcassets"):
                        resource_files.append(root)
                        break;
                    for f in files:
                        resource_files.append(os.path.join(root, f))

            # Find cmake files
            cmake_files = []
            for root, dires, files in os.walk(os.path.join(component.path, dirname)):
                for f in files:
                    name, ext = os.path.splitext(f)
                    if ext.lower() == '.cmake':
                        cmake_files.append(os.path.join(root, f))

            subdir_template = jinja_environment.get_template('subdir_CMakeLists.txt')

            file_contents = subdir_template.render({
                    'source_directory': os.path.join(component.path, dirname),
                          'executable': executable,
                          'file_names': [str(f) for f in source_files],
                         'object_name': object_name,
                   'link_dependencies': link_dependencies,
                           'languages': set(f.lang for f in source_files),
                        'source_files': set((f.fullpath, f.lang) for f in source_files),
                      'resource_files': resource_files,
                         'cmake_files': cmake_files
            })
        else:
            raise Exception('auto CMakeLists for non-source/test directories is not supported')
        self._writeFile(fname, file_contents)


    def containsSourceFiles(self, directory, component):
        c_exts          = set(('.c',))
        cpp_exts        = set(('.cpp','.cc','.cxx'))
        objc_exts       = set(('.m', '.mm'))
        header_exts     = set(('.h',))

        sources = []
        for root, dires, files in os.walk(directory):
            for f in files:
                name, ext = os.path.splitext(f)
                ext = ext.lower()
                fullpath = os.path.join(root, f)
                relpath  = os.path.relpath(fullpath, component.path)
                if component.ignores(relpath):
                    continue
                if ext in c_exts:
                    sources.append(SourceFile(fullpath, relpath, 'c'))
                elif ext in cpp_exts:
                    sources.append(SourceFile(fullpath, relpath, 'cpp'))
                elif ext in objc_exts:
                    sources.append(SourceFile(fullpath, relpath, 'objc'))
                elif ext in header_exts:
                    sources.append(SourceFile(fullpath, relpath, 'header'))
        return sources
