import dataclasses as dc
import enum
import typing as t
from abc import ABC, abstractmethod, abstractproperty
from typing import Any

from superduperdb import logging
from superduperdb.base.document import Document
from superduperdb.base.serializable import Serializable, Variable
from superduperdb.components.datatype import DataType

GREEN = '\033[92m'
BOLD = '\033[1m'
END = '\033[0m'


class _ReprMixin(ABC):
    @abstractmethod
    def repr_(self) -> str:
        pass

    def __repr__(self) -> str:
        return (
            f'<{self.__class__.__module__}.{self.__class__.__name__}'
            f'[\n    {GREEN + BOLD}{self.repr_()}{END}\n] object at {hex(id(self))}>'
        )


def _check_illegal_attribute(name):
    # Disable Query class objects from using access special methods
    # Otherwise it will conflict with some python built-in methods, like copy
    if name.startswith("__") and name.endswith("__"):
        raise AttributeError(f"Attempt to access illegal attribute '{name}'")


# TODO: Remove unused code
@dc.dataclass(repr=False)
class model(Serializable):
    """Model.

    :param identifier: The identifier of the model.
    """

    identifier: str

    def predict_one(self, *args, **kwargs):
        """Predict one."""
        return PredictOne(model=self.identifier, args=args, kwargs=kwargs)

    def predict(self, *args, **kwargs):
        """Predict."""
        raise NotImplementedError


class Predict:
    """Base class for all prediction queries."""

    ...


@dc.dataclass(repr=False)
class PredictOne(Predict, Serializable, ABC):
    """A query to predict a single document.

    :param model: The model to use
    :param args: The arguments to pass to the model
    :param kwargs: The keyword arguments to pass to the model
    """

    model: str
    args: t.Sequence = dc.field(default_factory=list)
    kwargs: t.Dict = dc.field(default_factory=dict)

    def execute(self, db):
        """Execute the query.

        :param db: The datalayer instance
        """
        m = db.models[self.model]
        out = m.predict_one(*self.args, **self.kwargs)
        if isinstance(m.datatype, DataType):
            out = m.datatype(out)
        if isinstance(out, dict):
            out = Document(out)
        else:
            out = Document({'_base': out})
        return out


@dc.dataclass(repr=False)
class Select(Serializable, ABC):
    """Base class for all select queries."""

    @abstractproperty
    def id_field(self):
        """Return the primary id of the table."""
        pass

    @property
    def query_components(self):
        """Return the query components of the query."""
        return self.table_or_collection.query_components

    def model_update(
        self,
        db,
        ids: t.List[str],
        predict_id: str,
        outputs: t.Sequence[t.Any],
        **kwargs,
    ):
        """
        Update model outputs for a set of ids.

        :param db: The DB instance to use
        :param ids: The ids to update
        :param predict_id: The predict_id of the outputs
        :param outputs: The outputs to update
        """
        return self.table_or_collection.model_update(
            db=db,
            ids=ids,
            predict_id=predict_id,
            outputs=outputs,
            **kwargs,
        )

    @abstractproperty
    def select_table(self):
        """Return a select query for the table."""
        pass

    @abstractmethod
    def add_fold(self, fold: str) -> 'Select':
        """Add a fold to the query.

        :param fold: The fold to add
        """
        pass

    @abstractmethod
    def select_using_ids(self, ids: t.Sequence[str]) -> 'Select':
        """Return a query that selects only the given ids.

        :param ids: The ids to select
        """

    @abstractproperty
    def select_ids(self) -> 'Select':
        """Return a query that selects only the ids."""
        pass

    @abstractmethod
    def select_ids_of_missing_outputs(self, predict_id: str) -> 'Select':
        """Return a query that selects ids where outputs are missing.

        :param predict_id: The predict_id of the outputs
        """
        pass

    @abstractmethod
    def select_single_id(self, id: str) -> 'Select':
        """Return a query that selects a single id.

        :param id: The id to select
        """
        pass

    @abstractmethod
    def execute(self, db, reference: bool = True):
        """Execute the query on the DB instance.

        :param db: The datalayer instance
        :param reference: Whether to return a reference to the data
        """
        pass


@dc.dataclass(repr=False)
class Delete(Serializable, ABC):
    """
    Base class for all deletion queries.

    :param table_or_collection: The table or collection that this query is linked to
    """

    table_or_collection: 'TableOrCollection'
    args: t.Sequence = dc.field(default_factory=list)
    kwargs: t.Dict = dc.field(default_factory=dict)

    @abstractmethod
    def execute(self, db):
        """Execute the query.

        :param db: The datalayer instance
        """
        pass


