#!/usr/bin/env python

import copy, urllib2, json
from contextlib import closing
from urllib2 import urlopen

""" We need to write some better documentation for this crap.
    Either that, or we just need to re-write the configuration stuff
    from scratch and actually document it this time.
"""

class ConfigurationSection(dict):
    """ modified dictionary that returns none for invalid keys
    """
    
    def __init__(self):

        dict.__init__(self)
        
        self.mutable = True
    
    def __getitem__(self, key):
    
        try: return dict.__getitem__(self, key)
        except (IndexError, KeyError) as e:
            raise KeyError("Unknown configuration key '%s'." % (key))
    
    def __setitem__(self, key, value):
    
        if self.mutable:
            self.update({ key: value })
        else:
            raise AttributeError("This section is not mutable.")
    
    def set_mutable(self, mutable):
    
        self.mutable = mutable
    
    def set(self, key, value):
    
        return self.__setitem__(key, value)
    
    def get(self, key):
    
        return self.__getitem__(key)
    
    def get_list(self, key, delimiter = ",", default = []):
    
        try:
            val = self.get(key)
            l = val.split(delimiter) if len(val) > 0 else default
            return [item.strip() for item in l]
        except: return default

    def get_string(self, key, default = ""):
    
        try:
            if str(self.get(key)) == '!None': return None
            return str(self.get(key)) or default
        except: raise
    
    def get_int(self, key, default = None):
    
        try: return int(self.get(key)) or default
        except: return default
    
    def get_bool(self, key, default = False):
    
        try:
            val = self.get(key) or default
            if isinstance(val, bool):
                return val
            elif isinstance(val, str):
                if val.lower() == 'true':
                    self.set(key, True)
                    return True
                elif val.lower() == 'false':
                    self.set(key, False)
                    return False
                else:
                    return default
            elif isinstanct(val, int):
                if val == 1:
                    self.set(key, True)
                    return True
                elif val == 0:
                    self.set(key, False)
                    return False
                else:
                    return default
            else:
                return default
        except: return default

class SectionPromise(object):
    """ this is a configuration section promise
        to make resolution of linked sections post-load
        easier.
    """
    
    promises = []
    
    def __init__(self, config, section, key, link):
        
        self.config = config
        self.section = section
        self.key = key
        self.link = link
        self.__fulfilled = False

        SectionPromise.promises.append(self)

    def __str__(self):
        """ Convert directly to a string for recreating the link
            during config write.  Better for serialization.
        """

        return '@' + self.link

    def resolve(self):
    
        if self.__fulfilled:
            return
        
        section = self.config.get_section(self.section)
        link = self.config.get_section(self.link)
        target = section.get(self.key)

        if isinstance(target, list):
            target.remove(self)
            target.append(link)
            section.set(self.key, target)
        else:
            section.set(self.key, link)

        # Preserve the promise for writing back out.
        section.set("_%s_promise" % (self.key), self)
        self.__fulfilled = True

