#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  sourceform.py
#  
#  Copyright 2014 Christopher MacMackin <cmacmackin@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  



import re
import os.path
import urllib
from pygments import highlight
from pygments.lexers import FortranLexer
from pygments.formatters import HtmlFormatter

import ford.reader
import ford.utils

VAR_TYPE_RE = re.compile("^integer|real|double\s*precision|character|complex|logical|type|class|procedure",re.IGNORECASE)
VARKIND_RE = re.compile("\((.*)\)|\*\s*(\d+|\(.*\))")
KIND_RE = re.compile("kind\s*=\s*",re.IGNORECASE)
LEN_RE = re.compile("len\s*=\s*",re.IGNORECASE)
ATTRIBSPLIT_RE = re.compile(",\s*(\w.*?)::\s*(.*)\s*")
ATTRIBSPLIT2_RE = re.compile("\s*(::)?\s*(.*)\s*")
ASSIGN_RE = re.compile("(\w+\s*(?:\([^=]*\)))\s*=(?!>)(?:\s*([^\s]+))?")
POINT_RE = re.compile("(\w+\s*(?:\([^=>]*\)))\s*=>(?:\s*([^\s]+))?")
EXTENDS_RE = re.compile("extends\s*\(\s*([^()\s]+)\s*\)")
DOUBLE_PREC_RE = re.compile("double\s+precision",re.IGNORECASE)
QUOTES_RE = re.compile("\"([^\"]|\"\")*\"|'([^']|'')*'",re.IGNORECASE)
PARA_CAPTURE_RE = re.compile("<p>.*?</p>",re.IGNORECASE|re.DOTALL)

base_url = ''
docmark = '!'
predocmark = ''

#TODO: Add ability to note EXTERNAL procedures, PARAMETER statements, and DATA statements.
class FortranBase(object):
    """
    An object containing the data common to all of the classes used to represent
    Fortran data.
    """
    POINTS_TO_RE = re.compile("\s*=>\s*",re.IGNORECASE)
    SPLIT_RE = re.compile("\s*,\s*",re.IGNORECASE)
    
    base_url = ''
    
    def __init__(self,source,first_line,parent=None,inherited_permission=None,
                 strings=[]):
        if inherited_permission:
            self.permission = inherited_permission.lower()
        else:
            self.permission = None
        self.strings = strings
        self.parent = parent
        if self.parent:
            self.parobj = self.parent.obj
        self.obj = type(self).__name__[7:].lower()
        if self.obj == 'subroutine' or self.obj == 'function':
            self.obj = 'proc'
        self._initialize(first_line)
        del self.strings
        self.doc = []
        line = source.next()
        while line[0:2] == "!" + docmark:
            self.doc.append(line[2:])
            line = source.next()
        source.pass_back(line)
        self.hierarchy = []
        cur = self.parent
        while cur:
            self.hierarchy.append(cur)
            cur = cur.parent
        self.hierarchy.reverse()
    
    def get_url(self):
        outstr = "{0}/{1}/{2}.html{3}"
        #~ and self.permission == 'public' and type(self.parent) == FortranSourceFile
        if ( (type(self) == FortranInterface and self.name) or
             (type(self) in [FortranType,FortranSourceFile,FortranProgram,FortranProgram,FortranModule]) or 
             (type(self) in [FortranFunction,FortranSubroutine]) ):
            outstr = urllib.quote(outstr.format(self.base_url,self.obj,self.name.lower().replace('/','\\'),''))
        elif ( (type(self) in [FortranFunction,FortranSubroutine]) or
               (type(self) == FortranBoundProcedure) ):
            outstr = urllib.quote(outstr.format(self.base_url,self.parobj,self.parent.name.lower().replace('/','\\'),self.name.lower().replace('/','\\')))
        else:
            outstr = None
        return outstr
    
    
    def __str__(self):
        outstr = "<a href='{0}'>{1}</a>"
        url = self.get_url()
        if url:
            outstr = outstr.format(url,self.name)
        else:
            if self.name:
                outstr = self.name
            else:
                outstr = ''
        return outstr

    
    def markdown(self,md):
        """
        Process the documentation with Markdown to produce HTML.
        """
        if len(self.doc) > 0:
            if len(self.doc) == 1 and ':' in self.doc[0]:
                words = self.doc[0].split(':')[0].strip()
                if words.lower() not in ['author','date','license','version','category','summary','deprecated']:
                    self.doc.insert(0,'')
                self.doc.append('')
            self.doc = '\n'.join(self.doc)
            self.doc = md.convert(self.doc)
            self.meta = md.Meta
            md.reset()
        else:
            self.doc = ""
            self.meta = {}
    
        for key in self.meta:
            if len(self.meta[key]) == 1:
                self.meta[key] = self.meta[key][0]
            elif key == 'summary':
                self.meta[key] = '\n'.join(self.meta[key])
            
        self.doc = ford.utils.sub_notes(self.doc)
    
        if 'summary' in self.meta:
            self.meta['summary'] = md.convert(self.meta['summary'])
        elif PARA_CAPTURE_RE.search(self.doc):
            self.meta['summary'] = PARA_CAPTURE_RE.search(self.doc).group()

        md_list = []
        if hasattr(self,'variables'): md_list.extend(self.variables)
        if hasattr(self,'types'): md_list.extend(self.types)
        if hasattr(self,'modules'): md_list.extend(self.modules)
        if hasattr(self,'subroutines'): md_list.extend(self.subroutines)
        if hasattr(self,'functions'): md_list.extend(self.functions)
        if hasattr(self,'interfaces'): md_list.extend(self.interfaces)
        if hasattr(self,'programs'): md_list.extend(self.programs)
        if hasattr(self,'boundprocs'): md_list.extend(self.boundprocs)
        # if hasattr(self,'finalprocs'): md_list.extend(self.finalprocs)
        # if hasattr(self,'constructor') and self.constructor: md_list.append(self.constructor)
        if hasattr(self,'args'): md_list.extend(self.args)
        if hasattr(self,'retvar') and self.retvar: md_list.append(self.retvar)
        
        for item in md_list:
            if isinstance(item, FortranBase): item.markdown(md)
        
        return
    