@dc.dataclass(repr=False)
class Update(Serializable, ABC):
    """
    Base class for all update queries.

    :param table_or_collection: The table or collection that this query is linked to
    """

    table_or_collection: 'TableOrCollection'

    @abstractmethod
    def select_table(self):
        """Return a select query for the table."""
        pass

    @abstractmethod
    def execute(self, db):
        """Execute the query.

        :param db: The datalayer instance
        """
        pass


@dc.dataclass(repr=False)
class Write(Serializable, ABC):
    """
    Base class for all bulk write queries.

    :param table_or_collection: The table or collection that this query is linked to
    """

    table_or_collection: 'TableOrCollection'

    @abstractmethod
    def select_table(self):
        """Return a select query for the table."""
        pass

    @abstractmethod
    def execute(self, db):
        """Execute the query on the DB instance.

        :param db: The datalaer instance
        """
        pass


@dc.dataclass(repr=False)
class CompoundSelect(_ReprMixin, Select, ABC):
    """
    A query with multiple parts.

    like ----> select ----> like

    :param table_or_collection: The table or collection that this query is linked to
    :param pre_like: The pre_like part of the query (e.g. ``table.like(...)...``)
    :param post_like: The post_like part of the query
                      (e.g. ``table.filter(...)....like(...)``)
    :param query_linker: The query linker that is responsible for linking the
                         query chain. E.g. ``table.filter(...).select(...)``.
    """

    table_or_collection: 'TableOrCollection'
    pre_like: t.Optional['Like'] = None
    post_like: t.Optional['Like'] = None
    query_linker: t.Optional['QueryLinker'] = None

    @abstractproperty
    def output_fields(self):
        """Return the output fields of the query."""
        pass

    @property
    def id_field(self):
        """Return the primary id of the table."""
        return self.primary_id

    @property
    def primary_id(self):
        """Return the primary id of the table."""
        return self.table_or_collection.primary_id

    def add_fold(self, fold: str):
        """Add a fold to the query.

        :param fold: The fold to add
        """
        assert self.pre_like is None
        assert self.post_like is None
        assert self.query_linker is not None
        return self._query_from_parts(
            table_or_collection=self.table_or_collection,
            query_linker=self.query_linker.add_fold(fold),
        )

    @property
    def select_ids(self):
        """Query which selects the same documents/ rows but only ids."""
        assert self.pre_like is None
        assert self.post_like is None

        return self._query_from_parts(
            table_or_collection=self.table_or_collection,
            query_linker=self.query_linker.select_ids,
        )

    def select_ids_of_missing_outputs(self, predict_id: str):
        """Query which selects ids where outputs are missing.

        :param predict_id: The predict_id of the outputs
        """
        assert self.pre_like is None
        assert self.post_like is None
        assert self.query_linker is not None

        return self._query_from_parts(
            table_or_collection=self.table_or_collection,
            query_linker=self.query_linker._select_ids_of_missing_outputs(
                predict_id=predict_id
            ),
        )

    def select_single_id(self, id: str):
        """
        Query which selects a single id.

        :param id: The id to select.
        """
        assert self.pre_like is None
        assert self.post_like is None
        assert self.query_linker is not None

        return self._query_from_parts(
            table_or_collection=self.table_or_collection,
            query_linker=self.query_linker.select_single_id(id),
        )

    def select_using_ids(self, ids):
        """
        Subset a query to only these ids.

        :param ids: The ids to subset to.
        """
        assert self.pre_like is None
        assert self.post_like is None

        return self._query_from_parts(
            table_or_collection=self.table_or_collection,
            query_linker=self.query_linker.select_using_ids(ids),
        )

    def repr_(self):
        """String representation of the query."""
        components = []
        components.append(str(self.table_or_collection.identifier))
        if self.pre_like:
            components.append(str(self.pre_like))
        if self.query_linker:
            components.extend(self.query_linker.repr_().split('.')[1:])
        if self.post_like:
            components.append(str(self.post_like))
        return '.'.join(components)

    @classmethod
    def _query_from_parts(
        cls,
        table_or_collection,
        pre_like=None,
        post_like=None,
        query_linker=None,
    ):
        return cls(
            table_or_collection=table_or_collection,
            pre_like=pre_like,
            post_like=post_like,
            query_linker=query_linker,
        )

    def _get_query_component(
        self,
        name: str,
        type: str,
        args: t.Optional[t.Sequence] = None,
        kwargs: t.Optional[t.Dict] = None,
    ):
        query_component_cls = self.table_or_collection.query_components.get(
            name, QueryComponent
        )
        return query_component_cls(name, type=type, args=args, kwargs=kwargs)

    @abstractmethod
    def _get_query_linker(cls, table_or_collection, members) -> 'QueryLinker':
        pass

    def __getattr__(self, name):
        _check_illegal_attribute(name)
        assert self.post_like is None
        if self.query_linker is not None:
            query_linker = getattr(self.query_linker, name)
        else:
            query_linker = self._get_query_linker(
                self.table_or_collection,
                members=[self._get_query_component(name, type=QueryType.ATTR)],
            )
        return self._query_from_parts(
            table_or_collection=self.table_or_collection,
            pre_like=self.pre_like,
            query_linker=query_linker,
        )

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Add a query to the query chain."""
        assert self.post_like is None
        assert self.query_linker is not None
        return self._query_from_parts(
            table_or_collection=self.table_or_collection,
            pre_like=self.pre_like,
            query_linker=self.query_linker(*args, **kwargs),
        )

    @abstractmethod
    def execute(self, db, load_hybrid: bool = True):
        """
        Execute the compound query on the DB instance.

        :param db: The DB instance to use
        :param load_hybrid: Whether to load hybrid fields
        """

    def like(self, r: Document, vector_index: str, n: int = 10):
        """Return a query that performs a vector search.

        :param r: The document to search for
        :param vector_index: The vector index to use
        :param n: The number of results to return
        """
        assert self.query_linker is not None
        assert self.pre_like is None
        return self._query_from_parts(
            table_or_collection=self.table_or_collection,
            pre_like=None,
            query_linker=self.query_linker,
            post_like=Like(r=r, n=n, vector_index=vector_index),
        )


@dc.dataclass(repr=False)
class Insert(_ReprMixin, Serializable, ABC):
    """
    Base class for all insert queries.

    :param table_or_collection: The table or collection that this query is linked to
    :param documents: The documents to insert
    :param verbose: Whether to print the progress of the insert
    :param kwargs: Any additional keyword arguments to pass to the insert method
    """

    table_or_collection: 'TableOrCollection'
    documents: t.Sequence['Document'] = dc.field(default_factory=list)
    verbose: bool = True
    kwargs: t.Dict = dc.field(default_factory=dict)

    def repr_(self):
        """String representation of the query."""
        documents_str = (
            str(self.documents)[:25] + '...'
            if len(self.documents) > 25
            else str(self.documents)
        )
        return f'{self.table_or_collection.identifier}.insert_many({documents_str})'

    @abstractmethod
    def select_table(self):
        """Return a select query for the inserted documents."""
        pass

    @abstractmethod
    def execute(self, parent: t.Any):
        """
        Insert the data.

        :param parent: The parent instance to use for insertion
        """
        pass

    def to_select(self, ids=None):
        """Return a select query for the inserted documents.

        :param ids: The ids to select
        """
        if ids is None:
            ids = [r['_id'] for r in self.documents]
        return self.table.find({'_id': ids})


class QueryType(str, enum.Enum):
    """The type of a query. Either `query` or `attr`."""

    QUERY = 'query'
    ATTR = 'attr'


def _deep_flat_encode_impl(self, cache):
    import json
    import uuid

    out_str = []
    documents = {}
    for k in dc.fields(self):
        if k.name in {'name', 'type'}:
            continue
        if k.name == 'args':
            for arg in self.args:
                if isinstance(arg, Document):
                    id = uuid.uuid4().hex[:5].upper()
                    out_str.append(f'_documents[{id}]')
                    documents[id] = arg
                    continue
                out_str.append(json.dumps(arg).replace('"', "'"))
            continue
        if k.name == 'kwargs':
            for k, v in self.kwargs.items():
                if v is None:
                    continue
                if isinstance(v, Document):
                    id = uuid.uuid4().hex[:5].upper()
                    out_str.append(f'{k}=_documents[{id}]')
                    documents[id] = v
                else:
                    v = json.dumps(v).replace('"', "'")
                    out_str.append(f'{k}={v}')
            continue
        v = getattr(self, k.name)
        if v is None:
            continue
        if isinstance(v, Document):
            id = uuid.uuid4().hex[:5].upper()
            out_str.append(f'{k.name}=_documents[{id}]')
            documents[id] = v
        else:
            v = json.dumps(v).replace('"', "'")
            out_str.append(f'{k.name}={str(v)}')
    out_str = ', '.join(out_str)
    if hasattr(self, 'name'):
        return f'{self.name}({out_str})', documents
    else:
        return f'{self.__class__.__name__.lower()}({out_str})', documents


@dc.dataclass(repr=False)
class QueryComponent(Serializable):
    """QueryComponent is a representation of a query object in ibis query chain.

    This is used to build a query chain that can be executed on a database.
    Query will be executed in the order they are added to the chain.

    If we have a query chain like this:
        query = t.select(['id', 'name']).limit(10)
    here we have 2 query objects, `select` and `limit`.

    `select` will be wrapped with this class and added to the chain.

    :param name: The name of the query
    :param type: The type of the query, either `query` or `attr`
    :param args: The arguments to pass to the query
    :param kwargs: The keyword arguments to pass to the query
    :param _deep_flat_encode: The method to encode the query
    """

    name: str
    type: str = QueryType.ATTR
    args: t.Sequence = dc.field(default_factory=list)
    kwargs: t.Dict = dc.field(default_factory=dict)

    _deep_flat_encode = _deep_flat_encode_impl

    def repr_(self) -> str:
        """String representation of the query."""
        if self.type == QueryType.ATTR:
            return self.name

        def to_str(x):
            if isinstance(x, str):
                return f"'{x}'"
            elif isinstance(x, list):
                return f'[{", ".join([to_str(a) for a in x])}]'
            elif isinstance(x, dict):
                return str({k: to_str(v) for k, v in x.items()})
            elif isinstance(x, _ReprMixin):
                return x.repr_()
            else:
                return str(x)

        args_as_strs = [to_str(a) for a in self.args]
        args_as_strs += [f'{k}={to_str(v)}' for k, v in self.kwargs.items()]
        joined = ', '.join(args_as_strs)
        return f'{self.name}({joined})'

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Add a query to the query chain."""
        try:
            assert (
                self.type == QueryType.ATTR
            ), '__call__ method must be called on an attribute query'
        except AssertionError as e:
            logging.warn('QUERY_COMPONENT: ' + self.name)
            raise e
        return type(self)(
            name=self.name,
            type=QueryType.QUERY,
            args=args,
            kwargs=kwargs,
        )

    def execute(self, parent: t.Any):
        """Execute the query on the parent object.

        :param parent: The parent object to execute the query on.
        """
        if self.type == QueryType.ATTR:
            return getattr(parent, self.name)
        assert self.type == QueryType.QUERY
        parent = getattr(parent, self.name)(*self.args, **self.kwargs)
        return parent


