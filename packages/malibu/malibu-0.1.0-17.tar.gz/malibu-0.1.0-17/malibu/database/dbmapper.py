#!/usr/bin/env python2.7

import sqlite3, types, re

class DBMapper(object):

    # FETCH Constants for __execute()

    FETCH_ONE = 'one'
    FETCH_MANY = 'many'
    FETCH_ALL = 'all'
   
    # INDEX Constants for options dictionary.

    INDEX_PRIMARY = 'primaryIndex'
    INDEX_AUTOINCR = 'autoincrIndex'
    INDEX_UNIQUE = 'uniqueIndices'

    # Placeholder for database options (static methods)

    _options = None
    __default_options = {
            INDEX_PRIMARY : 0,
            INDEX_AUTOINCR : True,
            INDEX_UNIQUE : []
    }

    @staticmethod
    def get_default_options():

        return DBMapper.__default_options
    
    @classmethod
    def set_db_options(cls, db, keys, ktypes, options = __default_options):

        cls._options = {}
        cls._options['database'] = db
        cls._options['keys'] = keys
        cls._options['keytypes'] = ktypes
        cls._options['options'] = options

    @classmethod
    def load(cls, **kw):

        if cls._options is None:
            raise Exception('Static database options have not been set.')

        dbo = cls._options
        obj = cls(dbo['database'])
        cur = dbo['database'].cursor()

        keys = []
        vals = []
        for key, val in kw.iteritems():
            keys.append(key)
            vals.append(val)
        whc = []
        for pair in zip(keys, vals):
            whc.append("%s=?" % (pair[0]))
        query = "select * from %s where (%s)" % (obj._table, ' and '.join(whc))
        result = obj.__execute(cur, query, args = vals)
        if result is None:
            for key in dbo['keys']:
                setattr(obj, "_%s" % (key), None)
            return
        for key, dbv in zip(dbo['keys'], result):
            setattr(obj, "_%s" % (key), dbv)

        return obj

    @classmethod
    def new(cls, **kw):

        if cls._options is None:
            raise Exception('Static database options have not been set.')

        dbo = cls._options
        obj = cls(dbo['database'])
        cur = dbo['database'].cursor()

        keys = []
        vals = []
        for key, val in kw.iteritems():
            keys.append(key)
            vals.append(val)
        anonvals = []
        for val in vals:
            anonvals.append('?')
        query = "insert into %s (%s) values (%s)" % (obj._table, ','.join(keys), ','.join(anonvals))
        result = obj.__execute(cur, query, args = vals)
        
        return cls.load(**kw)

    @classmethod
    def find(cls, **kw):

        if cls._options is None:
            raise Exception('Static database options have not been set.')
        
        dbo = cls._options
        obj = cls(dbo['database'])
        cur = dbo['database'].cursor()
        primaryKey = dbo['keys'][dbo['options'][DBMapper.INDEX_PRIMARY]]

        keys = []
        vals = []
        for key, val in kw.iteritems():
            keys.append(key)
            vals.append(val)
        whc = []
        for pair in zip(keys, vals):
            whc.append('%s=?' % (pair[0]))
        query = "select %s from %s where (%s)" % (primaryKey, obj._table, ' and '.join(whc))
        result = obj.__execute(cur, query, args = vals, fetch = DBMapper.FETCH_ALL)
        
        load_pairs = []
        for row in result:
            load_pairs.append({primaryKey : row[dbo['options'][DBMapper.INDEX_PRIMARY]]})

        return DBResultList([cls.load(**pair) for pair in load_pairs])

    @classmethod
    def find_all(cls):

        if cls._options is None:
            raise Exception('Static database options have not been set.')
        
        dbo = cls._options
        obj = cls(dbo['database'])
        cur = dbo['database'].cursor()
        primaryKey = dbo['keys'][dbo['options'][DBMapper.INDEX_PRIMARY]]

        query = "select %s from %s" % (primaryKey, obj._table)
        result = obj.__execute(cur, query, fetch = DBMapper.FETCH_ALL)

        load_pairs = []
        for row in result:
            load_pairs.append({primaryKey : row[dbo['options'][DBMapper.INDEX_PRIMARY]]})

        return DBResultList([cls.load(**pair) for pair in load_pairs])

    @classmethod
    def join(cls, cond, a, b):

        if cls._options is None or cond._options is None:
            raise Exception('Static database options have not been set.')

        dba = cls._options
        obja = cls(dba['database'])
        dbb = cond._options
        objb = cond(dbb['database'])
        cur = dba['database'].cursor()
        primaryKeyA = dba['keys'][dba['options'][DBMapper.INDEX_PRIMARY]]
        primaryKeyB = dbb['keys'][dba['options'][DBMapper.INDEX_PRIMARY]]

        query = "select A.%s, B.%s from %s as A join %s as B on A.%s=B.%s" % (
                    primaryKeyA, primaryKeyB, obja._table, objb._table, a, b)
        result = obja.__execute(cur, query, fetch = DBMapper.FETCH_ALL)

        load_pair_a = []
        load_pair_b = []
        for row in result:
            load_pair_a.append({primaryKeyA : row[0]})
            load_pair_b.append({primaryKeyB : row[1]})

        return zip([cls.load(**pair) for pair in load_pair_a], [cond.load(**pair) for pair in load_pair_b])

    def __init__(self, db, keys, keytypes, options = __default_options):

        self._db = db
        self._options = options
        self._table = self.__class__.__name__.lower() if 'tableName' not in self._options else self._options['tableName']

        self._keys = keys
        self._keytypes = keytypes

        self._primary_ind = self._options[DBMapper.INDEX_PRIMARY]
        self._autoincr_ind = self._options[DBMapper.INDEX_AUTOINCR]
        self._primary = self._keys[self._primary_ind]
        self._unique_keys = self._options[DBMapper.INDEX_UNIQUE]

        self.__generate_structure()
        self.__generate_getters()
        self.__generate_setters()
        self.__generate_properties()

    def __execute(self, cur, sql, fetch = FETCH_ONE, limit = -1, args = ()):
        
        query = sql
        try:
            if len(args) >= 1:
                cur.execute("select " + ", ".join(["quote(?)" for i in args]), args)
                quoted_values = cur.fetchone()
                for quoted_value in quoted_values:
                    query = query.replace('?', str(quoted_value), 1)
        except: pass

        try: cur.execute(query)
        except (sqlite3.ProgrammingError): cur.execute(query, args)

        if fetch == DBMapper.FETCH_ONE:
            return cur.fetchone()
        elif fetch == DBMapper.FETCH_MANY:
            if limit == -1: limit = cur.arraysize
            return cur.fetchmany(size = limit)
        elif fetch == DBMapper.FETCH_ALL:
            return cur.fetchall()
        else:
            return cur.fetchall()

    def __get_table_info(self):

        cur = self._db.cursor()
        query = "pragma table_info(%s)" % (self._table)

        return self.__execute(cur, query, fetch = DBMapper.FETCH_ALL)

    def __generate_structure(self):

        # use pragma constructs to get table into
        tblinfo = self.__get_table_info()

        # create the table if the statement does not exist
        if len(tblinfo) == 0:
            ins = zip(self._keys, self._keytypes)
            typarr = []
            for pair in ins:
                if pair[0] == self._primary:
                    # identifier type primary key
                    if self._autoincr_ind:
                        typarr.append("%s %s primary key autoincrement" % (pair[0], pair[1]))
                    else:
                        typarr.append("%s %s primary key" % (pair[0], pair[1]))
                elif pair[0] in self._unique_keys:
                    typarr.append("%s %s unique" % (pair[0], pair[1]))
                else:
                    # identifier type
                    typarr.append("%s %s" % (pair[0], pair[1]))
            cur = self._db.cursor()
            # create table if not exists <table> (<typarr>)
            query = "create table if not exists %s (%s)" % \
                (self._table, ', '.join(typarr))
            self.__execute(cur, query)

        # make sure table columns are up to date.
        if len(tblinfo) > 0:
            # use pragma table info to build database schema
            schema_ids = []
            schema_types = []
            for col in tblinfo:
                schema_ids.append(col[1])
                schema_types.append(col[2])
            # use schema to determine / apply database updates
            schema_updates = []
            for pair in zip(self._keys, self._keytypes):
                if pair[0] in schema_ids:
                    continue
                else:
                    schema_updates.append("%s %s" % (pair[0], pair[1]))
            for defn in schema_updates:
                query = "alter table %s add column %s" % (self._table, defn)
                cur = self._db.cursor()
                self.__execute(cur, query)

    def __generate_getters(self):

        for _key in self._keys:
            def getter_templ(self, __key = _key):
                if __key not in self._keys:
                    return
                cur = self._db.cursor()
                # select * from table where key=<key>
                query = "select %s from %s where %s=?" % (__key, self._table, self._primary)
                result = self.__execute(cur, query, args = (getattr(self, "_%s" % (self._primary)),))
                try: return result[0]
                except: return result
            setattr(self, "get_%s" % (_key), types.MethodType(getter_templ, self))

    def __generate_setters(self):

        for _key in self._keys:
            def setter_templ(self, value, __key = _key):
                if __key not in self._keys:
                    return
                cur = self._db.cursor()
                # update table set key=value where primary=id
                query = "update %s set %s=? where %s=?" % (
                    self._table, __key, self._primary)
                self.__execute(cur, query, args = (value, getattr(self, "_%s" % (self._primary)),))
                setattr(self, "_%s" % (__key), value)
            setattr(self, "set_%s" % (_key), types.MethodType(setter_templ, self))

    def __generate_properties(self):

        for _key in self._keys:
            setattr(self, "_%s" % (_key), None)
        
        for _key in self._keys:
            getf = getattr(self, "get_%s" % (_key))
            setf = getattr(self, "set_%s" % (_key))
            setattr(self, _key, property(getf, setf, None, "[%s] property"))

    def create(self):

        cur = self._db.cursor()
        vals = []
        for key in self._keys:
            if key == self._primary and self._autoincr_ind:
                vals.append(None) # Put None in for the index since it's going to be autoincr'd
            else:
                vals.append(getattr(self, "_%s" % (key)))
        qst = ', '.join(["?" for item in vals])
        query = "insert into %s values (%s)" % (self._table, qst)
        self.__execute(cur, query, args = vals)
        setattr(self, "_%s" % (self._primary), cur.lastrowid)

