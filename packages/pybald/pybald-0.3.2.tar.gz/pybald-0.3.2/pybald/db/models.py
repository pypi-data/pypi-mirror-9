from sqlalchemy import dialects

# load sqlalchemy modules proxied through the models object
# this is mostly for convenience
from sqlalchemy import (
    MetaData,
    INT as Int,
    Integer,
    Float,
    Column,
    UniqueConstraint,
    Index,
    ForeignKey,
    String,
    DateTime,
    TIMESTAMP as TimeStamp,
    PickleType,
    Time,
    Table,
    or_,
    and_,
    not_,
    select
    )

from sqlalchemy.types import (
    BLOB,
    BOOLEAN,
    BigInteger,
    Binary,
    Boolean,
    CHAR,
    CLOB,
    DATE,
    DATETIME,
    DECIMAL,
    Date,
    DateTime,
    Enum,
    FLOAT,
    Float,
    INT,
    INTEGER,
    Integer,
    Interval,
    LargeBinary,
    NCHAR,
    NVARCHAR,
    NUMERIC,
    Numeric,
    PickleType,
    SMALLINT,
    SmallInteger,
    String,
    TEXT,
    TIME,
    TIMESTAMP,
    Text,
    Time,
    TypeDecorator,
    Unicode,
    UnicodeText,
    VARCHAR,
    )


from sqlalchemy.orm import (
    column_property,
    mapper,
    scoped_session,
    sessionmaker,
    reconstructor,
    relationship,
    backref,
    contains_eager,
    eagerload,
    eagerload_all,
    joinedload,
    synonym,
    object_session
    )

from sqlalchemy.orm.attributes import (
    instance_state
    )

from sqlalchemy.orm.util import (
    has_identity
)

from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound
    )

from sqlalchemy.exc import (
    IntegrityError
    )

from sqlalchemy.sql import (
    exists,
    )

from sqlalchemy.sql.expression import (
    asc,
    case,
    desc,
    literal,
    literal_column,
    null
    )

from sqlalchemy.ext.hybrid import (
                    hybrid_property,
                    hybrid_method
    )

from sqlalchemy import func

import json
import pickle
import zlib
from pybald.db import engine, dump_engine
from pybald.util import camel_to_underscore, pluralize

import project
# from project import mc

# from sqlalchemy.orm.interfaces import SessionExtension
from sqlalchemy.ext.mutable import Mutable

from sqlalchemy import __version__ as sa_ver

sa_maj_ver, sa_min_ver, sa_rev_ver = sa_ver.split(".")

if int(sa_min_ver) >= 7:
    from sqlalchemy.orm.attributes import flag_modified
else:
    from sqlalchemy.orm.attributes import instance_dict, NO_VALUE

    def flag_modified(instance, key):
        state, dict_ = instance_state(instance), instance_dict(instance)
        impl = state.manager[key].impl
        state.modified_event(dict_, impl, True, NO_VALUE)


session_args = {}

if project.green:
    from SAGreen import eventlet_greenthread_scope
    session_args['scopefunc'] = eventlet_greenthread_scope

session = scoped_session(sessionmaker(bind=engine, **session_args))

import sqlalchemy.ext.declarative
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base(bind=engine)