@dc.dataclass(repr=False)
class QueryLinker(_ReprMixin, Serializable, ABC):
    """QueryLinker is a representation of a query chain.

    This class is responsible for linking together a query using
    `getattr` and `__call__`.

    This allows ``superduperdb`` to serialize queries from a range of APIs.
    Intuitively this allows us to do something like this:

    >>> collection.find({}).limit(10).sort('name')
    -->
    [
        ('<NAME>', <ARGS>, <KWARGS>),
        ('find', {}, None),
        ('limit', 10, None),
        ('sort', 'name', None),
    ]

    table.filter(t.select('id') == '1')

    :param table_or_collection: The table or collection that this query is linked to.
    :param members: The members of the query chain.
    """

    table_or_collection: 'TableOrCollection'
    members: t.List = dc.field(default_factory=list)

    @property
    def query_components(self):
        """Return the query components of the query chain."""
        return self.table_or_collection.query_components

    def repr_(self) -> str:
        """String representation of the query."""
        return (
            f'{self.table_or_collection.identifier}'
            + '.'
            + '.'.join([m.repr_() for m in self.members])
        )

    def _get_query_component(self, k):
        if k in self.query_components:
            return self.query_components[k](name=k, type=QueryType.ATTR)
        return QueryComponent(name=k, type=QueryType.ATTR)

    @classmethod
    def _get_query_linker(cls, table_or_collection, members):
        return cls(
            table_or_collection=table_or_collection,
            members=members,
        )

    def __getattr__(self, k):
        _check_illegal_attribute(k)
        return self._get_query_linker(
            self.table_or_collection,
            members=[*self.members, self._get_query_component(k)],
        )

    @property
    @abstractmethod
    def select_ids(self):
        """Return a query that selects only the ids.

        This is used to select only the ids of the documents.
        """
        pass

    @abstractmethod
    def select_single_id(self, id):
        """Return a query that selects a single id.

        :param id: The id to select
        """
        pass

    @abstractmethod
    def select_using_ids(self, ids):
        """Return a query that selects only the given ids.

        :param ids: The ids to select
        """
        pass

    def __call__(self, *args, **kwargs):
        """Add a query to the query chain."""
        members = [*self.members[:-1], self.members[-1](*args, **kwargs)]
        return type(self)(table_or_collection=self.table_or_collection, members=members)

    @abstractmethod
    def execute(self, db):
        """Execute the query.

        :param db: The datalayer instance
        """
        pass