class FortranContainer(FortranBase):
    """
    A class on which any classes requiring further parsing are based.
    """
    PUBLIC_RE = re.compile("^public(\s+|\s*::\s*)((\w|\s|,)+)$",re.IGNORECASE)
    PRIVATE_RE = re.compile("^private(\s+|\s*::\s*)((\w|\s|,)+)$",re.IGNORECASE)
    PROTECTED_RE = re.compile("^protected(\s+|\s*::\s*)((\w|\s|,)+)$",re.IGNORECASE)
    OPTIONAL_RE = re.compile("^optional(\s+|\s*::\s*)((\w|\s|,)+)$",re.IGNORECASE)
    END_RE = re.compile("^end\s*(?:(module|subroutine|function|program|type|interface)(?:\s+(\w+))?)?$",re.IGNORECASE)
    MODPROC_RE = re.compile("^module\s+procedure\s*(?:::|\s)?\s*(\w.*)$",re.IGNORECASE)
    MODULE_RE = re.compile("^module(?:\s+(\w+))?$",re.IGNORECASE)
    PROGRAM_RE = re.compile("^program(?:\s+(\w+))?$",re.IGNORECASE)
    SUBROUTINE_RE = re.compile("^\s*(?:(.+?)\s+)?subroutine\s+(\w+)\s*(\([^()]*\))?(\s*bind\s*\(\s*c.*\))?$",re.IGNORECASE)
    FUNCTION_RE = re.compile("^(?:(.+?)\s+)?function\s+(\w+)\s*(\([^()]*\))?(?:\s*result\s*\(\s*(\w+)\s*\))?(\s*bind\s*\(\s*c.*\))?$",re.IGNORECASE)
    TYPE_RE = re.compile("^type(?:\s+|\s*(,.*)?::\s*)((?!(?:is))\w+)\s*(\([^()]*\))?\s*$",re.IGNORECASE)
    INTERFACE_RE = re.compile("^(abstract\s+)?interface(?:\s+(\S.+))?$",re.IGNORECASE)
    BOUNDPROC_RE = re.compile("^(generic|procedure)\s*(\([^()]*\))?\s*(.*)\s*::\s*(\w.*)",re.IGNORECASE)
    FINAL_RE = re.compile("^final\s*::\s*(\w.*)",re.IGNORECASE)
    VARIABLE_RE = re.compile("^(integer|real|double\s*precision|character|complex|logical|type(?!\s+is)|class(?!\s+is)|procedure)\s*((?:\(|\s\w|[:,*]).*)$",re.IGNORECASE)
    USE_RE = re.compile("^use\s+(\w+)($|,\s*)",re.IGNORECASE)
    CALL_RE = re.compile("^(?:if\s*\(.*\)\s*)?call\s+(\w+)\s*(?:\(\s*(.*?)\s*\))?$",re.IGNORECASE)
    #TODO: Add the ability to recognize function calls
        
    def __init__(self,source,first_line,parent=None,inherited_permission=None,
                 strings=[]):
        if type(self) != FortranSourceFile:
            FortranBase.__init__(self,source,first_line,parent,inherited_permission,
                             strings)
        incontains = False
        permission = "public"
      
        for line in source:
            if line[0:2] == "!" + docmark: 
                self.doc.append(line[2:])
                continue

            # Temporarily replace all strings to make the parsing simpler
            self.strings = []
            search_from = 0
            while QUOTES_RE.search(line[search_from:]):
                self.strings.append(QUOTES_RE.search(line[search_from:]).group())
                line = line[0:search_from] + QUOTES_RE.sub("\"{}\"".format(len(self.strings)-1),line[search_from:],count=1)
                search_from += QUOTES_RE.search(line[search_from:]).end(0)

            # Check the various possibilities for what is on this line
            if line.lower() == "contains":
                if not incontains and type(self) in _can_have_contains:
                    incontains = True
                    if isinstance(self,FortranType): permission = "public"
                elif incontains:
                    raise Exception("Multiple CONTAINS statements present in scope")
                else:
                    raise Exception("CONTAINS statement in {}".format(type(self).__name__[7:].upper()))
            elif line.lower() == "public": permission = "public"
            elif self.PUBLIC_RE.match(line):
                varlist = self.SPLIT_RE.split(self.PUBLIC_RE.match(line).group(2))
                varlist[-1] = varlist[-1].strip()
                if hasattr(self,'public_list'): 
                    self.public_list.extend(varlist)
                else:
                    raise Exception("PUBLIC declaration in {}".format(type(self).__name__[7:].upper()))
            elif line.lower() == "private": permission = "private"
            elif self.PRIVATE_RE.match(line):
                varlist = self.SPLIT_RE.split(self.PRIVATE_RE.match(line).group(2))
                varlist[-1] = varlist[-1].strip()
                if hasattr(self,'private_list'): 
                    self.private_list.extend(varlist)
                else:
                    raise Exception("PRIVATE declaration in {}".format(type(self).__name__[7:].upper()))
            elif line.lower() == "protected": permission = "protected"
            elif self.PROTECTED_RE.match(line):
                varlist = self.SPLIT_RE.split(self.PROTECTED_RE.match(line).group(2))
                varlist[-1] = varlist[-1].strip()
                if hasattr(self,'protected_list'): 
                    self._protected_list.extend(varlist)
                else:
                    raise Exception("PROTECTED declaration in {}".format(type(self).__name__[7:].upper()))
            elif line.lower() == "sequence":
                if type(self) == FortranType: self.sequence = True
            elif self.OPTIONAL_RE.match(line):
                varlist = self.SPLIT_RE.split(self.OPTIONAL_RE.match(line).group(2))
                varlist[-1] = varlist[-1].strip()
                if hasattr(self,'optional_list'): 
                    self._optional_list.extend(varlist)
                else:
                    raise Exception("OPTIONAL declaration in {}".format(type(self).__name__[7:].upper()))
            elif self.END_RE.match(line):
                if isinstance(self,FortranSourceFile):
                    raise Exception("END statement outside of any nesting")
                self._cleanup()
                return
            elif self.MODPROC_RE.match(line):
                if hasattr(self,'modprocs'):
                    self.modprocs.extend(get_mod_procs(source,
                                         self.MODPROC_RE.match(line),self))
                else:
                    raise Exception("Found module procedure in {}".format(type(self).__name__[7:].upper()))
            elif self.MODULE_RE.match(line):
                if hasattr(self,'modules'):
                    self.modules.append(FortranModule(source,
                                        self.MODULE_RE.match(line),self))
                else:
                    raise Exception("Found MODULE in {}".format(type(self).__name__[7:].upper()))
            elif self.PROGRAM_RE.match(line):
                if hasattr(self,'programs'):
                    self.programs.append(FortranProgram(source,
                                         self.PROGRAM_RE.match(line),self))
                else:
                    raise Exception("Found PROGRAM in {}".format(type(self).__name__[7:].upper()))
                if len(self.programs) > 1:
                    raise Exception("Multiple PROGRAM units in same source file.")
            elif self.SUBROUTINE_RE.match(line):
                if isinstance(self,FortranCodeUnit) and not incontains: continue
                if hasattr(self,'subroutines'):
                    self.subroutines.append(FortranSubroutine(source,
                                            self.SUBROUTINE_RE.match(line),self,
                                            permission))
                else:
                    raise Exception("Found SUBROUTINE in {}".format(type(self).__name__[7:].upper()))
            elif self.FUNCTION_RE.match(line):
                if isinstance(self,FortranCodeUnit) and not incontains: continue
                if hasattr(self,'functions'):
                    self.functions.append(FortranFunction(source,
                                          self.FUNCTION_RE.match(line),self,
                                          permission))
                else:
                    raise Exception("Found FUNCTION in {}".format(type(self).__name__[7:].upper()))
            elif self.TYPE_RE.match(line):
                if hasattr(self,'types'):
                    self.types.append(FortranType(source,self.TYPE_RE.match(line),
                                      self,permission))
                else:
                    raise Exception("Found derived TYPE in {}".format(type(self).__name__[7:].upper()))
            elif self.INTERFACE_RE.match(line):
                if hasattr(self,'interfaces'):
                    self.interfaces.append(FortranInterface(source,
                                           self.INTERFACE_RE.match(line),self,
                                           permission))
                else:
                    raise Exception("Found INTERFACE in {}".format(type(self).__name__[7:].upper()))
            elif self.BOUNDPROC_RE.match(line) and incontains:
                if hasattr(self,'boundprocs'):
                    self.boundprocs.append(FortranBoundProcedure(source,
                                           self.BOUNDPROC_RE.match(line),self,
                                           permission))
                else:
                    raise Exception("Found type-bound procedure in {}".format(type(self).__name__[7:].upper()))
            elif self.FINAL_RE.match(line) and incontains:
                if hasattr(self,'finalprocs'):
                    procedures = self.FINAL_RE.match(line).group(1).strip()
                    self.finalprocs.extend(self.SPLIT_RE.split(procedures))
                else:
                    raise Exception("Found finalization procedure in {}".format(type(self).__name__[7:].upper()))
            elif self.VARIABLE_RE.match(line):
                if hasattr(self,'variables'):
                    self.variables.extend(line_to_variables(source,line,
                                          permission,self))
                else:
                    raise Exception("Found variable in {}".format(type(self).__name__[7:].upper()))
            elif self.USE_RE.match(line):
                if hasattr(self,'uses'): 
                    self.uses.append(self.USE_RE.match(line).group(1))
                else:
                    raise Exception("Found USE statemnt in {}".format(type(self).__name__[7:].upper()))
            elif self.CALL_RE.match(line):
                if hasattr(self,'calls'):
                    callval = self.CALL_RE.match(line).group()
                    if self.CALL_RE.match(line).group() not in self.calls: 
                        self.calls.append(callval)
                else:
                    raise Exception("Found procedure call in {}".format(type(self).__name__[7:].upper()))
            
        if not isinstance(self,FortranSourceFile):
            raise Exception("File ended while still nested.")
    
    def _cleanup(self):
        return
        
             
    
