#!/usr/bin/env python 
#version 2.12
#author tobyrosen@gmail.com
"""
Copyright (c) 2011, Sony Pictures Imageworks
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import optparse
import sys
import os
import time
import json
import glob
import tempfile
import datetime
import getpass
import re


#try to import user customized classes if they exist. default is null class.
try:
    from PypCustom import PypCustom
except ImportError:
    class PypCustom():
        pass

try:
    from PypCustom import PowerPipeListCustom
except ImportError :
    class PowerPipeListCustom():
        pass

try:
    from PypCustom import PypStrCustom
except ImportError  :
    class PypStrCustom():
        pass
        
try :
    from PypCustom import PypListCustom
except ImportError:
    class PypListCustom():
        pass

try:
    from PypCustom import PypFunctionCustom
except ImportError:
    class PypFunctionCustom():
        pass


class Colors(object):
    '''defines basic color scheme'''
    OFF = chr(27) + '[0m' 
    RED = chr(27) + '[31m'
    GREEN = chr(27) + '[32m'
    YELLOW = chr(27) + '[33m'
    MAGENTA = chr(27) + '[35m'
    CYAN = chr(27) + '[36m'
    WHITE = chr(27) + '[37m'
    BLUE = chr(27) + '[34m'
    BOLD = chr(27) + '[1m'
    COLORS = [OFF, RED, GREEN, YELLOW, MAGENTA, CYAN, WHITE, BLUE, BOLD]
    
class NoColors(object):
    '''defines basic null color scheme'''
    OFF = ''
    RED = ''
    GREEN =''
    YELLOW = ''
    MAGENTA = ''
    CYAN = ''
    WHITE =''
    BLUE =  ''
    BOLD =  ''
    COLORS = [OFF, RED, GREEN, YELLOW, MAGENTA, CYAN, WHITE, BLUE, BOLD]
      
class PowerPipeList(list,PowerPipeListCustom):
    '''
    defines pp object, allows manipulation of entire input using python list methods
    '''
    def __init__(self, *args):
        super(PowerPipeList, self).__init__(*args)
        try:
            PowerPipeListCustom.__init__(self)
        except AttributeError:
            pass
        self.pyp = Pyp()
        
    
    def divide(self, n_split):
        '''
        splits list into subarrays with n_split members
        @param n_split: number of members produced by split
        @type n_split: int
        @return : new array split up by n_split
        @rtype : list<str>
        '''
        sub_out = []
        out = []
        n = 0
        pyp = Pyp()
        inputs = self.pyp.flatten_list(self)
        
        while inputs:
            input = inputs.pop(0)
            n = n + 1
            sub_out.append(input)
            if not n % n_split or not inputs:
                out.append([sub_out])
                sub_out = []
        
        return out
        
    def delimit(self, delimiter):
        '''
        splits up array based on delimited instead of newlines
        @param delimiter: delimiter used for split
        @type delimiter: str
        @return: new string split by delimiter and joined by ' '
        @rtype: list<str>
        '''
        return ' '.join(self.pyp.flatten_list(self)).split(delimiter)

    def oneline(self,delimiter = ' '):
        '''
        combines list to one line with optional delimeter
        @param delimiter: delimiter used for joining to one line
        @type delimiter: str
        @return: one line output joined by delimiter
        @rtype: list<str>
        '''

        flat_list =  self.flatten_list(self)
        return delimiter.join(flat_list)

    def uniq(self):
        '''
        returns only unique elements from list
        @return: unique items
        @rtype: list<str> 
        '''
        strings= self.pyp.flatten_list(self)
        
        return list(set(strings))

    def flatten_list(self, iterables):
        '''
        returns a list of strings from nested lists
        @param iterables: nested lists containing strs or PypStrs
        @type iterables: list
        @return: unnested list of strings
        @rtype: list<str>
        '''
        return self.pyp.flatten_list(iterables)

    def unlist(self):
        '''
        splits a list into one element per line
        @param self: nested list
        @type self: list<str>
        @return: unnested list
        @rtype: list<str>
        '''
        return self.pyp.flatten_list(self)

    def after(self, target, after_n=1):
        '''
        consolidates after_n lines after matching target text to 1 line
        @param target: target string to find
        @type target: str
        @param after_n: number of lines to consolidate
        @type after_n: int
        @return: list of after_n members
        @rtype: list<str>
        '''
        out = []
        n = 0
        inputs = self.pyp.flatten_list(self)

        for input in inputs:
            n = n + 1
            if target in input:
                out.append([ [input] + inputs[n:n + after_n] ])
        return out

    def before(self, target, before_n=1):
        '''
        consolidates before_n lines before matching target text to 1 line
        @param target: target string to find
        @type target: str
        @param before_n: number of lines to consolidate
        @type before_n: int
        @return: list of before_n members
        @rtype: list<str>
        '''
        out = []
        n = 0
        inputs = self.pyp.flatten_list(self)

        for input in inputs:
            n = n + 1
            if target in input:
                out.append([ [input] + inputs[n - before_n - 1:n - 1] ])

        return out

    def matrix(self, target, matrix_n=1):
        '''
        consolidates matrix_n lines surrounding matching target text to 1 line
        @param target: target string to find
        @type target: str
        @param matrix_n: number of lines to consolidate
        @type matrix_n: int
        @return: list of matrix_n members
        @rtype: list<str>
        '''
        out = []
        n = 0
        inputs = self.pyp.flatten_list(self)

        for input in inputs:
            n = n + 1
            if target in input:
                out.append([ inputs[n - matrix_n - 1:n - 1] + [input] + inputs[n:n + matrix_n]  ])

        return out
    
    
class PypStr(str,PypStrCustom):
    '''
    defines p string object, allows manipulation of input line by line using python
    string methods
   
    '''
    def __init__(self, *args):
        super(PypStr, self).__init__()       
        try:
            PypStrCustom.__init__(self)  
        except AttributeError:
            pass
        
    def dir(self):
        pdir = None

        try:
            pdir = PypStr(os.path.split(self.rstrip('/'))[0])
        except:
            pass

        return pdir

         
    def file(self):
        pfile = None

        try:
            pfile = os.path.split(self)[1]
        except:
            pass

        return pfile

    def ext(self):
        pext = None

        try:
            pext = self.split('.')[-1]
        except:
            pass

        return pext
    
    def trim(self,delim='/'):
        '''
        returns everything but the last directory/file
        @param self: directory path
        @type self: str
        @return: directory path missing without last directory/file
        @rtype: PypStr
        '''
        return PypStr(delim.join(self.split(delim)[0:-1]))


    def kill(self, *args):
        '''
        replaces to_kill with '' in string
        @param args: strings to remove 
        @type args : strs
        @return: string without to_kill
        @rtype: PypStr
        '''
        for arg in args:
            self = self.replace(arg, '')
        
        return PypStr(self)
    
    def letters(self):
        '''
        returns only letters
        @return: list of strings with only letters
        @rtype: PypList
        '''
           
        new_string=''
        for letter in list(self):
            if letter.isalpha():
                new_string = new_string + letter
            else:
                new_string = new_string + ' '
        return [PypStr(x) for x in new_string.split() if x]
    
    def punctuation(self):
        '''
        returns only punctuation
        @return: list of strings with only punctuation
        @rtype: PypList
        '''
           
        new_string=''
        for letter in list(self):
            if letter in """!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~""":
                new_string = new_string + letter
            else:
                new_string = new_string + ' '
        return [PypStr(x) for x in new_string.split() if x]
    
    def digits(self):
        '''
        returns only digits
        @return: list of string with only digits
        @rtype: PypList
        '''
        new_string=''
        for letter in list(self):
            if letter.isdigit():
                new_string = new_string + letter
            else:
                new_string = new_string + ' '
        return [PypStr(x) for x in new_string.split() if x]
        
    
    
    def clean(self,delim = '_'):
        '''   
        returns a metacharater sanitized version of input. ignores underscores and slashes and dots.
        @return: string with delim (default '_') replacing bad metacharacters
        @rtype: PypStr
        @param delim: delimeter to rejoin cleaned string with. default is "_"
        @type delime: str 
        '''
        
        for char in self:
            if not char.isalnum() and char not in ['/','.',delim]:
                self = self.replace(char, ' ')
        return PypStr(delim.join([x for x in self.split() if x.strip()]))
    
    def re(self,to_match):
        '''   
        returns characters that match a regex using to_match
        @return: portion of string that matches regex
        @rtype: PypStr
        @param to_match: regex used for matching
        @type to_match: str 
        '''
        
        match = re.search(to_match,self)
        if match:
            return PypStr(match.group(0))
        else:
            return ''
    
    
class PypList(list,PypListCustom):
    '''
    defines p list object, allows manipulation of input line by line using python
    list methods
    '''
    
    def __init__(self, *args):
        super(PypList, self).__init__(*args)
        try:
            PypListCustom.__init__(self)
        except AttributeError:
            pass
class Pyp(object):
    '''
    pyp engine. manipulates input stream using python methods
    @ivar history: master record of all manipulations
    @type history: dict<int:dict>
    @ivar pwd: current directory
    @type pwd: str
    @ivar p: current input line being manipulated
    @type p: str or list 
    @ivar n: current input line number
    @type n: int
    '''
    
    def __init__(self, opts=None):
        # For unit tests
        if opts is not None:
            global options
            options = opts

        self.history = {} #dictionary of all data organized input line by input line
        try: #occasionally, python loses pwd info
            self.pwd = os.getcwd()
        except:
            self.pwd =''
    
    def get_custom_execute(self):
        '''returns customized paths to macro files if they are setup'''
        custom_ob = PypCustom()
        custom_attrs = dir(custom_ob)
        
        if 'custom_execute' in custom_attrs and custom_ob.custom_execute:
           final_execute = custom_ob.custom_execute
        else:
           final_execute = self.default_final_execute
           
        return final_execute
    
    def default_final_execute(self,cmds):
        for cmd in cmds:
            os.system(cmd)
    
    
    def get_custom_macro_paths(self):
        '''returns customized paths to macro files if they are setup'''
        home =  os.path.expanduser('~')
        custom_ob = PypCustom()
        custom_attrs = dir(custom_ob)
        
        if 'user_macro_path' in custom_attrs:
            user_macro_path = custom_ob.user_macro_path
        else:
            user_macro_path = home + '/pyp_user_macros.json'

        
        if 'group_macro_path' in custom_attrs:
            group_macro_path = custom_ob.group_macro_path
        else:
            group_macro_path = home + '/pyp_group_macros.json'
            
        return user_macro_path,group_macro_path

    def cmds_split(self, cmds, macros):
        '''
        splits total commmand array based on pipes taking into account quotes,
        parantheses and escapes. returns array of commands that will be processed procedurally.
        Substitutes macros without executable commands.
        
        @param cmds: user supplied command set
        @type cmds: list<str>
        @param macros: user defined marcros
        @type macros: dict<str:dict>
        @return: list of commands to be evaluated
        @rtype: list<str>
        '''
       
        cmd_array = []
        cmd = ''
        open_single = False
        open_double = False
        open_parenth = 0
        escape = False
        letters = list(cmds)
        while letters:
            letter = letters.pop(0)
            if cmd and cmd[-1] == '\\': escape = True
            
            #COUNTS QUOTES
            if letter == "'":
                if open_single and not escape:
                    open_single = not open_single
                else:
                    open_single = True
            if letter == '"':
                if open_double and not escape:
                    open_double = not open_double
                else:
                    open_double = True
            
            #COUNTS REAL PARANTHESES
            if not open_single and not open_double:
                if letter == '(' :
                    open_parenth = open_parenth + 1
                if letter == ')':
                    open_parenth = open_parenth - 1

            #MONEY MOVE--substitutes command for macro or starts building new command after adding command to cmd_array
            if cmd.strip() in macros and letter in ['|', '[', '%', ',', '+', ' ']:
                cmd = cmd.strip()
                letters = list('|'.join(macros[cmd]['command']) + letter + ''.join(letters))
                cmd = ''
            elif letter == '|' and not open_single and not open_double and not open_parenth:#
                cmd_array.append(cmd)
                cmd = ''
            else:
                cmd = cmd + letter
            escape = False

            #for last command, either recursively run cmd_split or add last command to array
        if cmd.strip() in macros and not options.macro_save_name: #allows macro be split and also to be correctly overwritten
            return self.cmds_split('|'.join(cmd_array + macros[cmd]['command']), macros) #this is by definition the last cmd. 
        else:
            cmd_array.append(cmd) #gets last cmd

        
        return [x for x in cmd_array if x]

    def load_macros(self,macro_path):
        '''
        loads macro file; returns macros dict
        @param macro_path: file path to macro file
        @type macro_path: str
        @return: dictionary of user defined macros
        @rtype: dict<str:dict>
        '''
        #macro_path = self.macro_path
        if os.path.exists(macro_path):
            macro_ob = open(macro_path)
            macros = json.load(macro_ob)
            macro_ob.close()
        else:
           macros = {}
        return macros

    def write_macros(self, macros,macro_path, cmds):
        '''
        writes macro file
        @param macros: dictionary of user defined macros
        @type macros: dict<str:dict>
        @param macro_path: file path to macro file
        @type macro_path: str
        @param cmds: commands to be saved as a macro
        @type cmds: list<str>
        '''
        
        if options.macro_save_name:
            macro = options.macro_save_name
            macro_name = macro.split('#')[0].strip()
            macros[macro_name] = {}
            macros[macro_name]['command'] = cmds
            macros[macro_name]['user'] = getpass.getuser() 
            macros[macro_name]['date'] =str(datetime.datetime.now()).split('.')[0]

            if '#' in macro: #deals with comments
                macros[macro_name]['comments'] = '#' + macro.split('#')[1].strip()
            else:
                macros[macro_name]['comments'] = ''
            macro_ob = open(macro_path, 'w')
            json.dump(macros, macro_ob)
            macro_ob.close()
            self.load_macros(macro_path)
            if macro_name in macros:
                print Colors.YELLOW + macro_name , "successfully saved!" + Colors.OFF
                sys.exit()
            else:
                print Colors.RED + macro_name, 'was not saved...unknown error!' + Colors.OFF
                sys.exit(1)

    def delete_macros(self, macros,macro_path):
        '''
        deletes macro from file
        @param macros: dictionary of user defined macros
        @type macros: dict<str:dict>
        @param macro_path: file path to macro file
        @type macro_path: str
        '''
        if options.macro_delete_name:
            if options.macro_delete_name in macros:
                del macros[options.macro_delete_name]
                json_ob = open(macro_path, 'w')
                json.dump(macros, json_ob)
                json_ob.close()
                print Colors.MAGENTA + options.macro_delete_name + " macro has been successfully obliterated" + Colors.OFF
                sys.exit()
            else:
                print Colors.RED + options.macro_delete_name + " does not exist" + Colors.OFF
                sys.exit(1)

    def list_macros(self, macros):
        '''
        prints out formated macros, takes dictionary macros as input
        @param macros: dictionary of user defined macros
        @type macros: dict<str:dict>
        '''
        if options.macro_list or options.macro_find_name:
            macros_sorted = [x for x in macros]
            macros_sorted.sort()
            for macro_name in macros_sorted:
                if options.macro_list or options.macro_find_name in macro_name or options.macro_find_name in macros[macro_name]['user']:
                    print Colors.MAGENTA + macro_name + '\n\t ' + Colors.YELLOW+macros[macro_name]['user'] \
                     + '\t' + macros[macro_name]['date']\
                    +'\n\t\t' + Colors.OFF + '"'\
                     + '|'.join(macros[macro_name]['command']) + '"' + Colors.GREEN + '\n\t\t'\
                      + macros[macro_name].get('comments', '') + Colors.OFF + '\n'
            sys.exit()

    def load_file(self):
        '''
        loads file for pyp processing
        @return: file data
        @rtype: list<str>
        '''
        if options.text_file:
            if not os.path.exists(options.text_file):
                print Colors.RED + options.text_file + " does not exist" + Colors.OFF
                sys.exit()
            else:
                f = [x.rstrip() for x in open(options.text_file) ]
                return f
        else:
            return []


    def shell(self, command):
        '''
        executes a shell commands, returns output in array sh
        @param command: shell command to be evaluated
        @type command: str
        @return: output of shell command
        @rtype: list<str>
        '''
        sh = [x.strip() for x in os.popen(command).readlines()]
        return sh

    def shelld(self, command, *args):
        '''
        executes a shell commands, returns output in dictionary based on args
        @param command: shell command to be evaluated
        @type command: str
        @param args: optional delimiter. default is ":".
        @type args: list 
        @return: hashed output of shell command based on delimiter
        @rtype: dict<str:str>
        
        '''
        if not args:
            ofs = ':'
        else:
            ofs = args[0]
        shd = {}
        for line in [x.strip() for x in os.popen(command).readlines()]:
            try:
                key = line.split(ofs)[0]
                value = ofs.join(line.split(ofs)[1:])
                shd[key] = value
            except IndexError:
                pass

        return shd

    
    def rekeep(self,to_match):
        '''
        keeps lines based on regex string matches
        @param to_match: regex
        @type to_match: str
        @return: True if any of the strings match regex else False
        @rtype: bool
        '''
        
        match = []
        flat_p = self.flatten_list(self.p)
        for item in flat_p:
            if re.search(to_match,item):
                match.append(item)
        if match:
            return True
        else:
            return False
    
    def relose(self,to_match):
        '''
        loses lines based on regex string matches
        @param to_match: regex
        @type to_match: str
        @return: False if any of the strings match regex else True
        @rtype: bool
        '''
        
        return not self.rekeep(to_match)
    
    
    def keep(self,*args):
        '''
        keeps lines based on string matches
        @param args: strings to search for 
        @type args: list<str>
        @return: True if any of the strings are found else False
        @rtype: bool
        '''
        
        kept = []
        for arg in args:
            flat_p = self.flatten_list(self.p)
            for item in  flat_p:
                if arg in item:
                    kept.append(arg)
                
        if kept:
            return True
        else:
            return False
    
    def lose(self,*args):
        '''
        removes lines based on string matches
        @param args: strings to search for 
        @type args: list<str> 
        @return: True if any of the strings are not found else False
        @rtype: bool
        '''
        return not self.keep(*args)

    def array_tracer(self, input,power_pipe=''):
        '''
        generates colored, numbered output for lists and dictionaries and other types
        @param input: one line of input from evaluted pyp command
        @type input: any
        @param power_pipe: Output from powerpipe (pp) evaluation
        @type power_pipe: bool
        @return: colored output based on input contents
        @rtype: str
        '''
        if not input and input is not 0: #TRANSLATE FALSES TO EMPTY STRINGS OR ARRAYS. SUPPLIES DUMMY INPUT TO KEEP LINES IF NEEDED.
            if options.keep_false or power_pipe:
                input = ' '
            else:
                return ''
       
       #BASIC VARIABLES
        nf = 0
        output = ''
        
        if power_pipe:
            n_index = Colors.MAGENTA + '[%s]' % (self.n) + Colors.GREEN
            final_color = Colors.OFF
        else:
            n_index = ''
            final_color=''
        
        #DEALS WITH DIFFERENT TYPES OF INPUTS
        if type(input) in [ list, PypList, PowerPipeList] :#deals with lists

            for field in input:
                if not nf == len(input):
                    if type(field)  in [str, PypStr]:
                        COLOR = Colors.GREEN
                    else:
                        COLOR = Colors.MAGENTA

                    output = str(output) + Colors.BOLD + Colors.BLUE + "[%s]" % nf + Colors.OFF + COLOR + str(field) + Colors.GREEN
                nf = nf + 1
            return  n_index + Colors.GREEN + Colors.BOLD + '[' + Colors.OFF + output + Colors.GREEN + Colors.BOLD + ']' + Colors.OFF 

        elif type(input) in [str, PypStr] :
            return n_index + str(input) + final_color

        elif type(input) in [int, float] :
            return n_index + Colors.YELLOW + str(input) +  Colors.OFF 
 
        elif type(input) is dict: #deals with dictionaries
            for field in sorted(input,key=lambda x : x.lower()):
                output = output + Colors.OFF + Colors.BOLD + Colors.BLUE  + field  + Colors.GREEN + ": " + Colors.OFF + Colors.GREEN + str(input[field]) + Colors.BOLD + Colors.GREEN + ',\n '
            return n_index + Colors.GREEN + Colors.BOLD + '{' + output.strip().strip(' ,') + Colors.GREEN + Colors.BOLD + '}' + Colors.OFF

        else: #catches every else
            return  n_index + Colors.MAGENTA + str(input) + Colors.OFF

    def cmd_split(self, cmds):
        '''
        takes a command (as previously split up by pipes and input as array cmds), 
        and returns individual terms (cmd_array) that will be evaluated individually.
        Also returns a string_format string that will be used to stitch together
        the output with the proper spacing based on the presence of "+" and ","
        @param cmds: individual commands separated by pipes
        @type cmds: list<str>
        @return: individual commands with corresponding string format
        @rtype: list<str>
        '''
       
        string_format = '%s'
        cmd_array = []
        cmd = ''
        open_quote = False
        open_parenth = 0
        open_bracket = 0

        for letter in cmds:
            
            if letter in [ "'" , '"']:
                if cmd and cmd[-1] == '\\':
                    open_quote = True
                else:
                    open_quote = not open_quote

            if not open_quote: #this all ignores text in () or [] from being split by by , or + 
                if letter == '(' :
                    open_parenth = open_parenth + 1
                elif letter == ')':
                    open_parenth = open_parenth - 1    
                elif letter == '[' :
                    open_bracket = open_bracket + 1
                elif letter == ']':
                    open_bracket = open_bracket - 1
                
                if not open_parenth and not open_bracket and letter in [',', '+']: #these are actual formatting characters
                    cmd_array.append(cmd)
                    cmd = ''
                    string_format = string_format + letter.replace('+', '%s').replace(',', ' %s')
                    continue

            cmd = cmd + letter


        cmd_array.append(cmd)
        output = [(cmd_array, string_format)]
        return output

    def all_meta_split(self, input_str):
        '''
        splits a string on any metacharacter
        @param input_str: input string
        @type input_str: str
        @return: list with no metacharacters
        @rtype: list<str>
        '''

        for char in input_str:
            if not char.isalnum():
                input_str = input_str.replace(char, ' ')
        return [x for x in input_str.split() if x.strip()]

    def string_splitter(self):
        '''
        splits self.p based on common metacharacters. returns a
        dictionary of this information.
        @return: input split up by common metacharacters
        @rtype: dict<str:list<str>>
        '''
        
        whitespace =self.p.split(None)
        slash =self.p.split('/')
        underscore =self.p.split('_')
        colon =self.p.split(':')
        dot =self.p.split('.')
        minus =self.p.split('-')
        all= self.all_meta_split(self.p)
        comma = self.p.split(',')
        
        split_variables_raw = {
        
            'whitespace' :whitespace,
            'slash' :slash,
            'underscore' :underscore,
            'colon' :colon,
            'dot' :dot,
            'minus' :minus,
            'all' : all,
            'comma' : comma,
            
            'w' :whitespace,
            's' :slash,
            'u' :underscore,
            'c' :colon,
            'd' :dot,
            'm' :minus,
            'a' : all,
            'mm' : comma,
                              }
        #gets rid of empty fields
        split_variables = dict((x, PypList([PypStr(y) for y in split_variables_raw[x]])) for x in  split_variables_raw)
        return split_variables

    def join_and_format(self, join_type):
        '''
        joins self.p arrays with a specified metacharacter  
        @param join_type: metacharacter to join array 
        @type join_type: str
        @return: string joined by metacharacter
        @rtype: str
        '''
       
        temp_joins = []
        
        if options.small:
            derived_string_format = self.history[self.n]['string_format'][-1]
        #TODO:
        else:
            derived_string_format = self.string_format[-1]

        len_derived_str_format = len(derived_string_format.strip('%').split('%'))
        if len(self.p) == len_derived_str_format:
            string_format = derived_string_format #normal output
            for sub_p in self.p:
                if type(sub_p) in [list, PypList]:
                    temp_joins.append(join_type.join(sub_p))
                else: #deals with printing lists and strings
                    temp_joins.append(sub_p)

            return PypStr(string_format % tuple(temp_joins))

        else: #deals with piping pure arrays to p
            return PypStr(join_type.join(PypStr(x)for x in self.p))

    def array_joiner(self):
        '''
        generates a dict of self.p arrays joined with various common metacharacters
        @return: input joined by common metacharacters
        @rtype: dict<str:str>
        '''
        whitespace = self.join_and_format(' ')
        slash = self.join_and_format(os.sep)
        underscore = self.join_and_format('_')
        colon = self.join_and_format(':')
        dot = self.join_and_format('.')
        minus = self.join_and_format('-')
        all = self.join_and_format(' ')
        comma = self.join_and_format(',')
            
        join_variables = {
            'w' : whitespace,
            's' : slash,
            'u' : underscore,
            'c' : colon,
            'd' : dot,
            'm' : minus,
            'a' : all,
            'mm' : comma,
            
            'whitespace' : whitespace,
            'slash' : slash,
            'underscore' : underscore,
            'colon' : colon,
            'dot' : dot,
            'minus' : minus,
            'all' : all,
            'comma' : comma  
                            }

        return join_variables

    def translate_preset_variables(self, translate_preset_variables,file_input, second_stream_input):
        '''
        translates variables to protected namespace dictionary for feeding into eval command.
        @param file_input: data from file
        @type file_input: list 
        @param second_stream_input: input from second stream 
        @type second_stream_input: list<str>
        @return: values of preset variable for direct use by users
        @rtype: dict<str:str>
       '''
        
        
        #generic variables
        presets = {
                     'n' : self.kept_n,
                     'on' : self.n,
                     'fpp' : file_input,
                     'spp' : second_stream_input,
                     'nk': 1000 + self.kept_n,
                     'shell': self.shell,
                     'shelld' : self.shelld,
                     'keep': self.keep,
                     'lose': self.lose,
                     'k': self.keep,
                     'l':self.lose,
                     'rekeep':self.rekeep,
                     'relose':self.relose,
                     'rek':self.rekeep,
                     'rel':self.relose,
                     'quote': '"',
                     'apost':"'",
                     'qu':'"',
                     'dollar': '$',
                     'pwd': self.pwd,
                     'date': datetime.datetime.now(),
                     'env': os.environ.get,
                     'glob' : glob.glob,
                     'letters': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
                     'digits': '0123456789',
                     'punctuation': """!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~""",
                     'str':(PypStr),
                             }     
  
        if options.small:
            #removes nested entries from history
            history = []
            for hist in self.history[self.n]['history']:
                if type(hist) in (list,PypList):
                    hist = self.unlist_p(hist)
                history.append(hist)
            presets['history'] = presets['h'] = history
        
        # file
        if options.text_file:
            try:
                fp = file_input[self.n]
            except IndexError:
                fp = ''
            presets['fp'] = fp

        # second stream
        try:
            sp = second_stream_input[self.n]
        except IndexError:
            sp = ''
        except Exception:
            sp = ''
 
        presets['sp'] = sp

        if options.small:
            #original input
            if self.history[self.n]['output']:
                presets['o'] = self.history[self.n]['history'][0]
            
            else:
                presets['o'] = ''
            presets['original'] = presets['o']
         
        # p cleanup   
        p = self.p
        if type(p) in [str]:
            presets['p'] = PypStr(p)
        elif  type(p) in [list]:
            presets['p'] = PypList(p)
        else:
            presets['p'] = p
     
        #custom functions
        presets.update(PypFunctionCustom.__dict__) #adds user defined functions
        return presets

    def initialize_n(self):
        '''
        initializes history dict for a particular n,
        where n is the line of the input being processed
        '''
        self.history[self.n] = {} #creates dict
        self.history[self.n]['error'] = '' # error data
        self.history[self.n]['history'] = [] #  
        self.history[self.n]['history'].append(self.p) # records current p
        self.history[self.n]['string_format'] = [] #used for formating output
        self.history[self.n]['original_splits'] = {}#dict of original splits
        self.history[self.n]['output'] = True

    def safe_eval(self, cmd, variables):
        '''
        evaluates a str command (cmd) safely. takes a dictionary of protected 
        namespace variables as input.returns output of python call, which can
        be any type of python data type (typically str or array though).
        @param cmd: command to be evaluated using python
        @type cmd: str
        @param variables: preset variables used for evaluation
        @type variables: dictionary
        @return: output from python evaluation
        @rtype: list<str>
        '''
 
        if (not options.small) or (not self.history[self.n]['error'] and self.history[self.n]['output']): #if no errors, go forward 
            total_output = []
            for cm_tuple in self.cmd_split(cmd):#cm_tuple consists of commands and string format.cmd_split splits each command into terms.
                string_format = cm_tuple[1] #how the results will eventually be formatted.
                for cm in cm_tuple[0]:#cm is the expression seperated by a + or a ,                        
                    #evaluate cm and add to dictionary catching any error.
                    try:
                        output = eval(cm, variables) #500 lines of code wrap this line!!!
                    except KeyboardInterrupt:
                        print Colors.RED + "killed by user" + Colors.OFF
                        sys.exit()
                    except Exception, err:
                        if options.small:
                            self.history[self.n]['error'] = Colors.RED + 'error: ' + str(err) + Colors.OFF, Colors.RED + cmd + Colors.OFF
                        break
                    #totals output for each cm
                    try:
                        if output is True : #allows truth tests
                            output = self.p
                    except:
                        pass                    
                    
                    total_output.append(output)

                    #updates self.history dictionary
                if options.small: 
                    self.history[self.n]['string_format'].append(string_format)
                else:
                    self.string_format.append(string_format)
                #generates printable output                 
            return total_output

    
    def get_user_input(self, total_output,second_stream_input,file_input, power_pipe):
        '''
        figures out what to show user in terms of powerpipe output. does NOT update history dictionary.
        
        @param total_output: line output from eval
        @type total_output: list<string>
        @param second_stream_input: entire input from second string
        @type second_stream_input: list<string>
        @param file_input: entire input from file
        @type file_input: list<string>
        @param power_pipe: kind of power pipe
        @type power_pipe: string
        @return: output for display
        @rtype: list<str>
        '''
    
        try: #who knows what could happen with user input
            n = self.n
            if  power_pipe ==    'pp' and total_output or not power_pipe: #standard input
                user_output =  total_output
            elif power_pipe ==   'spp'  and second_stream_input:
                user_output =  [second_stream_input[n]]
            elif power_pipe ==   'fpp' and file_input:
                user_output =  [file_input[n]]
            elif power_pipe: #  power pipe variable is referenced, but does not exist.
                print Colors.RED + "YOUR LIST VARIABLE DOES NOT EXIST: " + Colors.GREEN + power_pipe + Colors.OFF
                sys.exit()
        except: #default output is null per line
            user_output =[' ']   
    
        return user_output

    def get_history(self, total_output):
        '''
        updates history dictionary with output from python evaluation
        @param total_output: line output from eval
        @type total_output: list<string>
        @param second_stream_input: entire input from second string
        @type second_stream_input: list<string>
        @param file_input: entire input from file
        @type file_input: list<string>
        '''
        hist = []

        #marks null output, as '' except when output  is zero, poerpope, or we are printing out null lines
        if (not total_output or not [x for x in total_output if x]) and total_output != [0]: #kill irrelevant output
            
            hist.append(False)
            output = False
        else: # good output
            output_array = []
            history_array = []
            contains_list = False
            #actual output is p or pp unless spp is invoked.
            #TODO: 
            #user_input = self.get_user_input(total_output, second_stream_input, file_input, power_pipe)
            #self.kept_n = self.kept_n + 1 #only update if output is kept

            user_input = total_output

            #update history array
            for out in total_output: # forms an array called_output array of strings or array_traced strings
                history_array.append(out) # for feeding back to pipe
                contains_list = True if type(out) not in [str, PypStr] else False
            
            #update actual output
            for out in user_input:
                output_array.append(self.array_tracer(out)) # for output

            
            output = self.string_format % (tuple(output_array))
            ''' 
            if contains_list: #this section prevents buildup of recursive lists.
                hist.append(total_output) # just adds list to total output if list
            else:
                hist.append(self.string_format % (tuple(history_array))) # adds properly formatted string if string.
            '''
            return output


    def update_history(self, total_output,second_stream_input,file_input, power_pipe):
        '''
        updates history dictionary with output from python evaluation
        @param total_output: line output from eval
        @type total_output: list<string>
        @param second_stream_input: entire input from second string
        @type second_stream_input: list<string>
        @param file_input: entire input from file
        @type file_input: list<string>
        @param power_pipe: kind of power pipe
        @type power_pipe: string
        '''
        
        #marks null output, as '' except when output  is zero, poerpope, or we are printing out null lines
        if (not total_output or not [x for x in total_output if x]or  self.history[self.n]['error'])\
            and total_output != [0]\
            and not power_pipe: #kill irrelevant output
            
            self.history[self.n]['history'].append(False)
            self.history[self.n]['output']=False
        else: # good output
            string_format = self.history[self.n]['string_format'][-1]
            output_array = []
            history_array = []
            contains_list = False
            #actual output is p or pp unless spp is invoked.
            user_input = self.get_user_input(total_output, second_stream_input, file_input, power_pipe)
            self.kept_n = self.kept_n + 1 #only update if output is kept

            #update history array
            for out in total_output: # forms an array called_output array of strings or array_traced strings
                history_array.append(out) # for feeding back to pipe
                contains_list = True if type(out) not in [str, PypStr] else False
            
            #update actual output
            for out in user_input:
                output_array.append(self.array_tracer(out, power_pipe)) # for output
            
            self.history[self.n]['output'] = string_format % (tuple(output_array))
            
            if contains_list: #this section prevents buildup of recursive lists.
                self.history[self.n]['history'].append(total_output) # just adds list to total output if list
            else:
                self.history[self.n]['history'].append(string_format % (tuple(history_array))) # adds properly formatted string if string.
    
    def flatten_list(self, iterables):
        '''
        returns a list of strings from nested lists
        @param iterables: nested list to flatten
        @type iterables: list<str>
        '''
        out = []
        try:
            if [x for x in iterables if type(x) in [str, PypStr]]:
                out = out + iterables
            else:
                for x in iterables:
                    out = out + self.flatten_list(x)
        except:              #catches non iterables
            out = [iterables]
    
        return out
    
    def power_pipe_eval(self, cmd, inputs, second_stream_input, file_input, power_pipe_type):
        '''
        evaluates pp statement. returns sanitized result.
        @param cmd: power pipe command
        @type cmd: str
        @param inputs: inputs from std-in or previous python eval
        @type inputs: list<str>
        @param power_pipe_type: kind of powerpipe 
        @type power_pipe_type: str
        @return: 'p' and output of python evaluation
        @rtype: list<str>
        '''
        variables = {}
        self.history = {}
        padded_output = []
        
        
        variables['str'] = PypStr #useful for list comps
        variables['n'] = self.kept_n
        variables['on'] = self.n
        
        inputs = self.flatten_list(inputs)
        
        inputs = [x for x in inputs if self.unlist_p(x) is not False] #keeps unfiltered output
        
        variables['pp'] = PowerPipeList(inputs)
        variables['spp'] = PowerPipeList(second_stream_input)
        variables['fpp'] = PowerPipeList(file_input)
        
        
        try:
            output = eval(cmd, variables) #1000 lines of code wrap this line!!!
        except KeyboardInterrupt:
            print Colors.RED + "killed by user" + Colors.OFF
            sys.exit()
        except Exception, err:
            print Colors.RED + 'error: ' + str(err) + Colors.OFF, Colors.RED + cmd + Colors.OFF
            sys.exit()

        if output is None: #allows use of inplace methods like sort
            output = variables[power_pipe_type]
        
        if type(output)  in [int, float]: #keeps output in array
            output = [output]

        if type(output) in [str, PypStr, tuple]: #makes sure output is in list of lists
            output = [[output]]

        if [x for x in output if type(x) in [tuple]]:#changes tuples to lists 
            output = [PypList(x) for x in output if type(x) in [tuple]]
        
        if len(output) == 1:      #turn off powerpipe if output is single item
            power_pipe_type = ''                
        
        return output,  power_pipe_type

    def detect_power_pipe(self, command, power_pipe_type):
        '''
        detects presense of powerpipe
        @param command: command to be evaluated
        @type command: str
        @param power_pipe_type: kind of powerpipe (future use)
        @type power_pipe_type: str
        @return: True if powerpipe else False
        @rtype: bool
        '''
        open_quote = False
        cmd_raw = list(command)
        cmd = []

        for letter in cmd_raw:
            if letter not in  ['"', "'"] and not letter.isalnum():
                letter = ' '
            cmd.append(letter)

         
        cmds = ''.join(cmd).split()
        for cmd in cmds:
            cmd = list(cmd)
            test_cmd = ''
            while cmd:
                letter = cmd.pop(0)
                test_cmd = test_cmd + letter
                if not open_quote:
                    if  power_pipe_type == test_cmd and not cmd:
                        return True
                    
                if letter in [ "'" , '"']:
                    if cmd and cmd[0] == '\\':
                        open_quote = True
                    else:
                        open_quote = not open_quote
        return False

    def format_input(self, cmd, input_set, second_stream_input, file_input):
        '''
        checks for powerpipe presence, evaluates powerpipe pp and returns 
        formatted output if detected
        @param cmd: user command
        @type cmd: str
        @param input_set: input from std-in or previous python evaluation
        @type input_set: list<str>
        @return: command, input set, presence of powerpipe
        @rtype: list<str>
        '''
        #POWER PIPES 
        power_pipe = '' #power pipe is off by default
        if self.detect_power_pipe(cmd, 'pp') :
            input_set,power_pipe = self.power_pipe_eval( cmd, input_set, second_stream_input, file_input,'pp')
            cmd = 'p'
        elif self.detect_power_pipe(cmd, 'spp') :
            second_stream_input, power_pipe = self.power_pipe_eval( cmd, input_set, second_stream_input, file_input,'spp')
            cmd = 'p'
        elif  self.detect_power_pipe(cmd, 'fpp'):
            file_input, power_pipe = self.power_pipe_eval( cmd, input_set, second_stream_input, file_input,'fpp')
            cmd = 'p'
       
        return cmd, input_set,second_stream_input, file_input, power_pipe

    def unlist_p(self, p):
        '''
        changes one item arrays to strings for input cleanup
        @param p: input from std-in or previous pyp evaluation
        @type p: list
        @return: will return a string if input is a list and has one member
        @rtype: list<str>,str
        '''
        if  type(p)  in [list, PypList] and len(p) == 1:
            p = p[0]
        
        return p
    
     
    def process(self, inputs, file_input, cmds, second_stream_input):
        '''
        takes primary data from input stream (can be string, array or dictionary), applies user commands to it, 
        captures this output. Also, generates several variables such as line counter and 
        various string split and join variables. Outputs string, array, or dictionary in 
        a format deliniated by the string formating stamp
        @param inputs: inputs from std-in or previous pyp eval
        @type inputs: str,list
        @param file_input: inputs from file
        @type file_input: list
        @param cmds: python commands to be evaluated
        @type cmds: list<str>
        @param second_stream_input: second stream input
        @type second_stream_input: list<str>
        '''
    
        while cmds: #cmds are commands that will be executed on the input stream       
            self.n = -1 # overall line counter. will change to 0 asap.
            self.kept_n = 0 # counter of kept lines. needs to be avail for eval, so starts as 0
            cmd = cmds.pop(0)

            cmd, input_set,second_stream_input, file_input, power_pipe = self.format_input(cmd, inputs,second_stream_input, file_input)

            original_input_set = input_set[:]

            #MAIN LOOP 
            while input_set:
                self.p = self.unlist_p(input_set.pop(0)) # p is main line variable being manipulated                            

                self.n = self.n + 1  # raises counters
                variables = {}

                               
                if not self.n in self.history: # initializes self.history dict for line
                    self.initialize_n()
                else:
                    if self.p is False: #skip false output but n is updated
                        continue
                 
                if type(self.p) in [ str, PypStr]:                          # p is string    
                    variables = self.string_splitter()
                    if not self.history[self.n]['original_splits']: #makes variables dealing with original input
                       self.history[self.n]['original_splits'] = dict(('o' + x, variables[x]) for x in variables)
                    if not self.history[self.n]['output']: #kills o variables if there is no output
                        self.history[self.n]['original_splits'] = dict(('o' + x, '') for x in variables)

                elif type(self.p) in [list, PypList] and not power_pipe:                 # p is list of lists, constructs various joins 
                    try:                                                   #for going from list to powerpipe
                        variables = self.array_joiner()
                    except:
                        pass
                        
                variables.update(self.translate_preset_variables(original_input_set,file_input, second_stream_input)) #add incrementals
                variables.update(self.history[self.n]['original_splits']) # updates with original splits

                total_output = self.safe_eval(cmd, variables)
                self.update_history(total_output,second_stream_input,file_input ,power_pipe)
 
            #takes output, feeds back into input
        
            new_input = [self.history[x]['history'][-1] for x in self.history ] # takes last output as new input
            self.process(new_input, file_input, cmds, second_stream_input) #process new input

    
    def processLarge(self, inputs, file_input, cmds, second_stream_input):
        '''
        @param inputs: inputs from std-in or previous pyp eval
        @type inputs: str,list
        @param file_input: inputs from file
        @type file_input: list
        @param cmds: python commands to be evaluated
        @type cmds: list<str>
        @param second_stream_input: second stream input
        @type second_stream_input: list<str>
        '''
       
        #MAIN LOOP 
        for i in inputs:
            self.p = self.unlist_p(i) # p is main line variable being manipulated                            
            self.n = 0
            self.kept_n = 0 # counter of kept lines. needs to be avail for eval, so starts as 0

            self.string_format = []    
            for cmd in cmds: #cmds are commands that will be executed on the input stream      

                variables = {}

                if type(self.p) in [str, PypStr]:                          # p is string    
                    variables = self.string_splitter()
                elif type(self.p) in [list, PypList]:                 # p is list of lists, constructs various joins 
                    try:                                                   #for going from list to powerpipe
                        variables = self.array_joiner()
                    except:
                        pass
                        
                
                variables.update(self.translate_preset_variables(None, None, None)) #add incrementals
                #variables.update(self.history[self.n]['original_splits']) # updates with original splits

                variables['p'] = self.p

                self.p = self.unlist_p(self.safe_eval(cmd, variables))
                
                if self.p is False:
                    continue

            
            if self.p is False or self.p == '' or self.p == []:
                continue
            
            if type(self.p) in [str, PypStr]: 
                print self.p
            elif type(self.p) in [list, PypList]:
                print '\t'.join(self.flatten_list(self.p))
                #output = self.get_history(self.p)
                #print output
                '''
                output = ''
                for l in self.p:
                    if type(l) in [list, PypList]:
                        output += self.array_tracer(l)
                    else:
                        output += l
                if output != '':
                    print self.array_tracer(output)
                '''
            else:
                 print str(self.p)

    def output(self, total_cmds):
        '''
        generates final output.
        @param total_cmds: all commands executed
        @type total_cmds: list<str>
        '''
        execute_cmds = []
        for self.history_index in self.history:
            error = self.history[self.history_index]['error']
            
            if not error or "list index out of range" in error[0] or  'string index out of range' in error[0] : #no error
                
                cmd = self.history[self.history_index]['output'] #color formated output

                if cmd: #kept commands
                    if options.execute: #executes command        
                        execute_cmds.append(cmd)
                    elif options.delimited:
                        oput = self.history[self.history_index]['history'][-1]             
                        if type(oput) in [str, PypStr] and oput != '': 
                            print oput
                        elif type(oput) in [list, PypList]:
                            print options.delimiter.join(self.flatten_list(oput))
                    else:
                        print cmd # normal output
                elif options.keep_false: #prints blank lines for lost False commands 
                    print 
            else: #error
                print Colors.RED + self.history[self.history_index]['error'][0] + Colors.RED + ' : ' + self.history[self.history_index]['error'][1] + Colors.OFF
        
        if execute_cmds:
            self.final_execute(execute_cmds) 

    
    def initilize_input(self):
        '''
        decides what type of input to use (all arrays. can be from rerun file, yaml, or st-in. 
        also does some basic processing, for using different delimeters or looking for jts numbers
        @return: starting input for pyp processing
        @rtype: list
        '''
        
        if options.manual:
            print Docs.manual
            sys.exit()
            
        if options.unmodified_config:
            print Docs.unmodified_config
            sys.exit()
        
        rerun_path = '/%s/pyp_rerun_%d.txt' %(tempfile.gettempdir(),os.getppid())        

        if options.rerun: #deals with rerunning script with -r flag
            if not os.path.exists(rerun_path):
                gpid = int(os.popen("ps -p %d -oppid=" % os.getppid()).read().strip())
                rerun_gpid_path = '/%s/pyp_rerun_%d.txt' %(tempfile.gettempdir() ,gpid)
                if os.path.exists(rerun_gpid_path):
                    rerun_path = rerun_gpid_path
                else:
                    print Colors.RED + rerun_path + " does not exist" + Colors.OFF
                    sys.exit()
            pipe_input = [x.strip() for x in open(rerun_path) if x.strip()]
        
        elif options.blank_inputs:
            pipe_input = []
            end_n = int(options.blank_inputs)
            for n in range(0,end_n):
                pipe_input.append('')
       
        
        elif options.no_input:
            pipe_input = ['']
        
        elif options.small:
            pipe_input = [x.rstrip() for x in sys.stdin.readlines() if x.strip()]
            if not pipe_input:
                pipe_input = [''] #for using control d to activate comands with no input
        else:
            return ([PypStr(x.strip())] for x in sys.stdin if x.strip())
  
        rerun_file = open(rerun_path, 'w')
        rerun_file.write('\n'.join([str(x) for x in pipe_input]))
        rerun_file.close()


        inputs = pipe_input

        return [[PypStr(x)] for x in inputs]

    def main(self):
        '''generates input stream based on file, std-in options, rerun, starts process loop, generates output'''
        second_stream_input = [PypStr(x) for x in args[1:]] #2nd stream input
        file_input =          [PypStr(x) for x in self.load_file() ]# file input
        
        #load custom executer if possible.
        self.final_execute=self.get_custom_execute()
        
        #load user and group macros. 
        user_macro_path,group_macro_path=self.get_custom_macro_paths()
        user_macros = self.load_macros(user_macro_path)
        group_macros = self.load_macros(group_macro_path)
        group_macros.update(user_macros) #merges group and user macros
        macros = group_macros
        
        #macros for action ie saving and deleting
        action_macros = group_macros if options.macro_group else user_macros
        action_macros_path = group_macro_path if options.macro_group else user_macro_path
        
        self.list_macros(macros)
        self.delete_macros(action_macros, action_macros_path)
        
        if not args: # default command is just to print.
            cmds = ['p']
        else:
            cmds = self.cmds_split(args[0], macros)

        self.write_macros(action_macros, action_macros_path, cmds) #needs cmds before we write macros
       
        inputs = self.initilize_input() #figure out our input stream
        

        # For debugging
        #graphviz = GraphvizOutput()
        #graphviz.output_file = '/media/sf_Alex/pygraphm.png'

        #with PyCallGraph(output=graphviz):
        if options.small:
            self.process(inputs, file_input, cmds, second_stream_input,) #recursive processing to generate history dict
            self.output(cmds) #output text or execute commands from history dict
        else:
            self.processLarge(inputs, file_input, cmds, second_stream_input,) #recursive processing to generate history dict





class Docs():
    manual = ''' 
    ===================================================================================
    PYED PIPER MANUAL
    
    pyp is a command line utility for parsing text output and generating complex
    unix commands using standard python methods. pyp is powered by python, so any
    standard python string or list operation is available.  
    
    The variable "p" represents EACH line of the input as a python string, so for
    example, you can replace all "FOO" with "GOO" using "p.replace('FOO','GOO')".
    Likewise, the variable "pp" represents the ENTIRE input as a python array, so
    to sort the input alphabetically line-by-line, use "pp.sort()"
    
    Standard python relies on whitespace formating such as indentions. Since this 
    is not convenient with command line operations, pyp employs an internal piping
    structure ("|") similar to unix pipes.  This allows passing of the output of
    one command to the input of the next command without nested "(())" structures.
    It also allows easy spliting and joining of text using single, commonsense 
    variables (see below).  An added bonus is that any subresult between pipes
    is available, making it easy to refer to the original input if needed.
    
    Filtering output is straightforward using python Logic operations. Any output
    that is "True" is kept while anything "False" is eliminated. So "p.isdigit()"
    will keep all lines that are completely numbers. 
    
    The output of pyp has been optimized for typical command line scenarios. For
    example, if text is broken up into an array using the "split()" method, the
    output will be conveniently numbered by field because a field selection is
    anticipated.  If the variable  "pp" is employed, the output will be numbered
    line-by-line to facilitate picking any particular line or range of lines. In
    both cases, standard python methods (list[start:end]) can be used to select
    fields or lines of interest. Also, the standard python string and list objects
    have been overloaded with commonly used methods and attributes. For example,
    "pp.uniq()" returns all unique members in an array, and p.kill('foo') will
    eliminate all  "foo" in the input.
    
    pyp commands can be easily saved to disk and recalled using user-defined macros,
    so a complicated parsing operation requiring 20 or more steps can be recalled
    easily, providing an alternative to quick and dirty scripts. For more advanced
    users, these macros can be saved to a central location, allowing other users to
    execute them.  Also, an additional text file (PypCustom.py) can be set up that
    allows additional methods to be added to the pyp str and list methods, allowing
    tight integration with larger facilities data structures or custom tool sets.
    
    -----------------------------------------------------------------------------------
                                PIPING IN THE PIPER
    -----------------------------------------------------------------------------------
    You can pipe data WITHIN a pyp statement using standard unix style pipes ("|"),
    where "p" now represents the evaluation of the python statement before the "|".
    You can also refer back to the ORIGINAL, unadulterated input using the variable
    "o" or "original" at any time...and the variable "h" or "history" allows you
    to refer back to ANY subresult generated between pipes ("|"). 
    
    All pyp statements should be enclosed in double quotes, with single quotes being
    used to enclose any strings.''' + Colors.YELLOW + '''
    
         echo 'FOO IS AN ' | pyp "p.replace('FOO','THIS') | p + 'EXAMPLE'"
           ==> THIS IS AN EXAMPLE''' + Colors.GREEN + '''
    
    -----------------------------------------------------------------------------------
                             THE TYPE OF COLOR IS THE TYPE
    -----------------------------------------------------------------------------------
    pyp uses a simple color and numerical indexing scheme to help you identify what 
    kind of objects you are working with. Don't worry about the specifics right now,
    just keep in mind that different types can be readily identified:
    
    strings:                 hello world
    
    integers or floats:''' + Colors.YELLOW + '''      1984''' + Colors.GREEN + '''
    
    split-up line: ''' + Colors.BOLD +    '''          [''' + Colors.BLUE + '[0]' +  Colors.OFF + Colors.GREEN \
                  + 'hello' + Colors.BOLD + Colors.BLUE + '[1]' +  Colors.OFF  + Colors.GREEN + '''world''' +\
                   Colors.BOLD  + '] ' + Colors.OFF +  Colors.GREEN + '''
    
    entire input list:       ''' +\
    Colors.MAGENTA + '[0]' + Colors.GREEN + 'first line\n' +  Colors.OFF +\
    Colors.MAGENTA + '                             [1]' + Colors.GREEN + 'second line' + Colors.OFF   + Colors.GREEN + '''
                
    dictionaries:'''   + Colors.BOLD +    '''            {''' + Colors.BLUE + 'hello world'  + Colors.BOLD +\
                     Colors.GREEN + ': '  + Colors.OFF +  Colors.GREEN + '1984' +  Colors.BOLD + '}' + Colors.OFF +  Colors.GREEN  + '''
    
    other objects:''' + Colors.MAGENTA + '           RANDOM_OBJECT' + Colors.GREEN + ''' 
    
    The examples below will use a yellow/blue color scheme to seperate them
    from the main text however. Also, all colors can be removed using the
     --turn_off_color flag.
    
    -----------------------------------------------------------------------------------
                                  STRING OPERATIONS
    -----------------------------------------------------------------------------------
    Here is a simple example for splitting the output of "ls" (unix file list) on '.':''' + Colors.YELLOW + '''
    
        ls random_frame.jpg | pyp "p.split('.')"  
            ==>  [''' + Colors.BLUE + '[0]' + Colors.YELLOW + 'random_frame' + Colors.BLUE + '[1]' + Colors.YELLOW + 'jpg] ''' + Colors.GREEN + '''             
    
    The variable "p" represents each line piped in from "ls".  Notice the output has
    index numbers, so it's trivial to pick a particular field or range of fields,
    i.e. pyp "p.split('.')[0]"  is the FIRST field.  There are some pyp generated
    variables that make this simpler, for example the variable "d" or "dot" is the
    same as p.split('.'):''' + Colors.YELLOW + '''
        
        ls random_frame.jpg | pyp "dot"  
            ==> [''' + Colors.BLUE + '[0]' + Colors.YELLOW + 'random_frame' + Colors.BLUE + '[1]' + Colors.YELLOW + '''jpg]
        
        ls random_frame.jpg | pyp "dot[0]"
            ==>   random_frame''' + Colors.GREEN + '''
    
    To Join lists back together, just pipe them to the same or another built-in
    variable(in this case "u", or "underscore"):''' + Colors.YELLOW + '''
    
        ls random_frame.jpg | pyp "dot"  
            ==> [''' + Colors.BLUE + '[0]' + Colors.YELLOW + 'random_frame' + Colors.BLUE + '[1]' + Colors.YELLOW + '''jpg]
        
        ls random_frame.jpg | pyp "dot|underscore"   
            ==> random_frame_jpg ''' + Colors.GREEN + '''
    
    To add text, just enclose it in quotes, and use "+" or "," just like python: ''' + Colors.YELLOW + '''
    
        ls random_frame.jpg | pyp "'mkdir seq.tp_' , d[0]+ '_v1/misc_vd8'"  
            ==> mkdir seq.tp_random_frame_v1/misc_vd8'" ''' + Colors.GREEN + '''
            
    A fundamental difference between pyp and standard python is that pyp allows you
    to print out strings and lists on the same line using the standard "+" and ","
    notation that is used for string construction. This allows you to have a string
    and then print out the results of a particular split so it's easy to pick out
    your field of interest: ''' + Colors.YELLOW + '''
    
        ls random_frame.jpg | pyp "'mkdir', dot"  
         ==> mkdir [''' + Colors.BLUE + '[0]' + Colors.YELLOW + 'random_frame' + Colors.BLUE + '[1]' + Colors.YELLOW + '''jpg] '''+ Colors.GREEN + '''
    
    In the same way, two lists can be displayed on the same line using "+" or ",".
    If you are trying to actually combine two lists, enclose them in parentheses:'''  + Colors.YELLOW + '''
    
        ls random_frame.jpg | pyp "(underscore + dot)" 
        ==> [''' + Colors.BLUE + '[0]' + Colors.YELLOW + 'random' + Colors.BLUE  + '[1]' +  Colors.YELLOW  +'frame.jpg'\
         + Colors.BLUE + '[2]' + Colors.YELLOW + 'random_frame'+ Colors.BLUE + '[3]' + Colors.YELLOW + '''jpg] ''' + Colors.GREEN + '''
         
    This behaviour with '+' and ',' holds true in fact for ANY object, making
    it easy to build statements without having to worry about whether they
    are strings or not.
        
    -----------------------------------------------------------------------------------
                               ENTIRE INPUT LIST OPERATIONS
    -----------------------------------------------------------------------------------
    To perform operations that operate on the ENTIRE array of std-in, Use the variable
    "pp", which you can manipulate using any standard python list methods. For example,
    to sort the input, use:''' + Colors.YELLOW + '''
       
       pp.sort()''' + Colors.GREEN + '''
    
    When in array context, each line will be numbered with it's index in the array,
    so it's easy to, for example select the 6th line of input by using "pp[5]".
    You can pipe this back to p to continue modifying this input on a 
    line-by-line basis: ''' + Colors.YELLOW + '''
    
       pp.sort() | p  ''' + Colors.GREEN + '''
    
    You can add arbitrary entries to your std-in stream at this point using 
    list addition. For example, to add an entry to the start and end:''' +  Colors.YELLOW + '''
    
       ['first entry']  +  pp  +  ['last entry']  ''' + Colors.GREEN + ''' 
    
    The new pp will reflect these changes for all future operations.
    
    There are several methods that have been added to python's normal list methods 
    to facilitate common operations. For example, keeping unique members or 
    consolidating all input to a single line can be accomplished with: '''+  Colors.YELLOW + '''
    
       pp.uniq()
       pp.oneline()'''+ Colors.GREEN + ''' 
    
    Also, there are a few useful python math functions that work on lists of
    integers or floats like sum, min, and max. For example, to add up 
    all of the integers in the last column of input: '''+  Colors.YELLOW + '''
    
       whitespace[-1] | int(p) | sum(pp) '''+ Colors.GREEN + ''' 
    
    
    -----------------------------------------------------------------------------------
                                  MATH OPERATIONS
    -----------------------------------------------------------------------------------
    To perform simple math, use the integer or float functions  (int() or float())
    AND put the math in "()" + ''' + Colors.YELLOW + '''
    
        echo 665 | pyp "(int(p) + 1)"
           ==> 666 ''' + Colors.GREEN + '''
    -----------------------------------------------------------------------------------
                                  LOGIC FILTERS
    -----------------------------------------------------------------------------------
    To filter output based on a python function that returns a Booleon (True or False),
    just pipe the input to this function, and all lines that return True will keep
    their current value, while all lines that return False will be eliminated. ''' + Colors.YELLOW + '''
    
        echo 666 | pyp  "p.isdigit()"
           ==> 666''' + Colors.GREEN + '''
           
    Keep in mind, that if the Boolean is True, the entire value of p is returned.
    This comes in handy when you want to test on one field, but use something else.
    For example, a[2].isdigit() will return p, not a[2] if a[2] is a digit.
    
    Standard python logic operators such as "and","or","not", and 'in' work as well.
    
    For example to filter output based on the presence of "GOO" in the line, use this:''' + Colors.YELLOW + '''
    
        echo GOO | pyp "'G' in p"
           ==> GOO'''+ Colors.GREEN + '''
    
    The pyp functions "keep(STR)" and "lose(STR)", and their respective shortcuts,
    "k(STR)" and "i(STR)", are very useful for simple OR style string
    filtering. See below.
    
    Also note, all lines that test False ('', {}, [], False, 0) are eliminated from
    the output completely. You can instead print out a blank line if something tests
    false using --keep_false. This is useful if you need placeholders to keep lists 
    in sync, for example.
    -----------------------------------------------------------------------------------
                       SECOND STREAM, TEXT FILE, AND BLANK INPUT
    -----------------------------------------------------------------------------------
    Normally, pyp receives its input by piping into it like a standard unix shell
    command, but sometimes it's necessary to combine two streams of inputs, such as
    consolidating the output of two shell commands line by line.  pyp provides
    for this with the second stream input. Essentially anything after the pyp
    command that is not associated with an option flag is brought into pyp as
    the second stream, and can be accessed seperately from the primary stream
    by using the variable 'sp'
    
    To input a second stream of data, just tack on strings or execute (use backticks)
    a command to the end of the pyp command, and then access this array using the
    variable 'sp'  ''' + Colors.YELLOW + '''
    
        echo random_frame.jpg | pyp "p, sp" `echo "random_string"`
           ===> random_frame.jpg random_string''' + Colors.GREEN + '''
           
    In a similar way, text input can be read in from a text file using the 
    --text_file flag. You can access the entire file as a list using the variable
    'fpp', while the variable 'fp' reads in one line at a time. This text file
    capability is very useful for lining up std-in data piped into pyp with
    data in a text file like this:''' + Colors.YELLOW + ''' 
    
        echo normal_input | pyp -text_file example.txt "p, fp" ''' + Colors.GREEN + '''
    
    This setup is geared mostly towards combining data from std-in with that in
    a text file.  If the text file is your only data, you should cat it, and pipe
    this into pyp.
    
    If you need to generate output from pyp with no input, use --blank_inputs.
    This is useful for generating text based on line numbers using the 'n'
    variable.
    
    -----------------------------------------------------------------------------------
                       TEXT FILE AND SECOND STREAM LIST OPERATIONS
    -----------------------------------------------------------------------------------
    List operations can be performed on file inputs and second stream 
    inputs using the variables spp and fpp, respectively.  For example to sort
    a file input, use: ''' + Colors.YELLOW + '''
    
       fpp.sort() ''' + Colors.GREEN + '''
       
    Once this operation takes place, the sorted fpp will be used for all future
    operations, such as referring to the file input line-by-line using fp.  
    
    You can add these inputs to the std-in stream using simple list
    additions like this: ''' + Colors.YELLOW + ''' 
    
        pp + fpp ''' + Colors.GREEN + '''
    
    If pp is 10 lines, and fpp is 10 line, this will result in a new pp stream 
    of 20 lines. fpp will remain untouched, only pp will change with this 
    operation.   
    
    Of course, you can trim these to your needs using standard
    python list selection techniques: ''' + Colors.YELLOW + '''
    
        pp[0:5] + fpp[0:5] ''' + Colors.GREEN + '''
    
    This will result in a new composite input stream of 10 lines. 
    
    Keep in mind that the length of fpp and spp is trimmed to reflect
    that of std-in.  If you need to see more of your file or second
    stream input, you can extend your std-in stream simply:''' + Colors.YELLOW + '''
    
        pp + ['']*10 ''' + Colors.GREEN + '''
          
    will add 10 blank lines to std-in, and thus reveal another 10
    lines of fpp if available.
    
    
    -----------------------------------------------------------------------------------
                                  MACRO USAGE
    -----------------------------------------------------------------------------------
    Macros are a way to permently store useful commands for future recall. They are
    stored in your home directory by default. Facilites are provided to store public
    macros as well, which is useful for sharing complex commands within your work group.
    Paths to these text files can be reset to anything you choose my modifying the
    PypCustom.py config file.  Macros can become quite complex, and provide
    a useful intermediate between shell commands and scripts, especially for solving
    one-off problems.  Macro listing, saving, deleting, and searching capabilities are
    accessible using --macrolist, --macro_save, --macro_delete, --macro_find flags.
    Run pyp --help for more details.
    
    you can pyp to and from macros just like any normal pyp command. ''' + Colors.YELLOW + '''
        pyp "a[0]| my_favorite_macros | 'ls', p" ''' + Colors.GREEN + '''
    
    Note, if the macro returns a list, you can access individual elements using
    [n] syntax:''' + Colors.YELLOW + '''
        pyp "my_list_macro[2]" ''' + Colors.GREEN + '''
    
    Also, if the macro uses %s, you can append a %(string,..) to then end to string
    substitute: ''' + Colors.YELLOW + '''
        pyp "my_string_substitution_macro%('test','case')" ''' + Colors.GREEN + '''
    
    By default, macros are saved in your home directory. This can be modifed to any 
    directory by modifying the user_macro_path attribute in your PypCustom.py. If
    you work in a group, you can also save macros for use by others in a specific
    location by modifying group_macro_path. See the section below on custom 
    methods about how to set up this file.
    -----------------------------------------------------------------------------------
                                  CUSTOM METHODS
    -----------------------------------------------------------------------------------
    pyed pyper relies on overloading the standard python string and list objects
    with its own custom methods.  If you'd like to try writing your own methods
    either to simplify a common task or integrate custom functions using a 
    proprietary API, it's straightforward to do. You'll have to setup a config
    file first:
        
        pyp --unmodified_config > PypCustom.py
        sudo chmod 666 PypCustom.py
    
    There are example functions for string, list, powerpipe, and generic methods.
    to get you started. When pyp runs, it looks for this text file and automatically
    loads any found functions, overloading them into the appropriate objects. You
    can then use your custom methods just like any other pyp function.
    -----------------------------------------------------------------------------------
                                  TIPS AND TRICKS
    -----------------------------------------------------------------------------------
    If you have to cut and paste data (from an email for example), execute pyp, paste
    in your data, then hit CTRL-D.  This will put the data into the disk buffer. Then,
    just rerun pyp with --rerun, and you'll be able to access this data for further
    pyp manipulations!
    
    If you have split up a line into a list, and want to process this list line by 
    line, simply pipe the list to pp and then back to p: pyp "w | pp |p"
    
    Using --rerun is also great way to buffer data into pyp from long-running scripts
    
    pyp is an easy way to generate commands before executing them...iteratively keep
    adding commands until you are confident, then use the --execute flag or pipe them
    to sh.  You can use ";" to set up dependencies between these commands...which is
    an easy way to work out command sequences that would typically be executed in a 
    "foreach" loop.
    
    Break out complex intermediate steps into macros. Macros can be run at any point in a 
    pyp command.
    
    If you find yourself shelling out constantly to particular commands, it might 
    be worth adding python methods to the PypCustom.py config, especially if you
    are at a large facility.
    
    Many command line tools (like stat) use a KEY:VALUE format. The shelld function
    will turn this into a python dictionary, so you can access specific data using
    their respective keys by using something like this: shelld(COMMAND)[KEY] 
    
    ===================================================================================
    HERE ARE THE BUILT IN VARIABLES:
        
        STD-IN (PRIMARY INPUT)
        -------------
        p        line-by-line std-in variable. p represents whatever was 
                 evaluated to before the previous pipe (|).
        
        pp       python list of ALL std-in input. In-place methods like
                 sort() will work as well as list methods like sorted(LIST)
        
        SECOND STREAM
        --------------
        sp       line-by-line input second stream input, like p, but from all 
                 non-flag arguments AFTER pyp command: pyp "p, sp" SP1 SP2 SP3 ...
        
        spp      python list of ALL second stream list input. Modifications of
                 this list will be picked up with future references to sp 
        
        FILE INPUT
        --------------
        fp       line-by-line file input using --text_file TEXT_FILE. fp on 
                 the first line of output is the first line of the text file
        
        fpp      python list of ALL text file input. Modifications of
                 this list will be picked up with future references to fp 
        
        
        COMMON VARIABLES
        ----------------
        original original line by line input to pyp    
        o        same as original    
        
        quote    a literal "      (double quotes can't be used in a pyp expression)
        paran    a literal '
        dollar   a literal $
    
        n        line counter (1st line is 0, 2nd line is 1,...use the form "(n+3)"
                 to modify this value. n changes to reflect filtering and list ops.
        nk       n + 1000
        
        date     date and time. Returns the current datetime.datetime.now() object.
        pwd      present working directory
        
        history  history array of all previous results:
                   so pyp "a|u|s|i|h[-3]" shows eval of s
        h        same as history
        
        digits   all numbers [0-9]
        letters  all upper and lowercase letters (useful when combined with variable n).
                 letters[n] will print out "a" on the first line, "b" on the second...
        punctuation all punctuation [!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]
        
        
    ===================================================================================
    THE FOLLOWING ARE SPLIT OR JOINED BASED ON p BEING A STRING OR AN ARRAY:
        
        s  OR slash          p split/joined on "/"        
        d  OR dot            p split/joined on "."        
        w  OR whitespace     p split/joined on whitespace (on spaces,tabs,etc)
        u  OR underscore     p split/joined on '_'       
        c  OR colon          p split/joined on ':'       
        mm OR comma          p split/joined on ','        
        m  OR minus          p split/joined on '-'        
        a  OR all            p split on [' '-_=$...] (on "All" metacharacters)
    
    Also, the ORIGINAL INPUT (history[0]) lines are split on delimiters as above, but 
    stored in os, od, ow, ou, oc, omm, om and oa as well as oslash, odot, owhitepace,
    ocomma, ominus, and oall''' + Colors.GREEN + '''
    
    ===================================================================================
    HERE ARE THE BUILT IN FUNCTIONS AND ATTRIBUTES: 
    
       Function                Notes
       --------------------------------------------------------------------------------
            STRING     (all python STRING methods like p.replace(STRING1,STRING2) work)
       --------------------------------------------------------------------------------
        p.digits()           returns a list of contiguous numbers present in p
        p.letters()          returns a list of contiguous letters present in p
        p.punctuation()      returns a list of contiguous punctuation present in p
        
        p.trim(delimiter)    removes last field from string based on delimiter
                             with the default being "/"
        p.kill(STR1,STR2...) removes specified strings 
        p.clean(delimeter)   removes all metacharacters except for slashes, dots and 
                             the joining delimeter (default is "_")
        p.re(REGEX)          returns portion of string that matches REGEX regular 
                             expression. works great with p.replace(p.re(REGEX),STR) 
        
        p.dir()                directory of path
        p.file()               file name of path
        p.ext()                file extension (jpg, tif, hip, etc) of path
       
        These fuctions will work with all pyp strings eg: p, o, dot[0], p.trim(), etc. 
        Strings returned by native python functions (like split()) won't have these 
        available, but you can still access them using str(STRING). Basically,
        manually recasting anything using as a str(STRING) will endow them with 
        the custom pyp methods and attributes.
       
       --------------------------------------------------------------------------------                                                    
            LIST        (all LIST methods like pp.sort(), pp[-1], and pp.reverse() work)
       --------------------------------------------------------------------------------
       pp.delimit(DELIM)     split input on delimiter instead of newlines
       pp.divide(N)          consolidates N consecutive lines to 1 line. 
       pp.before(STRING, N)  searches for STRING, colsolidates N lines BEFORE it to
                             the same line. Default N is 1. 
       pp.after(STRING, N)   searches for STRING, colsolidates N lines AFTER  it to
                             same line. Default N is 1.
       pp.matrix(STRING, N)  returns pp.before(STRING, N) and pp.after(STRING, N).
                             Default N is 1.
       pp.oneline(DELIM)     combines all list elements to one line with delimiter.
                             Default delimeter is space.
       pp.uniq()             returns only unique elements
       pp.unlist()           breaks up ALL lists up into seperate single lines
       
       pp + [STRING]         normal python list addition extends list
       pp + spp + fpp        normal python list addition combines several inputs.
                             new input will be pp; spp and fpp are unaffected.
       sum(pp), max(pp),...  normal python list math works if pp is properly cast
                             i.e. all members of pp should be integers or floats.
       
       These functions will also work on file and second stream lists:  fpp and spp
       
       
       --------------------------------------------------------------------------------                                                    
            NATIVE PYP FUNCTIONS
       --------------------------------------------------------------------------------
       keep(STR1,STR2,...)   keep all lines that have at least one STRING in them
       k(STR1,STR2,...)      shortcut for keep(STR1,STR2,...)
       lose(STR1,STR2,...)   lose all lines that have at least one STRING in them
       l(STR1,STR2,...)      shortcut for lose(STR1,STR2,...)
       
       rekeep(REGEX)         keep all lines that match REGEX regular expression
       rek(REGEX)            shortcut for rekeep(REGEX)
       relose(REGEX)         lose all lines that match REGEX regular expression
       rel(REGEX)            shortcut for relose(REGEX)
       
       shell(SCRIPT)         returns output of SCRIPT in a list.
       shelld(SCRIPT,DELIM)  returns output of SCRIPT in dictionary key/value seperated 
                             on ':' (default) or supplied delimeter
       env(ENVIROMENT_VAR)   returns value of evironment variable using os.environ.get()
       glob(PATH)            returns globed files/directories at PATH. Make sure to use
                             '*' wildcard
       str(STR)              turns any object into an PypStr object, allowing use 
                             of custom pyp methods as well as normal string methods. 
    
    SIMPLE EXAMPLES:
    ===================================================================================
       pyp "'foo ' + p"                 ==>  "foo" + current line
       pyp "p.replace('x','y') | p + o" ==>  current line w/replacement + original line 
       pyp "p.split(':')[0]"            ==>  first field of string split on ':'
       pyp "slash[1:3]"                 ==>  array of fields 1 and 2 of string split on '/'
       pyp "s[1:3]|s"                   ==>  string of above joined with '/'
    ''' + Colors.OFF
    
    
    
    unmodified_config = '''
#!/usr/bin/env python
# This must be saved in same directory as pyp (or be in the python path)
# make sure to name this PypCustom.py and change permission to 666

import sys
import os


class Colors(object):
    OFF = chr(27) + '[0m'
    RED = chr(27) + '[31m'
    GREEN = chr(27) + '[32m'
    YELLOW = chr(27) + '[33m'
    MAGENTA = chr(27) + '[35m'
    CYAN = chr(27) + '[36m'
    WHITE = chr(27) + '[37m'
    BLUE = chr(27) + '[34m'
    BOLD = chr(27) + '[1m'
    COLORS = [OFF, RED, GREEN, YELLOW, MAGENTA, CYAN, WHITE, BLUE, BOLD]


class NoColors(object):
    OFF = ''
    RED = ''
    GREEN =''
    YELLOW = ''
    MAGENTA = ''
    CYAN = ''
    WHITE =''
    BLUE =  ''
    BOLD =  ''
    COLORS = [OFF, RED, GREEN, YELLOW, MAGENTA, CYAN, WHITE, BLUE, BOLD]


class PypCustom(object):
    'modify below paths to set macro paths'
    def __init__(self):
        self.user_macro_path = os.path.expanduser('~')+ '/pyp_user_macros.json'
        self.group_macro_path = os.path.expanduser('~')+ '/pyp_user_macros.json'
        self.custom_execute = False


class PowerPipeListCustom():
    'this is used for pp functions (list fuctions like sort) that operate on all inputs at once.'
    def __init__(self, *args):
        pass
    
    def test(self):
        print 'test' #pp.test() will print "test"


class PypStrCustom():   
    'this is used for string functions using p and other pyp string variables'
    def __init__(self, *args):
        self.test_attr = 'test attr'
    
    def test(self):
        print 'test' #p.test() will print "test" is p is a str
    
    
class PypListCustom():
    def __init__(self, *args):
        pass

    def test(self):
        print 'test' #p.test() will print "test" is p is a list broken up from a str


class PypFunctionCustom(object):
    'this is used for custom functions and variables (non-instance)'
    test_var = 'works'
    
    def __init__(self, *args):
        pass
    
    def test(self):
        print 'working func '  + self
'''


    usage = """    