@dc.dataclass
class Like(Serializable):
    """
    Base class for all like (vector-search) queries.

    :param r: The item to be converted to a vector, to search with.
    :param vector_index: The vector index to use
    :param n: The number of results to return
    :param _deep_flat_encode: The method to encode the query
    """

    r: t.Union[t.Dict, Document]
    vector_index: str
    n: int = 10

    _deep_flat_encode = _deep_flat_encode_impl

    def execute(self, db, ids: t.Optional[t.Sequence[str]] = None):
        """Execute the query.

        :param db: The datalayer instance
        :param ids: The ids to search for
        """
        return db.select_nearest(
            like=self.r,
            vector_index=self.vector_index,
            ids=ids,
            n=self.n,
        )


@dc.dataclass
class TableOrCollection(Serializable, ABC):
    """A base class for all tables and collections.

    Defines the interface for all tables and collections.

    :param identifier: The identifier of the table or collection.
    """

    query_components: t.ClassVar[t.Dict] = {}
    type_id: t.ClassVar[str] = 'table_or_collection'
    identifier: t.Union[str, Variable]

    @abstractmethod
    def _get_query_linker(self, members) -> QueryLinker:
        pass

    def _get_query_component(self, name: str) -> QueryComponent:
        return self.query_components.get(name, QueryComponent)(
            name=name, type=QueryType.ATTR
        )

    @abstractmethod
    def model_update(
        self,
        db,
        ids: t.List[t.Any],
        predict_id: str,
        outputs: t.Sequence[t.Any],
        flatten: bool = False,
        **kwargs,
    ):
        """Update model outputs for a set of ids.

        :param db: The datalayer instance
        :param ids: The ids to update
        :param predict_id: The predict_id of outputs
        :param outputs: The outputs to update
        :param flatten: Whether to flatten the output
        """
        pass

    @abstractmethod
    def insert(self, documents: t.Sequence[Document], **kwargs) -> Insert:
        """Return Insert query.

        :param documents: The documents to insert
        """
        pass

    @abstractmethod
    def _get_query(
        self,
        pre_like: t.Optional[Like] = None,
        query_linker: t.Optional[QueryLinker] = None,
        post_like: t.Optional[Like] = None,
    ) -> CompoundSelect:
        pass

    def __getattr__(self, k: str) -> 'CompoundSelect':
        # This method is responsible for dynamically creating a query chain,
        # which can be executed on a database. This is done by creating a
        # QueryLinker object, which is a representation of a query chain.
        # Under the hood, this is done by creating a QueryChain object, which
        # is a representation of a query chain.
        _check_illegal_attribute(k)
        query_linker = self._get_query_linker([self._get_query_component(k)])
        return self._get_query(query_linker=query_linker)

    def like(
        self,
        r: Document,
        vector_index: str,
        n: int = 10,
    ):
        """Return a query that performs a vector search.

        This method appends a query to the query chain where the query is repsonsible
        for performing a vector search on the parent query chain inputs.

        :param r: The vector to search for
        :param vector_index: The vector index to use
        :param n: The number of results to return
        """
        return self._get_query(
            pre_like=Like(
                r=r,
                n=n,
                vector_index=vector_index,
            ),
        )

    @abstractmethod
    def _insert(
        self,
        documents: t.Sequence[Document],
        *,
        refresh: bool = False,
        encoders: t.Sequence = (),
        verbose: bool = True,
        **kwargs,
    ):
        pass


@dc.dataclass
class RawQuery:
    """A raw query object.

    :param query: The raw query to execute.
    """

    query: t.Any

    @abstractmethod
    def execute(self, db):
        """A raw query method which executes the query and returns the result.

        :param db: The datalayer instance
        """