class DBResultList(list):

    def __init__(self, extend = None):

        if isinstance(extend, list):
            for item in extend:
                if isinstance(item, DBMapper):
                    self.append(item)
                else: continue

    def filter_equals(self, key, val):
        """ filter_equals(key, val) ->
              filters database find result based on
              key-value equality.
        """

        res = DBResultList()

        for dbo in self:
            try:
                if getattr(dbo, "_%s" % (key)) == val:
                    res.append(dbo)
                else: continue
            except: continue

        return res

    def filter_iequals(self, key, val):
        """ filter_iequals(key, val) ->
              filters database find result based on
              case insensitive key-value equality.
              assumes that db attribute and val are strings.
        """

        res = DBResultList()

        for dbo in self:
            try:
                if getattr(dbo, "_%s" % (key)).lower() == val.lower():
                    res.append(dbo)
                else: continue
            except: continue

        return res

    def filter_inequals(self, key, val):
        """ filter_inequals(key, val) ->
              filters database find result based on
              key-value inequality.
        """

        res = DBResultList()

        for dbo in self:
            try:
                if getattr(dbo, "_%s" % (key)) != val:
                    res.append(dbo)
                else: continue
            except: continue

        return res

    def filter_regex(self, key, regex):
        """ filter_regex(key, regex) ->
              filters database find result based on
              regex value matching.
        """

        res = DBResultList()

        for dbo in self:
            try:
                if re.match(regex, getattr(dbo, "_%s" % (key))) != None:
                    res.append(dbo)
                else: continue
            except: continue

        return res

