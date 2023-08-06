#!/usr/bin/env python2.7

import sys

class ArgumentParser(object):

    OPTION_SINGLE = 1
    OPTION_PARAMETERIZED = 2

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
        
        self._opt_types = {}
        self._mapping = mapping
        self._descriptions = {}
        self._aliases = {}
        self.options = {}
        self.parameters = []

    def add_option_type(self, option, type = OPTION_SINGLE):
        """
            Adds a type mapping to a specific option. Allowed types are 
            OPTION_SINGLE and OPTION_PARAMETERIZED.
        """

        self._opt_types[option] = type

    def add_option_mapping(self, option, map_name):
        """
            Maps a option value (-a, -g, --thing, etc.) to a full word or
            phrase that will be stored in the options dictionary after parsing
            is finished.  Makes option usage easier.
        """

        self._mapping[option] = map_name

    def add_option_alias(self, option, alias):
        """
            Adds an alias for a short option to a long option or for multiple
            long options.
        """

        self._aliases[option] = alias

        if option in self._descriptions:
            self._descriptions.remove(option)

        if alias in self._descriptions:
            description = self._descriptions[alias]
            self._descriptions.remove(alias)
            alias_keys = [option]
            if isinstance(alias, list):
                alias_keys.extend(alias)
            else:
                alias_keys.append(alias)
            self._descriptions.update({ alias_keys : description })

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
        for options, description in self._descriptions.iteritems():
            if not isinstance(options, list):
                options = [options]
            processed_options = []
            for option in options:
                if len(option) == 1: # This is a flag. Append a dash.
                    option = '-' + option
                    processed_options.append(option)
                elif len(option) > 1 and option.startswith('--'): # Option. Append blindly.
                    processed_options.append(option)
                elif len(option) > 1 and not option.startswith('--'): # Option. Append double-dash.
                    option = '--' + option
                    processed_options.append(option)
                else: # What is this? Blindly append.
                    processed_options.append(option)
            processed_descriptions.update({ processed_options : description })

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
                else:
                    param = paraml
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
                    self.options[waiting_argument] = param
                    waiting_argument = None
                else:
                    self.parameters.append(param)