# # lifted from zzzeek's post on "Magic ORM"
# # this only works for SA 7, due to the
# # use of the event system.
# # Source: http://techspot.zzzeek.org/2011/05/17/magic-a-new-orm/
# # Copyright (I assume) Michael Bayer
# # =====================================
# from sqlalchemy.orm import (
#             class_mapper, mapper, relationship,
#             scoped_session, sessionmaker, configure_mappers
#         )
# from sqlalchemy.ext.declarative import declared_attr, declarative_base
# from sqlalchemy import event
# import re
#
# @event.listens_for(mapper, "mapper_configured")
# def _setup_deferred_properties(mapper, class_):
#     """Listen for finished mappers and apply DeferredProp
#     configurations."""
#
#     for key, value in class_.__dict__.items():
#         if isinstance(value, DeferredProp):
#             value._config(class_, key)
#
# class DeferredProp(object):
#     """A class attribute that generates a mapped attribute
#     after mappers are configured."""
#
#     def _setup_reverse(self, key, rel, target_cls):
#         """Setup bidirectional behavior between two relationships."""
#
#         reverse = self.kw.get('reverse')
#         if reverse:
#             reverse_attr = getattr(target_cls, reverse)
#             if not isinstance(reverse_attr, DeferredProp):
#                 reverse_attr.property._add_reverse_property(key)
#                 rel._add_reverse_property(reverse)
#
# class FKRelationship(DeferredProp):
#     """Generates a one to many or many to one relationship."""
#
#     def __init__(self, target, fk_col, **kw):
#         self.target = target
#         self.fk_col = fk_col
#         self.kw = kw
#
#     def _config(self, cls, key):
#         """Create a Column with ForeignKey as well as a relationship()."""
#
#         target_cls = cls._decl_class_registry[self.target]
#
#         pk_target, fk_target = self._get_pk_fk(cls, target_cls)
#         pk_table = pk_target.__table__
#         pk_col = list(pk_table.primary_key)[0]
#
#         if hasattr(fk_target, self.fk_col):
#             fk_col = getattr(fk_target, self.fk_col)
#         else:
#             fk_col = Column(self.fk_col, pk_col.type, ForeignKey(pk_col))
#             setattr(fk_target, self.fk_col, fk_col)
#
#         rel = relationship(target_cls,
#                 primaryjoin=fk_col==pk_col,
#                 collection_class=self.kw.get('collection_class', set)
#             )
#         setattr(cls, key, rel)
#         self._setup_reverse(key, rel, target_cls)
#
# class one_to_many(FKRelationship):
#     """Generates a one to many relationship."""
#
#     def _get_pk_fk(self, cls, target_cls):
#         return cls, target_cls
#
# class many_to_one(FKRelationship):
#     """Generates a many to one relationship."""
#
#     def _get_pk_fk(self, cls, target_cls):
#         return target_cls, cls
#
# class many_to_many(DeferredProp):
#     """Generates a many to many relationship."""
#
#     def __init__(self, target, tablename, local, remote, **kw):
#         self.target = target
#         self.tablename = tablename
#         self.local = local
#         self.remote = remote
#         self.kw = kw
#
#     def _config(self, cls, key):
#         """Create an association table between parent/target
#         as well as a relationship()."""
#
#         target_cls = cls._decl_class_registry[self.target]
#         local_pk = list(cls.__table__.primary_key)[0]
#         target_pk = list(target_cls.__table__.primary_key)[0]
#
#         t = Table(
#                 self.tablename,
#                 cls.metadata,
#                 Column(self.local, ForeignKey(local_pk), primary_key=True),
#                 Column(self.remote, ForeignKey(target_pk), primary_key=True),
#                 keep_existing=True
#             )
#         rel = relationship(target_cls,
#                 secondary=t,
#                 collection_class=self.kw.get('collection_class', set)
#             )
#         setattr(cls, key, rel)
#         self._setup_reverse(key, rel, target_cls)
#
# # =====================================
# # end of zzzeek's code for "Magic" ORM
# # =====================================
class ASCII(TypeDecorator):
    '''
    A database string type that only allows ASCII characters.

    This is a data type check since all strings in the database could
    be unicode.
    '''
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        '''
        Run encode on a unicode string to make sure the string only
        contains ASCII characterset characters. To avoid another conversion
        pass, the original unicode value is passed to the underlying db.
        '''
        # run an encode on the value with ascii to see if it contains
        # non ascii. Ignore the return value because we only want to throw
        # an exception if the encode fails. The data can stay unicode for
        # insertion into the db.
        if value is not None:
            value.encode('ascii')
        return value

    def process_result_value(self, value, dialect):
        '''
        Run encode on a unicode string coming out of the database to turn the
        unicode string back into an encoded python bytestring.
        '''
        if isinstance(value, unicode):
            value = value.encode('ascii')
        return value


class JSONEncodedDict(TypeDecorator):
    '''
    Represents a dictionary as a json-encoded string in the database.
    '''
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        '''
        Turn a dictionary into a JSON encoded string on the way into
        the database.
        '''
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        '''
        Turn a JSON encoded string into a dictionary on the way out
        of the database.
        '''
        if value is not None:
            value = json.loads(value)
        return value


