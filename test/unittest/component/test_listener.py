import random
from test.db_config import DBConfig

import numpy as np
import pytest

from superduperdb import Document
from superduperdb.backends.ibis.query import Table, dtype
from superduperdb.backends.mongodb.query import Collection
from superduperdb.components.listener import Listener
from superduperdb.components.model import ObjectModel
from superduperdb.components.schema import Schema


def test_listener_serializes_properly():
    q = Collection("test").find({}, {})
    listener = Listener(
        model=ObjectModel("test", object=lambda x: x),
        select=q,
        key="test",
    )
    r = listener.dict().encode()

    # check that the result is JSON-able
    import json

    print(json.dumps(r, indent=2))


@pytest.mark.parametrize("db", [DBConfig.mongodb_empty], indirect=True)
def test_listener_chaining(db):
    collection = Collection("test")
    data = []

    def insert_random():
        for _ in range(5):
            y = int(random.random() > 0.5)
            x = int(random.random() > 0.5)
            data.append(
                Document(
                    {
                        "x": x,
                        "y": y,
                    }
                )
            )

        db.execute(collection.insert_many(data))

    # Insert data
    insert_random()

    m1 = ObjectModel(
        "m1", object=lambda x: x + 1, model_update_kwargs={"document_embedded": False}
    )
    m2 = ObjectModel("m2", object=lambda x: x + 2)

    listener1 = Listener(
        model=m1,
        select=collection.find({}),
        key="x",
        identifier="listener1",
    )

    listener2 = Listener(
        model=m2,
        select=Collection("_outputs.listener1::0").find(),
        key="_outputs.listener1::0",
        identifier="listener2",
    )

    db.add(listener1)
    db.add(listener2)

    docs = list(db.execute(Collection("_outputs.listener1::0").find({})))

    assert all("listener2::0" in r["_outputs"] for r in docs)

    insert_random()

    docs = list(db.execute(Collection("_outputs.listener1::0").find({})))

    assert all(["listener2::0" in d["_outputs"] for d in docs])


@pytest.mark.parametrize(
    "data",
    [
        1,
        "1",
        {"x": 1},
        [1],
        {
            "x": np.array([1]),
        },
        np.array([[1, 2, 3], [4, 5, 6]]),
    ],
)
@pytest.mark.parametrize("document_embedded", [True, False])
@pytest.mark.parametrize("flatten", [True, False])
@pytest.mark.parametrize("db", [DBConfig.mongodb_empty], indirect=True)
def test_create_output_dest_mongodb(db, data, flatten, document_embedded):
    collection = Collection("test")

    # Do not support flatten is True and document_embedded is True
    if flatten is True and document_embedded is True:
        return

    m1 = ObjectModel(
        "m1",
        object=lambda x: data if not flatten else [data],
        model_update_kwargs={"document_embedded": document_embedded},
        flatten=flatten,
    )
    db.execute(collection.insert_one(Document({"x": 1})))

    listener1 = Listener(
        model=m1,
        select=Collection("test").find({}),
        key="x",
        identifier="listener1",
    )

    db.add(listener1)
    doc = list(db.execute(listener1.outputs_select))[0]
    result = Document(doc.unpack(db))[listener1.outputs]
    assert isinstance(result, type(data))
    if isinstance(data, np.ndarray):
        assert np.allclose(result, data)
    else:
        assert result == data


@pytest.mark.parametrize(
    "data",
    [
        1,
        "1",
        {"x": 1},
        [1],
        {
            "x": np.array([1]),
        },
        np.array([[1, 2, 3], [4, 5, 6]]),
    ],
)
@pytest.mark.parametrize("flatten", [True, False])
@pytest.mark.parametrize("db", [DBConfig.sqldb_empty], indirect=True)
def test_create_output_dest_ibis(db, data, flatten):
    schema = Schema(
        identifier="test",
        fields={"x": dtype(int), "id": dtype(str)},
    )
    table = Table("test", schema=schema)
    db.apply(table)

    m1 = ObjectModel(
        "m1",
        object=lambda x: data if not flatten else [data],
        flatten=flatten,
    )
    db.execute(table.insert([Document({"x": 1, "id": "1"})]))

    listener1 = Listener(
        model=m1,
        select=table.to_query(),
        key="x",
        identifier="listener1",
    )

    db.add(listener1)
    doc = list(db.execute(listener1.outputs_select))[0]
    result = doc[listener1.outputs]
    if isinstance(data, np.ndarray):
        assert np.allclose(result, data)
    else:
        assert result == data
