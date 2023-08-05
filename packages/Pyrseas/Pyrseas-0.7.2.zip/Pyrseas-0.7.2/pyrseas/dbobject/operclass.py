# -*- coding: utf-8 -*-
"""
    pyrseas.dbobject.operclass
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module defines two classes: OperatorClass derived from
    DbSchemaObject and OperatorClassDict derived from DbObjectDict.
"""
from pyrseas.dbobject import DbObjectDict, DbSchemaObject
from pyrseas.dbobject import commentable, ownable


class OperatorClass(DbSchemaObject):
    """An operator class"""

    keylist = ['schema', 'name', 'index_method']
    objtype = "OPERATOR CLASS"
    single_extern_file = True

    def extern_key(self):
        """Return the key to be used in external maps for this operator

        :return: string
        """
        return '%s %s using %s' % (self.objtype.lower(), self.name,
                                   self.index_method)

    def identifier(self):
        """Return a full identifier for an operator class

        :return: string
        """
        return "%s USING %s" % (self.qualname(), self.index_method)

    def to_map(self, no_owner):
        """Convert operator class to a YAML-suitable format

        :return: dictionary
        """
        dct = self._base_map(no_owner)
        if self.name == self.family:
            del dct['family']
        return dct

    @commentable
    @ownable
    def create(self):
        """Return SQL statements to CREATE the operator class

        :return: SQL statements
        """
        dflt = ''
        if hasattr(self, 'default') and self.default:
            dflt = "DEFAULT "
        clauses = []
        for (strat, oper) in list(self.operators.items()):
            clauses.append("OPERATOR %d %s" % (strat, oper))
        for (supp, func) in list(self.functions.items()):
            clauses.append("FUNCTION %d %s" % (supp, func))
        if hasattr(self, 'storage'):
            clauses.append("STORAGE %s" % self.storage)
        return ["CREATE OPERATOR CLASS %s\n    %sFOR TYPE %s USING %s "
                "AS\n    %s" % (
                self.qualname(), dflt, self.type, self.index_method,
                ',\n    ' .join(clauses))]