class FortranCodeUnit(FortranContainer):
    """
    A class on which programs, modules, functions, and subroutines are based.
    """
    def correlate(self,project):
        # Add procedures, interfaces and types from parent to our lists
        if hasattr(self.parent,'pub_procs'): self.pub_procs.extend(self.parent.pub_procs)
        if hasattr(self.parent,'procs'): self.procs.extend(self.parent.procs)
        #FIXME: It would be better to make the all_interfaces list contain only abstract interfaces, and to start building it during cleanup, as was done for procs
        if hasattr(self.parent,'interfaces'):
            self.all_interfaces = self.interfaces + self.parent.interfaces
        else:
            self.all_interfaces = self.interfaces + []
        if hasattr(self.parent,'all_types'):
            self.all_types = self.types + self.parent.all_types
        else:
            self.all_types = self.types + []
        
        # Add procedures and types from USED modules to our lists
        for mod in self.uses:
            if type(mod) == str: continue
            self.pub_procs.extend(mod.pub_procs)
            self.procs.extend(mod.pub_procs)
            self.all_interfaces.extend(mod.all_interfaces)
            self.all_types.extend(mod.all_types) 
        
        # Match up called procedures
        if hasattr(self,'calls'):
            for i in range(len(self.calls)):
                for proc in self.procs:
                    if self.calls[i] == proc.name:
                        self.calls[i] = proc
                        break
        
        # Recurse
        for func in self.functions:
            func.correlate(project)
        for subrtn in self.subroutines:
            subrtn.correlate(project)
        for dtype in self.types:
            dtype.correlate(project)
        for interface in self.interfaces:
            interface.correlate(project)
        for var in self.variables:
            var.correlate(project)
        if hasattr(self,'args'):
            for arg in self.args:
                arg.correlate(project)
        if hasattr(self,'retvar'):
            #~ print self.name, self.retvar, self.parent.parent.name
            #~ for var in self.variables:
                #~ print var.name
            self.retvar.correlate(project)

        # Prune anything which we don't want to be displayed
        if self.obj == 'module':
            self.functions = [ obj for obj in self.functions if obj.permission in project.display]
            self.subroutines = [ obj for obj in self.subroutines if obj.permission in project.display]
            self.types = [ obj for obj in self.types if obj.permission in project.display]
            self.interfaces = [ obj for obj in self.interfaces if obj.permission in project.display]
            self.variables = [ obj for obj in self.variables if obj.permission in project.display]
       
        