class ZipPickler(object):
    '''Simple wrapper for pickle that auto compresses/decompresses values'''
    def loads(self, string):
        return pickle.loads(zlib.decompress(string))

    def dumps(self, obj, protocol):
        return zlib.compress(pickle.dumps(obj, protocol))


class MutationDict(Mutable, dict):
    '''
    A dictionary that automatically emits change events for SQA
    change tracking.

    Lifted almost verbatim from the SQA docs.
    '''
    @classmethod
    def coerce(cls, key, value):
        "Convert plain dictionaries to MutationDict."
        if not isinstance(value, MutationDict):
            if isinstance(value, dict):
                return MutationDict(value)
            # this call will raise ValueError
            return Mutable.coerce(key, value)
        else:
            return value

    def update(self, *args, **kwargs):
        '''
        Updates the current dictionary with kargs or a passed in dict.
        Calls the internal setitem for the update method to maintain
        mutation tracking.
        '''
        for k, v in dict(*args, **kwargs).iteritems():
            self[k] = v

    def __setitem__(self, key, value):
        "Detect dictionary set events and emit change events."
        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        "Detect dictionary del events and emit change events."
        dict.__delitem__(self, key)
        self.changed()

    def __getstate__(self):
        '''Get state returns a plain dictionary for pickling purposes.'''
        return dict(self)

    def __setstate__(self, state):
        '''
        Set state assumes a plain dictionary and then re-constitutes a
        Mutable dict.
        '''
        self.update(state)


class NotFound(NoResultFound):
    '''Generic Not Found Error'''
    pass


surrogate_pk_template = Column(Integer, nullable=False, primary_key=True)


class ModelMeta(sqlalchemy.ext.declarative.DeclarativeMeta):
    '''
    MetaClass that sets up some common behaviors for pybald models.

    Will assign tablename if not defined based on pluralization rules. Also
    applies project global table arguments. Lastly this will assign a
    numeric primary key id to the table if no primary key was defined
    in the model class.
    '''
    def __init__(cls, name, bases, ns):
        try:
            if Model not in bases:
                # Allow for inheritance of the Model object
                # for use with SqlAlchemy inheritance patterns
                super(ModelMeta, cls).__init__(name, bases, ns)
                return
        except NameError:
            # if this is the Model class, then just return
            return

        # set the tablename, if it's user set, use that, otherwise use a
        # function to create one
        cls.__tablename__ = getattr(cls, "__tablename__",
                                    pluralize(camel_to_underscore(name)))
        # tableargs adds autoload to create schema reflection
        cls.__table_args__ = getattr(cls, "__table_args__", {})

        if project.schema_reflection:
            # create or update the __table_args__ attribute
            cls.__table_args__['autoload'] = True
        if project.global_table_args:
            cls.__table_args__.update(project.global_table_args)

        # check if the class has at least one primary key
        # if not, automatically generate one.
        has_primary = any([False] + [value.primary_key
                                     for value in cls.__dict__.values()
                                     if isinstance(value, Column)])
        if not has_primary:
            # treat the id as a mixin w/copy
            surrogate_pk = surrogate_pk_template.copy()
            surrogate_pk._creation_order = surrogate_pk_template._creation_order
            cls.id = surrogate_pk
        super(ModelMeta, cls).__init__(name, bases, ns)


class RegistryMount(type):
    '''
    A registry creating metaclass that keeps track of all defined classes that
    inherit from a base class using this metaclass.
    '''
    # lifted almost verbatim from: http://martyalchin.com/2008/jan/10/simple-plugin-framework/
    def __init__(cls, name, bases, attrs):
        try:
            cls.registry.append(cls)
        except AttributeError:
            # this is processing the first class (the mount point)
            cls.registry = []

        return super(RegistryMount, cls).__init__(name, bases, attrs)


class RegistryModelMeta(RegistryMount, ModelMeta):
    pass


