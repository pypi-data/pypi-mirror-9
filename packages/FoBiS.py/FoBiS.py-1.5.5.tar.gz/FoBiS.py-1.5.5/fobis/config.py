#!/usr/bin/env python
"""
config.py, module definition of FoBiS.py configuration.
"""
import hashlib
import os
import re
import sys
from .Builder import Builder
from .Cleaner import Cleaner
from .Colors import Colors
from .Fobos import Fobos
from .ParsedFile import ParsedFile
from .cli_parser import cli_parser
from .utils import syswork
from .utils import dependency_hiearchy
from .utils import remove_other_main

__appname__ = "FoBiS.py"
__version__ = "v1.5.5"
__author__ = "Stefano Zaghi"
__author_email__ = "stefano.zaghi@gmail.com"
__license__ = "GNU General Public License v3 (GPLv3)"
__url__ = "https://github.com/szaghi/FoBiS"
__description__ = "a Fortran Building System for poor men"
__long_description__ = "FoBiS.py, a Fortran Building System for poor men, is a KISS tool for automatic building modern Fortran projects, it being able to automatically resolve inter-modules dependancy hierarchy."


class FoBiSConfig(object):
  """
  Object handling FoBiS.py configuration
  """
  def __init__(self):
    """
    Attributes
    ----------
    cliargs : {None}
      CLI arguments, argparse object
    fobos : {None}
      Fobos object, the FoBiS.py makefile
    colors : {Colors}
      Colors object
    """
    self.cliargs = None
    self.fobos = None
    self.colors = Colors()
    return

  def _update_colors(self):
    """
    Method for updating colors settings.
    """
    if not self.cliargs.colors:
      self.colors.disable()
    else:
      self.colors.enable()
    return

  def _print_b(self, string):
    """
    Method for printing string with bold color.

    Parameters
    ----------
    string : str
      string to be printed
    """
    self.colors.print_b(string)
    return

  def _print_r(self, string):
    """
    Method for printing string with red color.

    Parameters
    ----------
    string : str
      string to be printed
    """
    self.colors.print_r(string)
    return

  def _update_extensions(self):
    """Method for updating files extensions"""
    if self.cliargs.which == 'build':
      for inc in self.cliargs.inc:
        if inc not in self.cliargs.extensions:
          self.cliargs.extensions.append(inc)
    if self.cliargs.which == 'build':
      if len(self.cliargs.pfm_ext) > 0:
        self.cliargs.extensions += self.cliargs.pfm_ext
    return

  def _sanitize_paths(self):
    """
    Method for sanitizing paths.
    """
    if self.cliargs.which == 'clean' or self.cliargs.which == 'build':
      self.cliargs.build_dir = os.path.normpath(self.cliargs.build_dir) + os.sep
      self.cliargs.mod_dir = os.path.normpath(self.cliargs.mod_dir) + os.sep
      self.cliargs.obj_dir = os.path.normpath(self.cliargs.obj_dir) + os.sep
    if self.cliargs.which == 'build':
      self.cliargs.src = os.path.normpath(self.cliargs.src) + os.sep
    return

  def _check_cflags_heritage(self):
    """
    Method for checking the heritage of cflags: if a file named '.cflags.heritage' is found into the root dir FoBiS.py is runned that file
    is sourced and compared with the actual cflags and in case they differ the project is forced to be recompiled. The actual cflags are saved,
    in any case, into that file.
    """
    if self.cliargs.which == 'build':
      if self.cliargs.cflags_heritage:
        if os.path.exists(self.cliargs.build_dir + '.cflags.heritage'):
          cflags_old = open(self.cliargs.build_dir + '.cflags.heritage').read()
          if self.cliargs.cflags != cflags_old:
            self.cliargs.force_compile = True
            self._print_r("The present cflags are different from the heritages one: forcing to (re-)compile all")
        with open(self.cliargs.build_dir + '.cflags.heritage', 'w') as chf:
          chf.writelines(self.cliargs.cflags)
    return

  def _postinit(self):
    """
    Method for post-initialization update of config attributes, after CLI and fobos parsing.
    """
    self._update_colors()
    self._update_extensions()
    self._sanitize_paths()
    self._check_cflags_heritage()
    self._check_vlibs_md5sum()
    self._check_ext_vlibs_md5sum()
    self._check_interdependent_fobos()
    return

  @staticmethod
  def _check_md5sum(filename, hashfile):
    """
    Function for checking the md5sum hash of a file, compares with an eventual hashfile into which the hash is finally saved.

    Parameters
    ----------
    filename : str
      file name (with path) of file to be hashed
    hashfile : str
      file eventually present containing the hash and into which the hash is finally saved

    Returns
    -------
    2 bools containing the previously existance of the hashfile and the result of hashes comparison
    """
    md5sum = hashlib.md5(open(filename, 'rb').read()).hexdigest()
    hashexist = os.path.exists(hashfile)
    comparison = False
    if hashexist:
      md5sum_old = open(hashfile).read()
      comparison = md5sum == md5sum_old
    with open(hashfile, 'w') as md5:
      md5.writelines(md5sum)
    return hashexist, comparison

  def _check_vlibs_md5sum(self):
    """
    Method for checking if the md5sum of volatile libraries has changed and, in case, a re-build is triggered.
    """
    if self.cliargs.which == 'build':
      if len(self.cliargs.vlibs) > 0:
        for lib in self.cliargs.vlibs:
          if not os.path.exists(lib):
            self._print_r("The volatile library " + lib + " is not found!")
            # sys.exit(1)
          hashfile, comparison = self._check_md5sum(filename=lib, hashfile=self.cliargs.build_dir + '.' + os.path.basename(lib) + '.md5')
          if hashfile:
            self.cliargs.force_compile = (not comparison) or self.cliargs.force_compile
            if not comparison:
              self._print_r("The volatile library " + lib + " is changed with respect the last building: forcing to (re-)compile all")
    return

  def _check_ext_vlibs_md5sum(self):
    """
    Method for checking if the md5sum of volatile external libraries has changed and, in case, a re-build is triggered.
    """
    if self.cliargs.which == 'build':
      if len(self.cliargs.ext_vlibs) > 0:
        for lib in self.cliargs.ext_vlibs:
          lib_found = False
          if len(self.cliargs.lib_dir) > 0:
            for dirp in self.cliargs.lib_dir:
              libpath = os.path.join(dirp, 'lib' + lib + '.a')
              lib_found = os.path.exists(libpath)
              if lib_found:
                break
              libpath = os.path.join(dirp, 'lib' + lib + '.so')
              lib_found = os.path.exists(libpath)
              if lib_found:
                break
          else:
            libpath = 'lib' + lib + '.a'
            lib_found = os.path.exists(libpath)
            if not lib_found:
              libpath = 'lib' + lib + '.so'
              lib_found = os.path.exists(libpath)
          if not lib_found:
            self._print_r("The volatile library " + lib + " is not found!")
            # sys.exit(1)
          hashfile, comparison = self._check_md5sum(filename=libpath, hashfile=self.cliargs.build_dir + '.' + os.path.basename(libpath) + '.md5')
          if hashfile:
            self.cliargs.force_compile = (not comparison) or self.cliargs.force_compile
            if not comparison:
              self._print_r("The volatile library " + lib + " is changed with respect the last building: forcing to (re-)compile all")
    return

  def _add_include_paths(self, add_paths):
    """
    Method for adding include files search paths

    Parameters
    ----------
    add_paths : list
      added paths, each element has 3 elements: path[0] libraries search path, path[1] include files search path, path[2] the library
    """
    self._print_r("Include files search paths (include):")
    for path in add_paths:
      if self.cliargs.include:
        self.cliargs.include.append(path[1])
      else:
        self.cliargs.include = [path[1]]
      self._print_r("- " + path[1])
    return

  def _add_lib_dir_paths(self, add_paths):
    """
    Method for adding libraries search paths

    Parameters
    ----------
    add_paths : list
      added paths, each element has 3 elements: path[0] libraries search path, path[1] include files search path, path[2] the library
    """
    self._print_r("Libraries search paths (lib_dir):")
    for path in add_paths:
      if path[2][1].lower() == 'indirect':
        if self.cliargs.lib_dir:
          self.cliargs.lib_dir.append(path[0])
        else:
          self.cliargs.lib_dir = [path[0]]
        self._print_r("- " + path[0])
    return

  def _add_ext_libs_paths(self, add_paths):
    """
    Method for adding libraries paths

    Parameters
    ----------
    add_paths : list
      added paths, each element has 3 elements: path[0] libraries search path, path[1] include files search path, path[2] the library
    """
    self._print_r("Libraries paths:")
    for path in add_paths:
      if path[2][1].lower() == 'indirect':
        lib = re.sub(r"^lib", '', os.path.basename(path[2][0]))
        lib = re.sub(r"\.a$", '', lib)
        lib = re.sub(r"\.so$", '', lib)
        if self.cliargs.ext_libs:
          self.cliargs.ext_libs.append(lib)
        else:
          self.cliargs.ext_libs = [lib]
        self._print_r("- (ext_libs) " + lib)
      else:
        if self.cliargs.libs:
          self.cliargs.libs.append(path[2][0])
        else:
          self.cliargs.libs = [path[2][0]]
        self._print_r("- (libs) " + path[2][0])
    return

  def _add_auxiliary_paths(self, add_paths):
    """
    Method for adding auxiliary paths to default searched ones.

    Parameters
    ----------
    add_paths : list
      added paths, each element has 3 elements: path[0] libraries search path, path[1] include files search path, path[2] the library
    """
    self._print_r("The following auxiliary paths have been added")
    self._add_include_paths(add_paths=add_paths)
    self._add_lib_dir_paths(add_paths=add_paths)
    self._add_ext_libs_paths(add_paths=add_paths)
    return

  def _check_interdependent_fobos(self):
    """
    Method for checking interdependency project by its fobos.
    """
    if self.cliargs.which == 'build' and not self.cliargs.lmodes:
      if len(self.cliargs.dependon) > 0:
        add_paths = []
        for dependon in self.cliargs.dependon:
          fobos_path = os.path.dirname(dependon)
          fobos_file = os.path.basename(dependon)
          mode = ''
          linking = ''
          matching = re.match(r"^.*\(\((?P<link>.*)\)\).*$", fobos_file)
          if matching:
            linking = matching.group('link')
            fobos_file = re.sub(r"\(\(.*\)\)", '', fobos_file)
          if ":" in fobos_file:
            mode = os.path.basename(fobos_file).split(":")[1]
            fobos_file = os.path.basename(fobos_file).split(":")[0]
          old_pwd = os.getcwd()
          os.chdir(old_pwd + os.sep + fobos_path)
          if mode != '':
            self._print_b("Building dependency " + fobos_file + " into " + fobos_path + " with mode " + mode)
            result = syswork("FoBiS.py build -f " + fobos_file + " -mode " + mode)
            dbld = syswork("FoBiS.py rule -f " + fobos_file + " -mode " + mode + " -get build_dir")
            dmod = syswork("FoBiS.py rule -f " + fobos_file + " -mode " + mode + " -get mod_dir")
            output = syswork("FoBiS.py rule -f " + fobos_file + " -mode " + mode + " -get_output_name")
          else:
            self._print_b("Building dependency " + fobos_file + " into " + fobos_path + " with default mode")
            result = syswork("FoBiS.py build -f " + fobos_file)
            dbld = syswork("FoBiS.py rule -f " + fobos_file + " -get build_dir")
            dmod = syswork("FoBiS.py rule -f " + fobos_file + " -get mod_dir")
            output = syswork("FoBiS.py rule -f " + fobos_file + " -get_output_name")
          os.chdir(old_pwd)
          print(result[1])
          if result[0] != 0:
            sys.exit(result[0])
          add_paths.append([os.path.normpath(fobos_path + os.sep + dbld[1].strip('\n')) + os.sep,
                            os.path.normpath(fobos_path + os.sep + dbld[1].strip('\n') + os.sep + dmod[1].strip('\n')) + os.sep,
                            [os.path.normpath(fobos_path + os.sep + output[1].strip('\n')), linking]])
        self._add_auxiliary_paths(add_paths)
    return

  def _get_parsed_files_list(self):
    """
    Function for creating the list of parsed files

    Returns
    -------
    list
      list of ParsedFile objects
    """
    pfiles = []
    # parsing files loop
    for root, _, files in os.walk(self.cliargs.src):
      for filename in files:
        if any(os.path.splitext(os.path.basename(filename))[1] == ext for ext in self.cliargs.extensions):
          if os.path.basename(filename) not in [os.path.basename(exc) for exc in self.cliargs.exclude]:
            filen = os.path.join(root, filename)
            pfile = ParsedFile(name=filen)
            pfile.parse(inc=self.cliargs.inc)
            pfiles.append(pfile)
    return pfiles

  def _build(self):
    """
    Method for running FoBiS.py in building mode.
    """
    builder = Builder(cliargs=self.cliargs, print_n=self._print_b, print_w=self._print_r)
    pfiles = self._get_parsed_files_list()
    # building dependencies hierarchy
    dependency_hiearchy(builder=builder, pfiles=pfiles, print_w=self._print_r, force_compile=self.cliargs.force_compile)
    # compiling independent files that are libraries of procedures not contained into a module (old Fortran style)
    nomodlibs = []
    for pfile in pfiles:
      if pfile.nomodlib:
        builder.build(file_to_build=pfile, verbose=self.cliargs.verbose, log=self.cliargs.log)
        nomodlibs.append(pfile.basename + ".o")
    # building target or all programs found
    for pfile in pfiles:
      if self.cliargs.target:
        if os.path.basename(self.cliargs.target) == os.path.basename(pfile.name):
          self._print_b(builder.verbose(quiet=self.cliargs.quiet))
          if pfile.program:
            remove_other_main(builder=builder, pfiles=pfiles, mysefl=pfile)
          builder.build(file_to_build=pfile, output=self.cliargs.output, nomodlibs=nomodlibs, mklib=self.cliargs.mklib, verbose=self.cliargs.verbose, log=self.cliargs.log)
          if self.cliargs.log:
            pfile.save_build_log(builder=builder)
          if self.cliargs.graph:
            pfile.save_dep_graph()
      else:
        if pfile.program:
          self._print_b(builder.verbose(quiet=self.cliargs.quiet))
          remove_other_main(builder=builder, pfiles=pfiles, mysefl=pfile)
          builder.build(file_to_build=pfile, output=self.cliargs.output, nomodlibs=nomodlibs, verbose=self.cliargs.verbose, log=self.cliargs.log)
          if self.cliargs.log:
            pfile.save_build_log(builder=builder)
          if self.cliargs.graph:
            pfile.save_dep_graph()
    return

  def _clean(self):
    """
    Method for running FoBiS.py in cleaning mode.
    """
    cleaner = Cleaner(cliargs=self.cliargs, print_w=self._print_r)
    if not self.cliargs.only_obj and not self.cliargs.only_target:
      cleaner.clean_mod()
      cleaner.clean_obj()
      cleaner.clean_target()
    if self.cliargs.only_obj:
      cleaner.clean_mod()
      cleaner.clean_obj()
    if self.cliargs.only_target:
      cleaner.clean_target()
    return

  def _get_cli(self, fake_args=None):
    """
    Method for parsing CLI arguments.

    Parameters
    ----------
    fake_args : {None}
      list containing fake CLAs for using without CLI
    """
    cliparser = cli_parser(appname=__appname__, description=__description__, version=__version__)
    if fake_args:
      self.cliargs = cliparser.parse_args(fake_args)
    else:
      self.cliargs = cliparser.parse_args()
    self.fobos = Fobos(cliargs=self.cliargs, print_n=self._print_b, print_w=self._print_r)
    self._postinit()
    return

  def _reset(self):
    """
    Method for restoring default (init) values.
    """
    self.__init__()
    return

  def printf(self):
    """
    Method for returing a pretty formatted printable string of config settings.
    """
    string = ["FoBiS.py settings\n"]
    options = vars(self.cliargs)
    for key, value in options.items():
      string.append(str(key) + ": " + str(value))
    return "".join([s + "\n" for s in string])

  def run_fobis(self, fake_args=None):
    """
    Method for finnaly running FoBiS.py accordingly to the user configuration.

    Parameters
    ----------
    fake_args : {None}
      list containing fake CLAs for using without CLI
    """
    self._reset()
    self._get_cli(fake_args=fake_args)
    if self.cliargs.which == 'rule':
      if self.cliargs.list:
        self.fobos.rules_list(quiet=self.cliargs.quiet)
      elif self.cliargs.execute:
        self.fobos.rule_execute(rule=self.cliargs.execute, quiet=self.cliargs.quiet)
      elif self.cliargs.get:
        self.fobos.get(option=self.cliargs.get, mode=self.cliargs.mode)
      elif self.cliargs.get_output_name:
        self.fobos.get_output_name(mode=self.cliargs.mode)
      elif self.cliargs.ford:
        result = syswork("ford " + self.cliargs.ford)
        if result[0] != 0:
          self._print_r(result[1])
        else:
          self._print_b(result[1])
    else:
      if self.cliargs.lmodes:
        self.fobos.modes_list()
        sys.exit(0)

      if self.cliargs.which == 'clean':
        self._clean()
      if self.cliargs.which == 'build':
        self._build()
    return


# global variables
__initialized__ = False
if not __initialized__:
  __config__ = FoBiSConfig()
  __initialized__ = True