class FortranSourceFile(FortranContainer):
    """
    An object representing individual files containing Fortran code. A project
    will consist of a list of these objects. In tern, SourceFile objects will
    contains lists of all of that file's contents
    """
    def __init__(self,filepath):
        self.path = filepath.strip()
        self.name = os.path.basename(self.path)
        self.parent = None
        self.modules = []
        self.functions = []
        self.subroutines = []
        self.programs = []
        self.doc = []
        self.hierarchy = []
        self.obj = 'sourcefile'
        source = ford.reader.FortranReader(self.path,docmark,predocmark)
        FortranContainer.__init__(self,source,"")
        readobj = open(self.path,'r')
        self.src = readobj.read()
        #~ self.src = highlight(self.src,FortranLexer(),HtmlFormatter(linenos=True))
        # TODO: Get line-numbers working in such a way that it will look right with Bootstrap CSS
        self.src = highlight(self.src,FortranLexer(),HtmlFormatter())



class FortranModule(FortranCodeUnit):
    """
    An object representing individual modules within your source code. These
    objects contains lists of all of the module's contents, as well as its 
    dependencies.
    """
    def _initialize(self,line):
        self.name = line.group(1)
        # TODO: Add the ability to parse ONLY directives and procedure renaming
        self.uses = []
        self.variables = []
        self.public_list = []
        self.private_list = []
        self.protected_list = []
        self.subroutines = []
        self.functions = []
        self.interfaces = []
        self.types = []

    def _cleanup(self):
        # Create list of all local procedures. Ones coming from other modules
        # will be added later, during correlation.
        self.procs = self.functions + self.subroutines
        self.pub_procs = []
        for interface in self.interfaces:
            if interface.name:
                self.procs.append(interface)
            elif not interface.abstract:
                self.procs.extend(interface.functions)
                self.procs.extend(interface.subroutines)

        for name in self.public_list:
            for var in self.variables + self.procs + self.types + self.interfaces:
                if name.lower() == var.name.lower():
                    var.permission = "public"
        for name in self.private_list:
            for var in self.variables + self.procs + self.types + self.interfaces:
                if name.lower() == var.name.lower():
                    var.permission = "private"
        for varname in self.protected_list:
            for var in self.variables:
                if varname.lower() == var.name.lower():
                    var.permission = "protected"

        for proc in self.procs:
            if proc.permission == "public": self.pub_procs.append(proc)

        del self.public_list
        del self.private_list
        del self.protected_list
        return

        
    
