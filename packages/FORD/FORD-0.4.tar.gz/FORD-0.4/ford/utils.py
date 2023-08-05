#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  utils.py
#  
#  Copyright 2015 Christopher MacMackin <cmacmackin@gmail.com>
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

NOTE_RE = re.compile("@note\s*(.*?)\s*</p>",re.IGNORECASE|re.DOTALL)
WARNING_RE = re.compile("@warning\s*(.*?)\s*</p>",re.IGNORECASE|re.DOTALL)
TODO_RE = re.compile("@todo\s*(.*?)\s*</p>",re.IGNORECASE|re.DOTALL)
BUG_RE = re.compile("@bug\s*(.*?)\s*</p>",re.IGNORECASE|re.DOTALL)


def sub_notes(docs):
    """
    Substitutes the special controls for notes, warnings, todos, and bugs with
    the corresponding div.
    """
    while NOTE_RE.search(docs):
        docs = NOTE_RE.sub("<div class=\"alert alert-info\" role=\"alert\"><h4>Note</h4>\g<1></div></p>",docs)
        
    while WARNING_RE.search(docs):
        docs = WARNING_RE.sub("<div class=\"alert alert-warning\" role=\"alert\"><h4>Warning</h4>\g<1></div></p>",docs)
    
    while TODO_RE.search(docs):
        docs = TODO_RE.sub("<div class=\"alert alert-success\" role=\"alert\"><h4>ToDo</h4>\g<1></div></p>",docs)
    
    while BUG_RE.search(docs):
        docs = BUG_RE.sub("<div class=\"alert alert-danger\" role=\"alert\"><h4>Bug</h4>\g<1></div></p>",docs)

    return docs



def get_parens(line):
    """
    Takes a string starting with an open parenthesis and returns the portion
    of the string going to the corresponding close parenthesis.
    """
    if len(line) == 0: return line
    parenstr = ''
    level = 0
    blevel = 0
    for char in line:
        if char == '(':
            level += 1
        elif char == ')':
            level -= 1
        elif char == '[':
            blevel += 1
        elif char == ']':
            blevel -= 1
        elif (char.isalpha() or char == '_' or char == ':' or char == ',' 
          or char == ' ') and level == 0 and blevel == 0:
            return parenstr
        parenstr = parenstr + char
    
    if level == 0 and blevel == 0: return parenstr    
    raise Exception("Couldn't parse parentheses: {}".format(line))



def paren_split(sep,string):
    """
    Splits the string into pieces divided by sep, when sep is outside of parentheses.
    """
    if len(sep) != 1: raise Exception("Separation string must be one character long")
    retlist = []
    level = 0
    blevel = 0
    left = 0
    for i in range(len(string)):
        if string[i] == "(": level += 1
        elif string[i] == ")": level -= 1
        elif string[i] == "[": blevel += 1
        elif string[i] == "]": blevel -= 1
        elif string[i] == sep and level == 0 and blevel == 0:
            retlist.append(string[left:i])
            left = i+1
    retlist.append(string[left:])
    return retlist


