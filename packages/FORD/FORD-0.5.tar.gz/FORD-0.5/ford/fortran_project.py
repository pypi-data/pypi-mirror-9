#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  project.py
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

#FIXME: Need to add .lower() to all equality tests between strings
#TODO: Set up a list of the packages that this depends on--in particular, toposort

import os
import toposort

import ford.sourceform

class Project(object):
    """
    An object which collects and contains all of the information about the
    project which is to be documented.
    """
    def __init__(self,name,topdir=".",extensions=["f90","f95","f03","f08"],
                 display=['public','protected'], exclude=[],docmark='!'):
        self.name = name
        self.topdir = topdir
        self.extensions = extensions
        self.files = []
        self.modules = []
        self.programs = []
        self.procedures = []
        self.types = []
        self.display = display
        
        ford.sourceform.set_doc_mark(docmark)
        
        # Get all files within topdir, recursively
        srctree = os.walk(topdir)
        for srcdir in srctree:
            curdir = srcdir[0]
            for item in srcdir[2]:
                if item.split('.')[-1] in self.extensions and not item in exclude:
                    # Get contents of the file
                    print "Reading file {}".format(os.path.join(curdir,item))
                    try:
                        self.files.append(ford.sourceform.FortranSourceFile(os.path.join(curdir,item)))
                    except Exception as e:
                        print "Warning: Error parsing {}.\n\t{}".format(os.path.join(curdir,item),e.args[0])
                        continue
                        
                    for module in self.files[-1].modules:
                        self.modules.append(module)
                        for function in module.functions:
                            if function.permission in display:
                                self.procedures.append(function)
                        for subroutine in module.subroutines:
                            if subroutine.permission in display:
                                self.procedures.append(subroutine)
                        for interface in module.interfaces:
                            if interface.permission in display and interface.hasname:
                                self.procedures.append(interface)
                        for dtype in module.types:
                            if dtype.permission in display:
                                self.types.append(dtype)
                    
                    for function in self.files[-1].functions:
                        self.procedures.append(function)
                    for subroutine in self.files[-1].subroutines:
                        self.procedures.append(subroutine)
                    for program in self.files[-1].programs:
                        self.programs.append(program)
                        for function in program.functions:
                            self.procedures.append(function)
                        for subroutine in program.subroutines:
                            self.procedures.append(subroutine)
                        for interface in program.interfaces:
                            if interface.hasname:
                                self.procedures.append(interfaces)
                        for dtype in program.types:
                            self.types.append(dtype)


    def __str__(self):
        return self.name
    
    def correlate(self):
        """
        Associates various constructs with each other.
        """

        print "\nCorrelating information from different parts of your project...\n"
        
        # Match USE statements up with the right modules
        for srcfile in self.files:
            containers = srcfile.modules + srcfile.functions + srcfile.subroutines + srcfile.programs
            for container in containers:
                id_mods(container,self.modules)
            
        # Get the order to process other correlations with
        deplist = {}
        for mod in self.modules:
            deplist[mod] = set(mod.uses)
        ranklist = toposort.toposort_flatten(deplist)
        for proc in self.procedures:
            if proc.parobj == 'sourcefile': ranklist.append(proc[1])
        ranklist.extend(self.programs)
        
        # Perform remaining correlations for the project
        for container in ranklist:
            if type(container) != str:
                container.correlate(self)

    def markdown(self,md):
        """
        Process the documentation with Markdown to produce HTML.
        """
        for src in self.files:
            src.markdown(md)
        return



def id_mods(obj,modlist):
    """
    Match USE statements up with the right modules
    """
    for i in range(len(obj.uses)):
        for candidate in modlist:
            if obj.uses[i].lower() == candidate.name.lower():
                obj.uses[i] = candidate
                break
    for func in obj.functions:
        id_mods(func,modlist)
    for subroutine in obj.subroutines:
        id_mods(subroutine,modlist)
    return

#~ def place_mod(mod,ranklist,usedlist,allmods):
    #~ """
    #~ Places mod within ranklist in the appropriate order.
    #~ """
    #~ # get all modules which are used within this one
    #~ used_here = []
    
    #~ def find_uses(container,uses):
        #~ uses.extend(container.uses)
        #~ for subrtn in container.subroutines:
            #~ find_uses(subrtn,uses)
        #~ for func in container.functions:
            #~ find_uses(func,uses)

    #~ find_uses(mod,used_here)

    #~ # place each such module within the rank
    #~ mod_rank = 0
    #~ for item in used_here:
        #~ num = allmods.index(item)
        #~ if usedlist[num]:
            #~ tmp_rank = place_mod(item,ranklist,usedlist,allmods)
            #~ usedlist[num] = False
        #~ else:
            #~ tmp_rank = ranklist.index(item) + 1
        #~ if tmp_rank > mod_rank: mod_rank = tmp_rank
            

    #~ # Place the current module within the rank, after the last of the contained modules
    #~ num = allmods.index(mod)
    #~ usedlist[num] = False
    #~ ranklist.insert(mod_rank,mod)

    #~ return mod_rank + 1
    