class OperatorClassDict(DbObjectDict):
    "The collection of operator classes in a database"

    cls = OperatorClass
    query = \
        """SELECT nspname AS schema, opcname AS name, rolname AS owner,
                  amname AS index_method, opfname AS family,
                  opcintype::regtype AS type, opcdefault AS default,
                  opckeytype::regtype AS storage,
                  obj_description(o.oid, 'pg_opclass') AS description
           FROM pg_opclass o JOIN pg_am a ON (opcmethod = a.oid)
                JOIN pg_roles r ON (r.oid = opcowner)
                JOIN pg_opfamily f ON (opcfamily = f.oid)
                JOIN pg_namespace n ON (opcnamespace = n.oid)
           WHERE (nspname != 'pg_catalog' AND nspname != 'information_schema')
             AND o.oid NOT IN (
                 SELECT objid FROM pg_depend WHERE deptype = 'e'
                              AND classid = 'pg_opclass'::regclass)
           ORDER BY nspname, opcname, amname"""

    opquery = \
        """SELECT nspname AS schema, opcname AS name, amname AS index_method,
                  amopstrategy AS strategy, amopopr::regoperator AS operator
           FROM pg_opclass o JOIN pg_am a ON (opcmethod = a.oid)
                JOIN pg_namespace n ON (opcnamespace = n.oid), pg_amop ao,
                pg_depend
           WHERE refclassid = 'pg_opclass'::regclass
             AND classid = 'pg_amop'::regclass AND objid = ao.oid
             AND refobjid = o.oid
             AND (nspname != 'pg_catalog' AND nspname != 'information_schema')
             AND o.oid NOT IN (
                 SELECT objid FROM pg_depend WHERE deptype = 'e'
                              AND classid = 'pg_opclass'::regclass)
           ORDER BY nspname, opcname, amname, amopstrategy"""

    prquery = \
        """SELECT nspname AS schema, opcname AS name, amname AS index_method,
                  amprocnum AS support, amproc::regprocedure AS function
           FROM pg_opclass o JOIN pg_am a ON (opcmethod = a.oid)
                JOIN pg_namespace n ON (opcnamespace = n.oid), pg_amproc ap,
                pg_depend
           WHERE refclassid = 'pg_opclass'::regclass
             AND classid = 'pg_amproc'::regclass AND objid = ap.oid
             AND refobjid = o.oid
             AND (nspname != 'pg_catalog' AND nspname != 'information_schema')
             AND o.oid NOT IN (
                 SELECT objid FROM pg_depend WHERE deptype = 'e'
                              AND classid = 'pg_opclass'::regclass)
           ORDER BY nspname, opcname, amname, amprocnum"""

    def _from_catalog(self):
        """Initialize the dictionary of operator classes from the catalogs"""
        for opclass in self.fetch():
            if opclass.storage == '-':
                del opclass.storage
            self[opclass.key()] = OperatorClass(**opclass.__dict__)
        opers = self.dbconn.fetchall(self.opquery)
        self.dbconn.rollback()
        for (sch, opc, idx, strat, oper) in opers:
            opcls = self[(sch, opc, idx)]
            if not hasattr(opcls, 'operators'):
                opcls.operators = {}
            opcls.operators.update({strat: oper})
        funcs = self.dbconn.fetchall(self.prquery)
        self.dbconn.rollback()
        for (sch, opc, idx, supp, func) in funcs:
            opcls = self[(sch, opc, idx)]
            if not hasattr(opcls, 'functions'):
                opcls.functions = {}
            opcls.functions.update({supp: func})

    def from_map(self, schema, inopcls):
        """Initalize the dictionary of operator classes from the input map

        :param schema: schema owning the operator classes
        :param inopcls: YAML map defining the operator classes
        """
        for key in inopcls:
            if not key.startswith('operator class ') or not ' using ' in key:
                raise KeyError("Unrecognized object type: %s" % key)
            pos = key.rfind(' using ')
            opc = key[15:pos]  # 15 = len('operator class ')
            idx = key[pos + 7:]  # 7 = len(' using ')
            inopcl = inopcls[key]
            self[(schema.name, opc, idx)] = opclass = OperatorClass(
                schema=schema.name, name=opc, index_method=idx)
            if not inopcl:
                raise ValueError("Operator '%s' has no specification" % opc)
            for attr, val in list(inopcl.items()):
                setattr(opclass, attr, val)
            if 'oldname' in inopcl:
                opclass.oldname = inopcl['oldname']
            if 'description' in inopcl:
                opclass.description = inopcl['description']

    def diff_map(self, inopcls):
        """Generate SQL to transform existing operator classes

        :param inopcls: a YAML map defining the new operator classes
        :return: list of SQL statements

        Compares the existing operator class definitions, as fetched
        from the catalogs, to the input map and generates SQL
        statements to transform the operator classes accordingly.
        """
        stmts = []
        # check input operator classes
        for (sch, opc, idx) in inopcls:
            inoper = inopcls[(sch, opc, idx)]
            # does it exist in the database?
            if (sch, opc, idx) not in self:
                if not hasattr(inoper, 'oldname'):
                    # create new operator
                    stmts.append(inoper.create())
                else:
                    stmts.append(self[(sch, opc, idx)].rename(inoper))
            else:
                # check operator objects
                stmts.append(self[(sch, opc, idx)].diff_map(inoper))

        # check existing operators
        for (sch, opc, idx) in self:
            oper = self[(sch, opc, idx)]
            # if missing, mark it for dropping
            if (sch, opc, idx) not in inopcls:
                oper.dropped = False

        return stmts

    def _drop(self):
        """Actually drop the operator classes

        :return: SQL statements
        """
        stmts = []
        for (sch, opc, idx) in self:
            oper = self[(sch, opc, idx)]
            if hasattr(oper, 'dropped'):
                stmts.append(oper.drop())
        return stmts