pyp is a python-centric command line text manipulation tool.  It allows you to format, replace, augment
and otherwise mangle text using standard python syntax with a few golden-oldie tricks from unix commands
of the past. You can pipe data into pyp or cut and paste text, and then hit ctrl-D to get your input into pyp.  
    
After it's in, you can use the standard repertoire of python commands to modify the text. The key variables
are "p", which represents EACH LINE of the input as a PYTHON STRING.  and "pp", which represents ALL of the
inputs as a PYTHON ARRAY. 

You can pipe data WITHIN a pyp statement using standard unix style pipes ("|"), where "p" now represents the
evaluation of the python statement before the "|". You can also refer back to the ORIGINAL, unadulterated
input using the variable "o" or "original" at any time...and the variable "h" or "history" allows you
to refer back to ANY subresult generated between pipes ("|"). 

All pyp statements should be enclosed in double quotes, with single quotes being used to enclose any strings.

     echo 'FOO IS AN ' | pyp "p.replace('FOO','THIS') | p + 'EXAMPLE'"
       ==> THIS IS AN EXAMPLE
    
Splitting texton metacharacters is often critical for picking out particular fields of interest,
so common SPLITS and JOINS have been assigned variables. For example, "underscore" or "u" will split a string
to an array based on undercores ("_"), while "underscore" or "u" will ALSO join an array with underscores ("_") 
back to a string.  