class FortranSubroutine(FortranCodeUnit):
    """
    An object representing a Fortran subroutine and holding all of said 
    subroutine's contents.
    """
    def _initialize(self,line):
        self.proctype = 'Subroutine'
        self.name = line.group(2)
        attribstr = line.group(1)
        if not attribstr: attribstr = ""
        self.attribs = []
        if attribstr.find("pure") >= 0:
            self.attribs.append("pure")
            attribstr = attribstr.replace("pure","",1)
        if attribstr.find("elemntal") >= 0:
            self.attribs.append("elemental")
            attribstr = attribstr.replace("elemental","",1)
        if attribstr.find("recursive") >= 0:
            self.attribs.append("recursive")
            attribstr = attribstr.replace("recursive","",1)
        attribstr = re.sub(" ","",attribstr)
        self.name = line.group(2)
        self.args = []
        if line.group(3):
            if self.SPLIT_RE.split(line.group(3)[1:-1]):
                for arg in self.SPLIT_RE.split(line.group(3)[1:-1]):
                    if arg != '': self.args.append(arg.strip())
        self.bindC = bool(line.group(4))
        self.variables = []
        self.uses = []
        self.calls = []
        self.optional_list = []
        self.subroutines = []
        self.functions = []
        self.interfaces = []
        self.types = []

    def _cleanup(self):
        self.procs = self.functions + self.subroutines
        self.pub_procs = []
        for interface in self.interfaces:
            if interface.name:
                self.procs.append(interface)
            elif not interface.abstract:
                self.procs.extend(interface.functions)
                self.procs.extend(interface.subroutines)

        for varname in self.optional_list:
            for var in self.variables:
                if varname.lower() == var.name.lower(): 
                    var.permission = "protected"
                    break
        del self.optional_list
        for i in range(len(self.args)):
            for var in self.variables:
                if self.args[i].lower() == var.name.lower():
                    self.args[i] = var
                    self.variables.remove(var)
                    break
            if type(self.args[i]) == str:
                for intr in self.interfaces:
                    for proc in intr.subroutines + intr.functions:
                        if proc.name.lower() == self.args[i].lower():
                            self.args[i] = proc
                            if proc.proctype == 'Subroutine': intr.subroutines.remove(proc)
                            else: intr.functions.remove(proc)
                            if len(intr.subroutines + intr.functions) < 1:
                                self.interfaces.remove(intr)
                            self.args[i].parent = self
                            break

        return
    
    
class FortranFunction(FortranCodeUnit):
    """
    An object representing a Fortran function and holding all of said function's
    contents.
    """
    def _initialize(self,line):
        self.proctype = 'Function'
        self.name = line.group(2)
        attribstr = line.group(1)
        if not attribstr: attribstr = ""
        self.attribs = []
        if attribstr.find("pure") >= 0:
            self.attribs.append("pure")
            attribstr = attribstr.replace("pure","",1)
        if attribstr.find("elemntal") >= 0:
            self.attribs.append("elemental")
            attribstr = attribstr.replace("elemental","",1)
        if attribstr.find("recursive") >= 0:
            self.attribs.append("recursive")
            attribstr = attribstr.replace("recursive","",1)
        attribstr = re.sub(" ","",attribstr)
        if line.group(4):
            self.retvar = line.group(4)
        else:
            self.retvar = self.name
        if VAR_TYPE_RE.search(attribstr):
            rettype, retkind, retlen, retproto, rest =  parse_type(attribstr,self.strings)
            self.retvar = FortranVariable(self.retvar,rettype,self.parent,
                                          kind=retkind,strlen=retlen,
                                          proto=retproto)
        self.args = [] # Set this in the correlation step
        
        for arg in self.SPLIT_RE.split(line.group(3)[1:-1]):
            # FIXME: This is to avoid a problem whereby sometimes an empty argument list will appear to contain the argument ''. I didn't know why it would do this (especially since sometimes it works fine) and just put this in as a quick fix. However, at some point I should try to figure out the actual root of the problem.
            if arg != '': self.args.append(arg.strip())
        self.bindC = bool(line.group(5))
        self.variables = []
        self.uses = []
        self.calls = []
        self.optional_list = []
        self.subroutines = []
        self.functions = []
        self.interfaces = []
        self.types = []

    def _cleanup(self):
        self.procs = self.functions + self.subroutines
        self.pub_procs = []
        for interface in self.interfaces:
            if interface.name:
                procs.append(interface)
            elif not interface.abstract:
                procs.extend(interface.functions)
                procs.extend(interface.subroutines)

        for varname in self.optional_list:
            for var in self.variables:
                if varname.lower() == var.name.lower():
                    var.permission = "protected"
                    break
        del self.optional_list
        for i in range(len(self.args)):
            for var in self.variables:
                if self.args[i].lower() == var.name.lower():
                    self.args[i] = var
                    self.variables.remove(var)
                    break
            if type(self.args[i]) == str:
                for intr in self.interfaces:
                    for proc in intr.subroutines + intr.functions:
                        if proc.name.lower() == self.args[i].lower():
                            self.args[i] = proc
                            if proc.proctype == 'Subroutine': intr.subroutines.remove(proc)
                            else: intr.functions.remove(proc)
                            if len(intr.subroutines + intr.functions) < 1:
                                self.interfaces.remove(intr)
                            self.args[i].parent = self
                            break
        if type(self.retvar) != FortranVariable:
            for var in self.variables:
                if var.name.lower() == self.retvar.lower():
                    self.retvar = var
                    self.variables.remove(var)
                    break

        return
        
        
    
