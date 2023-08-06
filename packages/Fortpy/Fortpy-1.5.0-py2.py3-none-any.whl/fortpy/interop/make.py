"""This module generates makefiles for the unit testing package as well as
for the shared libraries required by the ftypes interop package.
"""
def makefile(identifier, dependencies, makepath, compileid,
             precompile=False, inclfortpy=True, parser=None,
             executable=True, extralinks=None):
    """Generates a makefile to create the unit testing executable
    for the specified test identifier.

    :arg identifier: the id of the test/library that this makefile should be made for.
    :arg dependencies: a list of the module names that need to be included in the compilation.
    :arg makepath: the path to the file to save the Makefile in.
    :arg compileid: the 'module.executable' that this Makefile is being produced for.
    :arg precompile: when True, the precompiler flags will be added to the makefile.
    :arg inclfortpy: when True, the fortpy module will be added first to the list of modules
      to compile for the executable/library.
    :arg parser: if the module file names are different from the module names, specify a
      code parser to use for converting one to the other. 
    :arg executable: when true and executable is compiled for rule 'all', else the library
      is the default and the executable is set as a different rule for 'identifier'.x.
    :arg extralinks: a list of additional libraries to link in with the explicitly compiled
      f90 files. These aren't checked at all, just added to the linklist.
    """
    lines = []

    #Append the general variables
    lines.append("EXENAME\t\t= {}.x".format(identifier))
    lines.append("SHELL\t\t= /bin/bash")
    lines.append("UNAME\t\t= $(shell uname)")
    lines.append("HOSTNAME\t= $(shell hostname)")
    lines.append("LOG\t\t= compile.log")
    lines.append("")

    #Now the standard entries for ifort. We will just have the ifort include
    #file so that the MPI and other options can be tested to.
    lines.append(_make_compiler_include(precompile, extralinks))
    lines.append(".SILENT:")
    lines.append("")
    
    #Append all the dependent modules to the makefile
    lines.append("LIBMODULESF90\t= \\")
    if inclfortpy:
        #Copy over the fortpy module in case we need it.
        lines.append("\t\tfortpy.f90 \\")

    for modk in dependencies[0:-1]:
        if modk != "fortpy" and modk != identifier:
            if parser is not None:
                lines.append("\t\t{} \\".format(_get_mapping(parser, modk)))
            else:
                lines.append("\t\t{} \\".format(modk))

    if parser is not None:
        lines.append("\t\t{}".format(_get_mapping(parser, dependencies[-1])))
    else:
        lines.append("\t\t{}".format(dependencies[-1]))

    lines.append("MAINF90\t\t= {}.f90".format(identifier))
    lines.append("SRCF90\t\t= $(LIBMODULESF90) $(MAINF90)")
    lines.append("OBJSF90\t\t= $(SRCF90:.f90=.o)")
    lines.append("SLIBF90\t\t= $(LIBMODULESF90:.f90=.o)")
    lines.append("")

    #Add explicitly defined libraries that should be included when linking
    #the unit testing executable.
    linklibs = _add_explicit_includes(lines, dependencies, extralinks)
    lines.append("")

    #We need to add the error handling commands to make debugging compiling easier.
    lines.append(_make_error())
    lines.append("")

    main = "$(EXENAME)" if executable == True else "{}.{}".format(identifier, executable)
    lines.append("all:	info {}".format(main))
    lines.append(_make_info(compileid))
    lines.append(_make_exe(linklibs, identifier))

    from os import path
    makedir, makef = path.split(makepath)
    lines[-1] += "	make -f '{}'".format(makef)

    with open(makepath, 'w') as f:
        f.writelines("\n".join(lines))

def get_fortpy_templates():
    import fortpy
    from os import path
    return path.join(path.dirname(fortpy.__file__), "templates")
        
def _add_explicit_includes(lines, dependencies=None, extralinks=None):
    """Adds any relevant libraries that need to be explicitly included according
    to the fortpy configuration file. Libraries are appended to the specified
    collection of lines. Returns true if relevant libraries were added.
    """
    from fortpy import config
    import sys
    from os import path
    includes = sys.modules["config"].includes
    linklibs = False

    if extralinks is not None and len(extralinks) > 0:
        for i, link in enumerate(extralinks):
            lines.append("LBD{0:d} 		= {1}".format(i, link))
        lines.append("")
    
    if len(includes) > 0:
        lines.append("LIBS\t\t= \\")
        for library in includes:
            addlib = False
            if "modules" in library:
                #We need to loop over the modules specified for the library and see
                #if any of them are in our list of modules.
                for libmod in library["modules"]:
                    if dependencies is None or libmod.lower() in dependencies:
                        addlib = True
                        break
            else:
                addlib = True

            if addlib:
                linklibs = True
                lines.append("\t\t{} \\".format(library["path"]))

        #These links specify explicit libraries to include in the final compilation.
        if extralinks is not None:
            for i in range(len(extralinks)):
                if path.isfile(extralinks[i]):
                    lines.append("\t\t$(LBD{0:d}) \\".format(i))
            
    return linklibs or (extralinks is not None and len(extralinks) > 0)

