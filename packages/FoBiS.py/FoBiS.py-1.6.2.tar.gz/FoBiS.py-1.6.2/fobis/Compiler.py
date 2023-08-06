#!/usr/bin/env python
"""
Compiler.py, module definition of Compiler class.
This is a class designed for handling compilers default support.
"""


class Compiler(object):
  """
  Compiler is an object that handles the compilers default support, its attributes and methods.

  Attributes
  ----------
  supported : {['gnu', 'intel', 'g95']}
    list of supported compilers
  """

  supported = ['gnu', 'intel', 'g95']

  def __init__(self, cliargs):
    """
    Parameters
    ----------
    cliargs : argparse object

    Attributes
    ----------
    compiler : {None}
      str containing compiler vendor name
    fcs : {None}
      str containing compiler statement
    cflags : {None}
      str containing compiling flags
    lflags : {None}
      str containing linking flags
    preproc : {None}
      str containing preprocessing flags
    modsw : {None}
      str containing compiler switch for modules searching path
    mpi : {False}
      activate the MPI compiler
    openmp : {False}
      activate the OpenMP pragmas
    coverage : {False}
      activate the coverage instruments
    profile : {False}
      activate the profile instruments
    """
    self._mpi = None
    self._openmp = None
    self._coverage = None
    self._profile = None
    self.compiler = cliargs.compiler
    if self.compiler:
      if self.compiler.lower() == 'gnu':
        self._gnu()
      elif self.compiler.lower() == 'intel':
        self._intel()
      elif self.compiler.lower() == 'g95':
        self._g95()
      elif self.compiler.lower() == 'custom':
        pass  # set by user options
      else:
        self._gnu()
    # overriding default values if passed
    if cliargs.fc:
      self.fcs = cliargs.fc
    if cliargs.cflags:
      self.cflags = cliargs.cflags
    if cliargs.lflags:
      self.lflags = cliargs.lflags
    if cliargs.preproc:
      self.preproc = cliargs.preproc
    if cliargs.modsw:
      self.modsw = cliargs.modsw
    self.mpi = cliargs.mpi
    self.openmp = cliargs.openmp
    self.coverage = cliargs.coverage
    self.profile = cliargs.profile
    self._set_fcs()
    self._set_cflags()
    self._set_lflags()
    return

  def __str__(self):
    return self.pprint()

  def _gnu(self):
    """Method for setting compiler defaults to the GNU gfortran compiler options."""
    self.compiler = 'gnu'
    self.fcs = 'gfortran'
    self.cflags = '-c'
    self.lflags = ''
    self.preproc = ''
    self.modsw = '-J '
    self._mpi = 'mpif90'
    self._openmp = ['-fopenmp', '-fopenmp']
    self._coverage = ['-ftest-coverage -fprofile-arcs', '-fprofile-arcs']
    self._profile = ['-pg', '-pg']
    return

  def _intel(self):
    """Method for setting compiler defaults to the Intel Fortran compiler options."""
    self.compiler = 'intel'
    self.fcs = 'ifort'
    self.cflags = '-c'
    self.lflags = ''
    self.preproc = ''
    self.modsw = '-module '
    self._mpi = 'mpif90'
    self._openmp = ['-openmp', '-openmp']
    self._coverage = ['-prof-gen=srcpos', '']
    self._profile = ['', '']
    return

  def _g95(self):
    """Method for setting compiler defaults to the g95 compiler options."""
    self.compiler = 'g95'
    self.fcs = 'g95'
    self.cflags = '-c'
    self.lflags = ''
    self.preproc = ''
    self.modsw = '-fmod='
    self._mpi = 'mpif90'
    self._openmp = ['', '']
    self._coverage = ['', '']
    self._profile = ['', '']
    return

  def _set_fcs(self):
    """Method for setting the compiler command statement directly depending on the compiler."""
    if self.compiler.lower() in Compiler.supported:
      if self.mpi:
        self.fcs = self._mpi
    return

  def _set_cflags(self):
    """Method for setting the compiling flags directly depending on the compiler."""
    if self.coverage:
      if self._coverage[0] != '':
        self.cflags += ' ' + self._coverage[0]
    if self.profile:
      if self._profile[0] != '':
        self.cflags += ' ' + self._profile[0]
    if self.openmp:
      if self._openmp[0] != '':
        self.cflags += ' ' + self._openmp[0]
    if self.preproc is not None:
      if self.preproc != '':
        self.cflags += ' ' + self.preproc
    return

  def _set_lflags(self):
    """Method for setting the linking flags directly depending on the compiler."""
    if self.coverage:
      if self._coverage[1] != '':
        self.lflags += ' ' + self._coverage[1]
    if self.profile:
      if self._profile[1] != '':
        self.lflags += ' ' + self._profile[1]
    if self.openmp:
      if self._openmp[1] != '':
        self.lflags += ' ' + self._openmp[1]
    return

  def compile_cmd(self, mod_dir):
    """
    Method returning the compile command accordingly to the compiler options.

    Parameters
    ----------
    mod_dir : str
      path of the modules directory
    """
    return self.fcs + ' ' + self.cflags + ' ' + self.modsw + mod_dir

  def link_cmd(self, mod_dir):
    """
    Method returning the compile command accordingly to the compiler options.

    Parameters
    ----------
    mod_dir : str
      path of the modules directory
    """
    return self.fcs + ' ' + self.lflags + ' ' + self.modsw + mod_dir

  def pprint(self, prefix=''):
    """
    Pretty printer.

    Parameters
    ----------
    prefix : {''}
      prefixing string of each line
    """
    string = prefix + 'Compiler options\n'
    string += prefix + '  Vendor: "' + self.compiler.strip() + '"\n'
    string += prefix + '  Compiler command: "' + self.fcs.strip() + '"\n'
    string += prefix + '  Module directory switch: "' + self.modsw.strip() + '"\n'
    string += prefix + '  Compiling flags: "' + self.cflags.strip() + '"\n'
    string += prefix + '  Linking flags: "' + self.lflags.strip() + '"\n'
    string += prefix + '  Preprocessing flags: "' + self.preproc.strip() + '"\n'
    string += prefix + '  Coverage: ' + str(self.coverage) + '\n'
    if self.coverage:
      string += prefix + '    Coverage compile and link flags: ' + str(self._coverage) + '\n'
    string += prefix + '  Profile: ' + str(self.profile) + '\n'
    if self.profile:
      string += prefix + '    Profile compile and link flags: ' + str(self._profile) + '\n'
    return string