class FortranProgram(FortranCodeUnit):
    """
    An object representing the main Fortran program.
    """
    def _initialize(self,line):
        self.name = line.group(1)
        self.variables = []
        self.subroutines = []
        self.functions = []
        self.interfaces = []
        self.types = []
        self.uses = []
        self.calls = []
    
    def _cleanup(self):
        self.procs = self.functions + self.subroutines
        self.pub_procs = []
        for interface in self.interfaces:
            if interface.name:
                procs.append(interface)
            elif not interface.abstract:
                procs.extend(interface.functions)
                procs.extend(interface.subroutines)

    
    
class FortranType(FortranContainer):
    """
    An object representing a Fortran derived type and holding all of said type's
    components and type-bound procedures. It also contains information on the
    type's inheritance.
    """
    def _initialize(self,line):
        self.name = line.group(2)
        self.extends = None
        self.attributes = []
        if line.group(1):
            attribstr = line.group(1)[1:].strip()
            attriblist = self.SPLIT_RE.split(attribstr.strip())
            for attrib in attriblist:
                if EXTENDS_RE.search(attrib):
                    self.extends = EXTENDS_RE.search(attrib).group(1)
                elif attrib.strip().lower() == "public":
                    self.permission = "public"
                elif attrib.strip().lower() == "private":
                    self.permission = "private"
                else:
                    self.attributes.append(attrib.strip())
        if line.group(3):
            paramstr = line.group(3).strip()
            self.parameters = self.SPLIT_RE.split(paramstr)
        else:
            self.parameters = []
        self.sequence = False
        self.variables = []
        self.boundprocs = []
        self.finalprocs = []
        self.constructor = None
        
        
    def _cleanup(self):
        # Match parameters with variables
        for i in range(len(self.parameters)):
            for var in self.variables:
                if self.parameters[i].lower() == var.name.lower():
                    self.parameters[i] = var
                    self.variables.remove(var)
                    break

        
    def correlate(self,project):
        self.all_interfaces = self.parent.all_interfaces
        self.all_types = self.parent.all_types
        self.procs = self.parent.procs
        # Get type of extension
        if self.extends:
            for dtype in self.all_types:
                if dtype.name.lower() == self.extends.lower():
                    self.extends = dtype
                    break
        # Match variables as needed (recurse)
        for i in range(len(self.variables)-1,-1,-1):
            if self.variables[i].permission in project.display:
                self.variables[i].correlate(project)
            else:
                del self.variables[i]
        # Match boundprocs with procedures
        for proc in self.boundprocs:
            if proc.permission in project.display:
                proc.correlate(project)
            else:
                self.boundprocs.remove(proc)
        # Match finalprocs
        for i in range(len(self.finalprocs)):
            for proc in self.procs:
                if proc.name.lower() == self.finalprocs[i].lower():
                    self.finalprocs[i] = proc
                    break
        # Find a constructor, if one exists
        for proc in self.procs:
            if proc.name.lower() == self.name.lower():
                self.constructor = proc
                break
        
        # Prune anything which we don't want to be displayed
        self.boundprocs = [ obj for obj in self.boundprocs if obj.permission in project.display ]
        self.variables = [ obj for obj in self.variables if obj.permission in project.display ]

        
    
class FortranInterface(FortranContainer):
    """
    An object representing a Fortran interface.
    """
    def _initialize(self,line):
        self.proctype = 'Interface'
        self.abstract = bool(line.group(1))
        self.name = line.group(2)
        self.hasname = bool(self.name)
        self.subroutines = []
        self.functions = []
        self.modprocs = []

    def _cleanup(self):
        if not self.hasname:
            contents = self.subroutines + self.functions
            self.name = contents[0].name
    
    def correlate(self,project):
        if self.abstract: return
        self.all_interfaces = self.parent.all_interfaces
        self.all_types = self.parent.all_types
        self.procs = self.parent.procs
        for modproc in self.modprocs:
            for proc in self.procs:
                if modproc.name.lower() == proc.name.lower():
                    modproc.procedure = proc
                    break
        for subrtn in self.subroutines:
            subrtn.correlate(project)
            #~ for proc in self.parent.procs:
                #~ if subrtn.name.lower() == proc.name.lower():
                    #~ subrtn.procedure = proc
                    #~ break
        for func in self.functions:
            func.correlate(project)
            #~ for proc in self.parent.procs:
                #~ if func.name.lower() == proc.name.lower():
                    #~ func.procedure = proc
                    #~ break
                    
    
    