Here are a few key split/join variables; run with --manual for all variable and see examples below in the string section.
    
    s OR slash           splits AND joins on "/"
    u OR underscore      splits AND joins on "_"
    w OR whitespace      splits on whitespace (spaces,tabs,etc) AND joins with spaces
    a OR all             splits on ALL metacharacters [!@#$%^&*()...] AND joins with spaces
    
EXAMPLES:
------------------------------------------------------------------------------
              List Operations              # all python list methods work
------------------------------------------------------------------------------
print all lines                              ==> pyp  "pp"
sort all input lines                         ==> pyp  "pp.sort()"
eliminate duplicates                         ==> pyp  "pp.uniq()"
combine all lines to one line                ==> pyp  "pp.oneline()"
print line after FOO                         ==> pyp  "pp.after('FOO')"
list comprehenision                          ==> pyp  "[x for x in pp]"
return to string context after sort          ==> pyp  "pp.sort() | p"

-------------------------------------------------------------------------------
            String Operations               # all python str methods work
-------------------------------------------------------------------------------
print line                                   ==> pyp  "p"
combine line with FOO                        ==> pyp  "p +'FOO'"
above, but combine with original input       ==> pyp  "p +'FOO'| p + o"

replace FOO with GOO                         ==> pyp  "p.replace('FOO','GOO')"
remove all GOO and FOO                       ==> pyp  "p.kill('GOO','FOO')"

string substitution                          ==> pyp  "'%s FOO %s %s GOO'%(p,p,5)"

split up line by FOO                         ==> pyp  "p.split('FOO')"
split up line by '/'                         ==> pyp  "slash"
select 1st field split up by '/'             ==> pyp  "slash[0]"
select fields 3 through 5 split up by '/'    ==> pyp  "s[2:6]"   
above joined together with '/'               ==> pyp  "s[2:6] | s"

-------------------------------------------------------------------------------
            Logic Filters                   # all python Booleon methods work
-------------------------------------------------------------------------------
keep all lines with GOO and FOO              ==> pyp  "'GOO' in p and 'FOO' in p"
keep all lines with GOO or FOO               ==> pyp  "keep('GOO','FOO')"
keep all lines that are numbers              ==> pyp  "p.isdigit()"

lose all lines with GOO and FOO              ==> pyp  "'GOO' not in p and 'FOO' not in p"
lose all lines with GOO or FOO               ==> pyp  "lose('GOO','FOO')"
lose all lines that are numbers              ==> pyp  "not p.isdigit()"

-------------------------------------------------------------------------------                
TO SEE EXTENDED HELP, use --manual

"""

if __name__ == '__main__':
    parser = optparse.OptionParser(Docs.usage)

    parser.add_option("-m", "--manual", action='store_true', help="prints out extended help")
    parser.add_option("-l", "--macro_list", action='store_true', help="lists all available macros")
    parser.add_option("-s", "--macro_save", dest='macro_save_name', type='string', help='saves current command as macro. use "#" for adding comments  EXAMPLE:    pyp -s "great_macro # prints first letter" "p[1]"')
    parser.add_option("-f", "--macro_find", dest='macro_find_name', type='string', help='searches for macros with keyword or user name')
    parser.add_option("-d", "--macro_delete", dest='macro_delete_name', type='string', help='deletes specified public macro')
    parser.add_option("-g", "--macro_group", action='store_true', help="specify group macros for save and delete; default is user")
    parser.add_option("-t", "--text_file", type='string', help="specify text file to load. for advanced users, you should typically cat a file into pyp")
    parser.add_option("-x", "--execute", action='store_true', help="execute all commands.")
    parser.add_option("-c", "--turn_off_color", action='store_true', help="prints raw, uncolored output")
    parser.add_option("-u", "--unmodified_config", action='store_true', help="prints out generic PypCustom.py config file")
    parser.add_option("-b", "--blank_inputs", action='store', type='string', help="generate this number of blank input lines; useful for generating numbered lists with variable 'n'")
    parser.add_option("-n", "--no_input", action='store_true', help="use with command that generates output with no input; same as --dummy_input 1")
    parser.add_option("-k", "--keep_false", action='store_true', help="print blank lines for lines that test as False. default is to filter out False lines from the output")
    parser.add_option("-r", "--rerun", action="store_true", help="rerun based on automatically cached data from the last run. use this after executing \"pyp\", pasting input into the shell, and hitting CTRL-D")    
    parser.add_option("-L", "--large", dest='small', action="store_false", default=True, help="large file input.  Allows only single line operations.")
    parser.add_option("--DEBUG", dest='DEBUG', action="store_true", default=False, help="Debug mode.  Do not catch exceptions.")
    parser.add_option("-D", "--delimited", dest='delimited', action="store_true", default=False, help="Raw, tab delimited output.  No colors or index numbers.")
    parser.add_option("-S", "--separated-by", dest='delimiter', type='string', default='\t', help="Delimiter for output.  Defaults to tab.")
   
    (options, args) = parser.parse_args()

    if options.turn_off_color or options.execute: # overall color switch asap.
        Colors = NoColors

    if options.DEBUG:
        pyp = Pyp().main()
    else:
        try:
            pyp = Pyp().main()
        except Exception, err:
            print Colors.RED + str(err) + Colors.OFF