def _make_compiler_include(precompile, extralinks):
    """Returns the include statement for the compiler to use."""
    #We need to see whether to include the pre-compiler directive or not.
    base = """ifeq ($(F90),ifort)
  include {2}/Makefile.ifort{0}{3}
else
ifeq ($(F90),gfortran)
  include {2}/Makefile.gfortran{1}{3}
else
  include Makefile.error
endif
endif"""
    if extralinks is not None and len(extralinks) > 0:
        from os import path
        libs = []
        for i, link in enumerate(extralinks):
            #We can only include *directories* for the -I specification.
            if path.isdir(link):
                libs.append("-I$(LBD{0:d})".format(i))
        exlinks = "\n  FFLAGS += {}".format(' '.join(libs))
    else:
        exlinks = ""
    
    if precompile:
        insert = ["\n  FFLAGS += -fpp -save-temps -heap-arrays", "\n  FFLAGS += -cpp",
                  get_fortpy_templates(), exlinks]
        return base.format(*insert)
    else:
        return base.format("", "", get_fortpy_templates(), exlinks)

def _make_error():
    """Generates script for compile-time error handling."""
    return """
# Error handling
NEWFILE		= \#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#\#
ERR		= ******************************* ERROR *******************************
SHOW_LOG	= ( perl -pi -e 's/ [Ee]rror \#/\\n\\n\\n$(ERR)\\n*** error \#/' $(LOG); perl -pi -e 's/^\# 1 \"/\\n\\n$(NEWFILE)\\n\\n\\n/' $(LOG); grep -n -A3 -E "$(ERR)|$(NEWFILE)" $(LOG) )
"""

def _make_exe(linklibs, identifier):
    """Generates the script to run the compiling."""
    linktxt = "$(LIBS) " if linklibs else ""
    base = """
$(EXENAME): $(OBJSF90)
	-rm $(EXENAME) 2> /dev/null
	echo -n "Linking... "
	-$(F90) $(LDFLAGS) -o $(EXENAME) $(OBJSF90) {0}>> $(LOG) 2>> $(LOG)
	echo "done."
	if test -e $(EXENAME); then echo "Produced executable: $(EXENAME)"; else $(SHOW_LOG); echo "Error."; fi

$(OBJSF90): %.o: %.f90
	echo -n "Compiling: $^... "
	-$(F90) -c $(FFLAGS) $^ >> $(LOG) 2>> $(LOG)
	echo "done."

{1}.so: $(SLIBF90)
	-rm {1}.so 2> /dev/null
	echo -n "Creating shared library..."
	-$(F90) -shared -fPIC $(FFLAGS) -o {1}.so {0}$(SLIBF90) >> $(LOG) 2>> $(LOG)
	echo "done."

{1}.a: $(SLIBF90)
	echo -n "Creating linked library..."
	ar ru $@ $?
	ranlib $@
	echo "done."

clean:
	-rm *.o *.mod *.i90 $(EXENAME) {1}.so
remake:
	-rm *.o *.mod *.i90 $(EXENAME) {1}.so
"""
    return base.format(linktxt, identifier)

def _make_info(identifier):
    """Generates the script for displaying compile-time info."""
    module, method = identifier.split(".")
    return """
info: 
	echo -e "\\nCompile time:" > $(LOG)
	date >> $(LOG)
	echo "------------------------------------------------------"| tee -a $(LOG)
	echo "                     FORTPY"                           | tee -a $(LOG)
	echo "               >>> version 1.4 <<<                    "| tee -a $(LOG)         
	echo "------------------------------------------------------"| tee -a $(LOG)
	echo -e "Compiling on system  : $(UNAME)"                    | tee -a $(LOG)
	echo -e "             machine : $(HOSTNAME)"                 | tee -a $(LOG)
	echo "Compiling for module : {0}"                            | tee -a $(LOG)         
	echo "              method : {1}"                            | tee -a $(LOG)         
	echo "------------------------------------------------------"| tee -a $(LOG)
	echo -e "DEBUG mode\\t:\\t$(DEBUG)"                          | tee -a $(LOG)
	echo -e "GPROF mode\\t:\\t$(GPROF)"                          | tee -a $(LOG)
	echo "------------------------------------------------------"| tee -a $(LOG)
	echo "F90    : $(F90)"                                       | tee -a $(LOG)
	echo "FFLAGS : $(FFLAGS)"                                    | tee -a $(LOG)
	echo "LDFLAGS: $(LDFLAGS)"                                   | tee -a $(LOG)
	echo "MKLpath:$(MKL)"                                        | tee -a $(LOG)
	echo "------------------------------------------------------"| tee -a $(LOG)
	echo ""                                                      | tee -a $(LOG)

""".format(module, method)

def _get_mapping(parser, mapped):
    """Gets the original file name for a module that was mapped
    when the module name does not coincide with the file name
    that the module was defined in."""
    if mapped in parser.mappings:
        return parser.mappings[mapped]
    else:
        return mapped + ".f90"