class Configuration(object):
    """ 
        This definitely needs to be documented.
    """

    def __init__(self):
        """ initialise the container
            store in key:value format withing the certain category
        """

        self.__container = ConfigurationSection()
        
        self._filename = None

        self.loaded = False
        
    def __resolve_links(self):
        """ resolves all linked references.
        """
        
        for promise in SectionPromise.promises:
            promise.resolve()
        
        SectionPromise.promises = []

    def add_section(self, section_name):
        """ adds a new configuration section to the main dictionary.
        """
        
        section = ConfigurationSection()
        self.__container.set(section_name, section)
        
        return section
    
    def remove_section(self, section_name):
        """ removes a section from the main dictionary.
        """
        
        del self.__container[section_name]
    
    def sections(self):
        """ returns a list of all sections in the configuration.
        """

        return self.__container.keys()

    def has_section(self, section_name):
        """ return if x has a section
        """

        return section_name in self.__container

    def get_section(self, section_name):
        """ return a raw/direct reference to a section
        """

        return self.__container[section_name] if self.__container.__contains__(section_name) else None
    
    def unload(self):
        """ unload an entire configuration
        """

        self.__container.clear()
        self.loaded = False
    
    def reload(self):
        """ reload the configuration from the initially specified file
        """

        self.unload()
        self.load(self._filename)
    
    def save(self, filename = None):

        if filename is None:
            filename = self._filename

        if filename is None:
            raise ValueError('No filename specified and no stored filename.')

        with closing(open(filename, 'w')) as config:
            for section, smap in self.__container.iteritems():
                config.write("[%s]\n" % (section))
                for key, value in smap.iteritems():
                    if isinstance(value, list):
                        value = "+list:" + json.dumps(value)
                    elif isinstance(value, ConfigurationSection):
                        if "_%s_promise" % (key) in smap:
                            value = str(smap["_%s_promise" % (key)])
                        else:
                            value = str(value)
                    elif isinstance(value, SectionPromise):
                        continue
                    elif isinstance(value, file):
                        value = "+file:" + value.name
                    else:
                        value = str(value)
                    config.write("%s = %s\n" % (key, value))
                config.write("\n")

    def load(self, filename):
        """
            load(filename)
            
            filename -> name of the file to load.
        """

        try:
            fobj = open(filename, 'r')
            self._filename = filename
            self.load_file(fobj)
            fobj.close()
        except IOError as e:
            raise ValueError("Invalid filename '%s'." % (filename))
        except: 
            raise

    def load_file(self, fobj):
        """ load a file and read in the categories and variables
        """

        if self.loaded: self.__container.clear()
        section_name = None
        option_key = None
        option_value = None

        for line in fobj.readlines():
            line = line.strip('\n').lstrip()
        
            if line.startswith('#') or line.startswith('//') or line.startswith(';'):
                continue
            elif line.startswith('[') and line.endswith(']'):
                # This is the beginning of a section tag.
                section_name = line[1:-1]
                if not self.get_section(section_name):
                    self.add_section(section_name)
                continue
            elif '=' in line:
                set = line.split('=')
                l = len(set[0])
                # strip whitespace
                option_key = set[0].strip()
                option_value = set[1].lstrip() if set[1] is not '' or ' ' else None
                
                if option_value[-1] == ';': option_value = option_value[0:-1]
                section = self.get_section(section_name)
                
                if option_value.startswith('+'): # typed reference / variable
                    dobj_type = option_value.split(':')[0][1:]
                    if len(option_value.split(':')) > 2:
                        dobj_value = ':'.join(option_value.split(':')[1:])
                    else:
                        dobj_value = option_value.split(':')[1]
                    
                    if dobj_type.lower() == 'file':
                        try:
                            section.set(option_key, open(dobj_value, 'r'))
                        except:
                            try: section.set(option_key, open(dobj_value, 'w+'))
                            except: section.set(option_key, None)
                    elif dobj_type.lower() == 'url' or dobj_type.lower() == "uri":
                        try: section.set(option_key, urlopen(dobj_value).read())
                        except: 
                            raise
                            section.set(option_key, None)
                    elif dobj_type.lower() == 'list':
                        try: dobj_list = json.loads('%s' % (dobj_value))
                        except: dobj_list = []
                        dobj_repl = []
                        for item in dobj_list:
                            if item.startswith('@'):
                                link_name = item[1:]
                                if not self.get_section(link_name):
                                    dobj_repl.append(SectionPromise(self, section_name, option_key, link_name))
                                else:
                                    link = self.get_section(link_name)
                                    dobj_repl.append(link)
                            else: dobj_repl.append(item)
                        section.set(option_key, dobj_repl)
                    else:
                        section.set(option_key, option_value)
                elif option_value.startswith('@'): # section reference
                    link_name = option_value[1:]
                    if not self.get_section(link_name):
                        section.set(option_key, SectionPromise(self, section_name, option_key, link_name))
                    else:
                        link = self.get_section(link_name)
                        section.set(option_key, link)
                else: section.set(option_key, option_value)
                continue
            else:
                continue
        self.__resolve_links()
        self.loaded = True