class FortranVariable(FortranBase):
    """
    An object representing a variable within Fortran.
    """
    def __init__(self,name,vartype,parent,attribs=[],intent="inout",
                 optional=False,permission="public",parameter=False,kind=None,
                 strlen=None,proto=None,doc=[],points=False,initial=None):
        self.name = name
        self.vartype = vartype.lower()
        self.parent = parent
        if self.parent:
            self.parobj = self.parent.obj
        self.obj = type(self).__name__[7:].lower()
        self.attribs = attribs
        self.intent = intent
        self.optional = optional
        self.kind = kind
        self.strlen = strlen
        self.proto = proto
        self.doc = doc
        self.permission = permission
        self.points = points
        self.parameter = parameter
        self.doc = []
        self.initial = initial
        self.dimension = ''
        index = self.name.find('(')
        if index > 0 :
            self.dimension = self.name[index:]
            self.name = self.name[0:index]

    def correlate(self,project):
        if self.proto and self.proto[0] == '*': self.proto[0] = '*'
        if (self.vartype == "type" or self.vartype == "class") and self.proto and self.proto[0] != '*':
            for dtype in self.parent.all_types:
                if dtype.name.lower() == self.proto[0].lower(): 
                    self.proto[0] = dtype
                    break
        elif self.vartype == "procedure" and self.proto:
            for proc in self.parent.procs:
                if proc.name.lower() == self.proto.lower():
                    self.proto = proc
                    break
            if type(self.proto) == str:
                for interface in self.parent.all_interfaces:
                    if interface.abstract:
                        for proc in interface.subroutines + interface.functions:
                            if proc.name.lower() == self.proto.lower():
                                self.proto = interface
                                break
            


class FortranBoundProcedure(FortranBase):
    """
    An object representing a type-bound procedure, possibly overloaded.
    """
    def _initialize(self,line):
        attribstr = line.group(3)
        self.attribs = []
        if attribstr:
            tmp_attribs = ford.utils.paren_split(",",attribstr[1:])
            for i in range(len(tmp_attribs)):
                tmp_attribs[i] = tmp_attribs[i].strip()
                if tmp_attribs[i].lower() == "public": self.permission = "public"
                elif tmp_attribs[i].lower() == "private": self.permission = "private"
                else: self.attribs.append(tmp_attribs[i])
        rest = line.group(4)
        split = self.POINTS_TO_RE.split(rest)
        self.name = split[0]
        self.generic = (line.group(1).lower() == "generic")
        self.bindings = []
        if len(split) > 1:
            binds = self.SPLIT_RE.split(split[1])
            for bind in binds:
                self.bindings.append(bind.strip())
        else:
            self.bindings.append(self.name)
        if line.group(2):
            self.prototype = line.group(2)[1:-1]
        else:
            self.prototype = None

    def correlate(self,project):
        self.procs = self.parent.procs
        for i in range(len(self.bindings)):
            for proc in self.procs:
                if proc.name.lower() == self.bindings[i].lower():
                    self.bindings[i] = proc
                    break
        
        

class FortranModuleProcedure(FortranBase):
    """
    An object representing a module procedure procedure.
    """
    def __init__(self,name,parent=None,inherited_permission=None):
        if inherited_permission:
            self.permission = inherited_permission.lower()
        else:
            self.permission = None
        self.parent = parent
        if self.parent:
            self.parobj = self.parent.obj
        self.obj = 'moduleprocedure'
        self.name = name
        self.procedure = None
        self.doc = []
        self.hierarchy = []
        cur = self.parent
        while cur:
            self.hierarchy.append(cur)
            cur = cur.parent
        self.hierarchy.reverse()
                

_can_have_contains = [FortranModule,FortranProgram,FortranFunction,
                      FortranSubroutine,FortranType]
        
