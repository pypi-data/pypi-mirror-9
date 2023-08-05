<a name="top"></a>
# FoBiS.py [![Latest Version](https://pypip.in/version/FoBiS.py/badge.svg?style=flat)](https://pypi.python.org/pypi/FoBiS.py/) [![GitHub tag](https://img.shields.io/github/tag/szaghi/FoBiS.svg)]()

[![License](https://pypip.in/license/FoBiS.py/badge.svg?style=flat)](https://pypi.python.org/pypi/FoBiS.py/)

### FoBiS.py, Fortran Building System for poor men
A KISS tool for automatic building modern Fortran projects.

### Status
[![Development Status](https://pypip.in/status/FoBiS.py/badge.svg?style=flat)](https://pypi.python.org/pypi/FoBiS.py/)
[![Build Status](https://travis-ci.org/szaghi/FoBiS.svg?branch=master)](https://travis-ci.org/szaghi/FoBiS)
[![Coverage Status](https://img.shields.io/coveralls/szaghi/FoBiS.svg)](https://coveralls.io/r/szaghi/FoBiS)

#### Issues
[![GitHub issues](https://img.shields.io/github/issues/szaghi/FoBiS.svg)]()
[![Ready in backlog](https://badge.waffle.io/szaghi/fobis.png?label=ready&title=Ready)](https://waffle.io/szaghi/fobis)
[![In Progress](https://badge.waffle.io/szaghi/fobis.png?label=in%20progress&title=In%20Progress)](https://waffle.io/szaghi/fobis)
[![Open bugs](https://badge.waffle.io/szaghi/fobis.png?label=bug&title=Open%20Bugs)](https://waffle.io/szaghi/fobis)

#### Python support [![Supported Python versions](https://pypip.in/py_versions/FoBiS.py/badge.svg?style=flat)](https://pypi.python.org/pypi/FoBiS.py/) [![Download format](https://pypip.in/format/FoBiS.py/badge.svg?style=flat)](https://pypi.python.org/pypi/FoBiS.py/)

## Why?
GNU Make, CMake, SCons & Co. are fantastic tools, even too much for a _poor-fortran-man_.

However, the support for modern Fortran project is still poor: in particular, it is quite difficult (and boring) to track the inter-module-dependency hierarchy of project using many module files.

Modern Fortran programs can take great advantage of using modules (e.g. encapsulation), however their compilations can quickly become a nightmare as the number of modules grows. As  a consequence, an automatic build system able to track (on the fly) any changes on the inter-module-dependency hierarchy can save the life of a _poor-fortran-man_.

### Why not use an auto-make-like tool?
There are a lot of alternatives for deal with inter-module-dependency hierarchy, but they can be viewed as a pre-processor for the actual building system (such as auto-make tools or even the Fortran compiler itself that, in most cases, can generate a dependency list of a processed file), thus they introduce another level of complexity... but a _poor-fortran-man_ always loves the KISS (Keep It Simple, Stupid) things!

##### FoBiS.py is designed to do just one thing: build a modern Fortran program without boring you to specify a particular compilation hierarchy.

### OK, what can FoBiS.py do? I am a _poor-fortran-man_, I do not understand you...
Let us consider the following project tree
```bash
└── src
    ├── cumbersome.f90
    └── nested-1
        ├── first_dep.f90
        └── nested-2
            └── second_dep.inc
```
The main program contained into `cumbersome.f90` depends on `first_dep.f90` via the use statement `use NesteD_1`, thus it actually depends on the module `nested_1`. This module depends on `second_dep.inc` via the include statement `include  'second_dep.inc'`. Note that the dependency files are stored in a *cumbersome* nested tree. Write a makefile for this very simple example could waste many minutes... when the modules number increases the time wasted blows up!

It would be very nice to have a tool that automatically track the actual dependency-hierarchy and build the project on the fly, without the necessity to track the dependency-hierarchy changes. FoBiS.py just makes this... and few more things!

Suppose your goal is to build some (all) of the main programs contained into the project tree. In this case FoBiS.py can save your life: just type
```bash
FoBiS.py build
```
in the root of your project and FoBis.py will build all the main programs nested into the current root directory. Obviously, FoBiS.py will not (re-)compile unnecessary objects if they are up-to-date (like the "magic" of a makefile).

FoBiS.py has many (ok... some) others interesting features: if I have convinced you, please read the following.

Go to [Top](#top)

## Main features
+ Automatic parsing of files for dependency-hierarchy creation in case of _use_ and _include_ statements;
+ automatic building of all _programs_ found into the root directory parsed or only a specific selected target;
+ automatic (re-)building when compiling flags change;
+ avoid unnecessary re-compilation (algorithm based on file-timestamp value);
+ simple command line interface (CLI);
+ friendly support for external libraries linking;
+ Intel, GNU and g95 Fortran Compilers support;
+ custom compiler support;
+ configuration-files-free;
+ ... but also configuration-file driven building for complex buildings;
+ parallel compiling enabled by means of concurrent `multiprocessing` jobs;
+ generation of GNU Make makefile  with rules fully supporting dependency-hierarchy for _make-irreducible users_;
+ easy-extensible;
+ well integrate with a flexible pythonic pre-processor, [PreForM.py](https://github.com/szaghi/PreForM).

Go to [Top](#top)

## Documentation
FoBiS.py documentations are hosted on GitHub. The [wiki](https://github.com/szaghi/FoBiS/wiki) and the [README](https://github.com/szaghi/FoBiS) are the main documentation resources. Other sources of documentation are the examples.

Here is a non-comprehensive list of the main topics

| [Install](https://github.com/szaghi/FoBiS/wiki/Install)                                            | [Usage](https://github.com/szaghi/FoBiS/wiki/Usage)                             |
|----------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------|
| [Manual Install](https://github.com/szaghi/FoBiS/wiki/Manual-Installation)                         | [Getting Started](https://github.com/szaghi/FoBiS/wiki/Getting-Started)         |
| [PyPi Install](https://github.com/szaghi/FoBiS/wiki/PyPI-Installation%2C-the-Python-Package-Index) | [A Taste of FoBiS.py](https://github.com/szaghi/FoBiS/wiki/Taste)               |
|                                                                                                    | [fobos: the FoBiS.py makefile](https://github.com/szaghi/FoBiS/wiki/fobos)      |
|                                                                                                    | [FoBiS.py in action](https://github.com/szaghi/FoBiS/wiki/Projects-Using-FoBiS) |

Go to [Top](#top)

## Copyrights
FoBiS.py is an open source project, it is distributed under the [GPL v3](http://www.gnu.org/licenses/gpl-3.0.html) license. A copy of the license should be distributed within FoBiS.py. Anyone interested to use, develop or to contribute to FoBiS.py is welcome. Take a look at the [contributing guidelines](CONTRIBUTING.md) for starting to contribute to the project.

Go to [Top](#top)