class Model(Base):
    '''Pybald Model class, inherits from SQLAlchemy Declarative Base.'''
    __metaclass__ = RegistryModelMeta

    NotFound = sqlalchemy.orm.exc.NoResultFound
    MultipleFound = sqlalchemy.orm.exc.MultipleResultsFound

    def is_modified(self):
        '''Check if SQLAlchemy believes this instance is modified.'''
        # TODO: Using this internal flag, is this a private internal
        # behavior? Is there a better, public-api way of getting this info?
        # alternatively is session.is_modified(self) although will this fail
        # if the instance isn't part of the session?
        return instance_state(self).modified

    def clear_modified(self):
        '''
        Unconditionally clear all modified state from the attibutes on
        this instance.
        '''
        # Uses this method: http://www.sqlalchemy.org/docs/orm/internals.html?highlight=commit_all#sqlalchemy.orm.state.InstanceState.commit_all
        if int(sa_min_ver) > 7:
            # the methods became private in SA 8, need to check if
            # this is a problem
            return instance_state(self)._commit_all({})
        else:
            return instance_state(self).commit_all({})

    def is_persisted(self):
        '''
        Check if this instance has ever been persisted. Means it is either
        `detached` or `persistent`.
        '''
        return has_identity(self)

    def save(self, flush=False):
        '''
        Saves (adds) this instance in the current databse session.

        This does not immediatly persist the data since these operations
        occur within a transaction and the sqlalchemy unit-of-work pattern.
        If something causes a rollback before the session is committed,
        these changes will be lost.

        When flush is `True`, flushes the data to the database immediately
        **within the same transaction**. This does not commit the transaction,
        for that use :py:meth:`~pybald.db.models.Model.commit`)
        '''

        session.add(self)

        if flush:
            self.flush()
        return self

    def delete(self, flush=False):
        '''
        Delete this instance from the current database session.

        The object will be deleted from the database at the next commit. If
        you want to immediately delete the object, you should follow this
        operation with a commit to emit the SQL to delete the item from
        the database and commit the transaction.
        '''
        session.delete(self)
        if flush:
            self.flush()
        return self

    def flush(self):
        '''
        Syncs all pending SQL changes (including other pending objects) to
        the underlying data store within the current transaction.

        Flush emits all the relevant SQL to the underlying store, but does
        **not** commit the current transaction or close the current
        database session.
        '''
        session.flush()
        return self

    def commit(self):
        '''
        Commits the entire database session (including other pending objects).

        This emits all relevant SQL to the databse, commits the current
        transaction, and closes the current session (and database connection)
        and returns it to the connection pool. Any data operations after this
        will pull a new database session from the connection pool.
        '''
        session.commit()
        return self

    @classmethod
    def get(cls, **where):
        '''
        A convenience method that constructs a load query with keyword
        arguments as the filter arguments and return a single instance.
        '''
        return cls.load(**where).one()

    @classmethod
    def all(cls, **where):
        '''
        Returns a collection of objects that can be filtered for
        specific collections.

        all() without arguments returns all the items of the model type.
        '''
        return cls.load(**where).all()

    # methods that return queries (must execute to retrieve)
    # =============================================================
    @classmethod
    def load(cls, **where):
        '''
        Convenience method to build a sqlalchemy query to return stored
        objects.

        Returns a query object. This query object must be executed to retrieve
        actual items from the database.
        '''
        if where:
            return session.query(cls).filter_by(**where)
        else:
            return session.query(cls)

    @classmethod
    def filter(cls, *pargs, **kargs):
        '''
        Convenience method that auto-builds the query and passes the filter
        to it.

        Returns a query object.
        '''
        return session.query(cls).filter(*pargs, **kargs)

    @classmethod
    def query(cls):
        '''
        Convenience method to return a query based on the current object
        class.
        '''
        return session.query(cls)

    @classmethod
    def show_create_table(cls):
        '''
        Uses the simple dump_engine to print to stdout the SQL for this
        table.
        '''
        cls.__table__.create(dump_engine)


class NonDbModel(object):
    '''
    A plain Python object that uses the RegistryMount system to register
    non database models. Inheriting from this allows the object to be registered
    as a Model.
    '''
    __metaclass__ = RegistryMount
    # use the same registry space for NonDbModels
    registry = Model.registry