def line_to_variables(source, line, inherit_permission, parent):
    """
    Returns a list of variables declared in the provided line of code. The
    line of code should be provided as a string.
    """
    vartype, kind, strlen, proto, rest = parse_type(line,parent.strings)
    attribs = []
    intent = "inout"
    optional = False
    permission = inherit_permission
    parameter = False
    
    attribmatch = ATTRIBSPLIT_RE.match(rest)
    if attribmatch:
        attribstr = attribmatch.group(1).strip()
        declarestr = attribmatch.group(2).strip()
        tmp_attribs = ford.utils.paren_split(",",attribstr)
        for i in range(len(tmp_attribs)):
            tmp_attribs[i] = tmp_attribs[i].strip()
            if tmp_attribs[i].lower() == "public": permission = "public"
            elif tmp_attribs[i].lower() == "private": permission = "private"
            elif tmp_attribs[i].lower() == "protected": permission = "protected"
            elif tmp_attribs[i].lower() == "optional": optional = True
            elif tmp_attribs[i].lower() == "parameter": parameter = True
            elif tmp_attribs[i].lower().replace(' ','') == "intent(in)":
                intent = 'in'
            elif tmp_attribs[i].lower().replace(' ','') == "intent(out)":
                intent = 'out'
            elif tmp_attribs[i].lower().replace(' ','') == "intent(inout)":
                pass
            else: attribs.append(tmp_attribs[i])
    else:
        declarestr = ATTRIBSPLIT2_RE.match(rest).group(2)
    declarations = ford.utils.paren_split(",",declarestr)

    varlist = []
    for dec in declarations:
        dec = re.sub(" ","",dec)
        split = ford.utils.paren_split('=',dec)
        if len(split) > 1:
            if split[1][0] == '>':
                name = split[0]
                initial = split[1][1:]
                points = True
            else:
                name = split[0]
                initial = split[1]
                points = False
        else:
            name = dec.strip()
            initial = None
            points = False
            
        if initial and vartype == "character":
            match = QUOTES_RE.search(initial)
            if match:
                num = int(match.group()[1:-1])
                initial = QUOTES_RE.sub(parent.strings[num],initial)
            # FIXME: add some code that will replace any spaces at the edges of a string with &nbsp;
            # What I have below is just a stop-gap measure. And it doesn't even seem to work...
            initial.replace("' '","'&nbsp;'")
            initial.replace('" "','"&nbsp;"')
            
        if proto:
            varlist.append(FortranVariable(name,vartype,parent,attribs,intent,
                           optional,permission,parameter,kind,strlen,list(proto),
                           [],points,initial))
        else:
            varlist.append(FortranVariable(name,vartype,parent,attribs,intent,
                           optional,permission,parameter,kind,strlen,proto,
                           [],points,initial))
        
    doc = []
    docline = source.next()
    while docline[0:2] == "!" + docmark:
        doc.append(docline[2:])
        docline = source.next()
    source.pass_back(docline)
    varlist[-1].doc = doc
    return varlist
    
    

def parse_type(string,capture_strings):
    """
    Gets variable type, kind, length, and/or derived-type attributes from a 
    variable declaration.
    """
    match = VAR_TYPE_RE.match(string)
    if not match: raise Exception("Invalid variable declaration: {}".format(string))
    
    vartype = match.group().lower()
    if DOUBLE_PREC_RE.match(vartype): vartype = "double precision"
    rest = string[match.end():].strip()
    kindstr = ford.utils.get_parens(rest)
    rest = rest[len(kindstr):].strip()

    # FIXME: This won't work for old-fashioned REAL*8 type notations
    if len(kindstr) < 3 and vartype != "type" and vartype != "class":
        return (vartype, None, None, None, rest)
    match = VARKIND_RE.search(kindstr)
    if match:
        if match.group(1):
            star = False
            args = match.group(1).strip()
        else:
            star = True
            args = match.group(2).strip()

        args = re.sub("\s","",args)
        if vartype == "type" or vartype == "class" or vartype == "procedure":
            PROTO_RE = re.compile("(\*|\w+)\s*(?:\((.*)\))?")
            try:
                proto = list(PROTO_RE.match(args).groups())
                if not proto[1]: proto[1] = ''
            except:
                raise Exception("Bad type, class, or procedure prototype specification: {}".format(args))
            return (vartype, None, None, proto, rest)
        elif vartype == "character":
            if star:
                return (vartype, None, args[1], None, rest)
            else:
                kind = None
                length = None
                if KIND_RE.search(args):
                    kind = KIND_RE.sub("",args)
                    try:
                        match = QUOTES_RE.search(kind)
                        num = int(match.group()[1:-1])
                        kind = QUOTES_RE.sub(captured_strings[num],kind)
                    except:
                        pass
                elif LEN_RE.search(args):
                    length = LEN_RE.sub("",args)
                else:
                    length = args
                return (vartype, kind, length, None, rest)
        else: 
            kind = KIND_RE.sub("",args)
            return (vartype, kind, None, None, rest)

    raise Exception("Bad declaration of variable type {}: {}".format(vartype,string))


def set_base_url(url):
    FortranBase.base_url = url

def set_doc_mark(mark,premark):
    global docmark
    docmark = mark
    global predocmark
    predocmark = premark

def get_mod_procs(source,line,parent):
    inherit_permission = parent.permission
    retlist = []
    SPLIT_RE = re.compile("\s*,\s*",re.IGNORECASE)
    splitlist = SPLIT_RE.split(line.group(1))
    if splitlist and len(splitlist) > 0:
        for item in splitlist:
            retlist.append(FortranModuleProcedure(item,parent,inherit_permission))
    else:
        retlist.append(FortranModuleProcedure(line.group(1),parent,inherit_permission))
    
    doc = []
    docline = source.next()
    while docline[0:2] == "!" + docmark:
        doc.append(docline[2:])
        docline = source.next()
    source.pass_back(docline)
    retlist[-1].doc = doc
    
    return retlist