class DBJoinResultList(list):

    def __init__(self, extend = None):

        if isinstance(extend, list):
            for item in extend:
                if isinstance(item, tuple):
                    self.append(item)
                else: continue

    def filter_equals(self, key, val):
        """ filter_equals(key, val) ->
              filters database join result based on
              key-value equality.
        """

        res = DBResultList()

        for dbpair in self:
            for dbo in dbpair:
                try:
                    if getattr(dbo, "_%s" % (key)) == val:
                        res.append(dbo)
                        break
                    else: continue
                except: continue

        return res

    def filter_iequals(self, key, val):
        """ filter_iequals(key, val) ->
              filters database join result based on
              case insensitive key-value equality.
              assumes that db attribute and val are strings.
        """

        res = DBResultList()

        for dbpair in self:
            for dbo in dbpair:
                try:
                    if getattr(dbo, "_%s" % (key)).lower() == val.lower():
                        res.append(dbo)
                        break
                    else: continue
                except: continue

        return res

    def filter_inequals(self, key, val):
        """ filter_inequals(key, val) ->
              filters database join result based on
              key-value inequality.
        """

        res = DBResultList()

        for dbpair in self:
            for dbo in dbpair:
                try:
                    if getattr(dbo, "_%s" % (key)) != val:
                        res.append(dbo)
                        break
                    else: continue
                except: continue

        return res

    def filter_regex(self, key, regex):
        """ filter_regex(key, regex) ->
              filters database find result based on
              regex value matching.
        """

        res = DBResultList()

        for dbpair in self:
            for dbo in dbpair:
                try:
                    if re.match(regex, getattr(dbo, "_%s" % (key))):
                        res.append(dbo)
                        break
                    else: continue
                except: continue

        return res
