#!/usr/bin/env python2.7

import sys

class ArgumentParser(object):

    OPTION_SINGLE = 1
    OPTION_PARAMETERIZED = 2

    PARAM_SHORT = 1
    PARAM_LONG = 2

    @classmethod
    def from_argv(cls):
        """
            Creates an ArgumentParser engine with args from 
            sys.argv[].
        """
        return cls(sys.argv)

    def __init__(self, args, mapping = {}):
        """
            Initializes an ArgumentParser instance.  Parses out
            things that we already know, like args[0] (should be the 
            executable script).
        """

        try:
            self.exec_file = args[0]
        except:
            self.exec_file = ''

        self.__args = args
        
        self._default_types = {
                ArgumentParser.PARAM_SHORT : ArgumentParser.OPTION_SINGLE,
                ArgumentParser.PARAM_LONG  : ArgumentParser.OPTION_SINGLE
        }
        self._opt_types = {}
        self._mapping = mapping
        self._descriptions = {}
        self.options = {}
        self.parameters = []

    def set_default_param_type(self, param, opt = OPTION_SINGLE):
        """
            Sets the default type map that a parameter will be treated as.
            Can help force more uniform arguments without having to pre-define
            options.
        """

        self._default_types[param] = opt

    def add_option_type(self, option, opt = OPTION_SINGLE):
        """
            Adds a type mapping to a specific option. Allowed types are 
            OPTION_SINGLE and OPTION_PARAMETERIZED.
        """

        self._opt_types[option] = opt

    def add_option_mapping(self, option, map_name):
        """
            Maps a option value (-a, -g, --thing, etc.) to a full word or
            phrase that will be stored in the options dictionary after parsing
            is finished.  Makes option usage easier.
        """

        self._mapping[option] = map_name

    def add_option_description(self, option, description):
        """
            Adds a helpful description for an argument. Is returned when 
            get_option_descriptions is called.
        """

        self._descriptions[option] = description

    def get_option_descriptions(self):
        """
            Returns a map of options to their respective descriptions.  Good
            for printing out a series of help messages describing usage.
        """

        processed_descriptions = {}
        for option, description in self._descriptions.iteritems():
            if len(option) == 1: # This is a flag. Append a dash.
                option = '-' + option
                processed_descriptions.update({ option : description })
            elif len(option) > 1 and option.startswith('--'): # Option. Append blindly.
                processed_descriptions.update({ option : description })
            elif len(option) > 1 and not option.startswith('--'): # Option. Append double-dash.
                option = '--' + option
                processed_descriptions.update({ option : description })
            else: # What is this? Blindly append.
                processed_descriptions.update({ option : description })

        return processed_descriptions

    def parse(self):
        """ 
            Parses out the args into the mappings provided in self.mapping,
            stores the result in self.options.
        """

        waiting_argument = None

        for param in self.__args:
            if param.startswith('--'): # Long option mapping.
                paraml = param[2:]
                if '=' in paraml:
                    param, value = paraml.split('=')
                    # Automatically store a PARAMETERIZED option type, if none exists.
                    if param not in self._opt_types:
                        self.add_option_type(param, ArgumentParser.OPTION_PARAMETERIZED)
                else:
                    param = paraml
                    if param not in self._opt_types:
                        self.add_option_type(param, self._default_types[ArgumentParser.PARAM_LONG])
                store_as = param
                if param in self._mapping:
                    self.options.update({ self._mapping[param] : True })
                    store_as = self._mapping[param]
                else:
                    self.options.update({ param : True })
                if param in self._opt_types:
                    ptype = self._opt_types[param]
                    if ptype == ArgumentParser.OPTION_PARAMETERIZED:
                        if '=' in paraml: # Option is long and contains the value.
                            self.options.update({ store_as : value })
                            waiting_argument = None
                        else:
                            waiting_argument = store_as
            elif param.startswith('-'): # Short option mapping.
                param = param[1:]
                for opt in param:
                    store_as = opt
                    if opt in self._mapping:
                        self.options.update({ self._mapping[opt] : True })
                        store_as = self._mapping[opt]
                    else:
                        self.options.update({ opt : True })
                    if opt in self._opt_types:
                        ptype = self._opt_types[opt]
                        if ptype == ArgumentParser.OPTION_PARAMETERIZED:
                            waiting_argument = store_as
            else: # Option parameter or command parameter.
                if waiting_argument is not None:
                    self.options.update({ waiting_argument : param })
                    waiting_argument = None
                else:
                    self.parameters.append(param)
