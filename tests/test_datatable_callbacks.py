from typing import Any

import pytest
from sqlalchemy import Engine
from sqlalchemy.sql.selectable import FromClause

from datatables import DTDataCallbacks
from datatables.base import DTKey
from datatables.datatable import DataTable
from tests.fixtures import column_names
from tests.fixtures import create_query_params
from tests.fixtures import engine
from tests.fixtures import setup_db
from tests.fixtures import table


@pytest.fixture(scope='function', autouse=True)
def setup() -> None:
    assert setup_db is not None
    assert column_names is not None
    assert table is not None
    assert engine is not None


@pytest.fixture(scope='function')
def callbacks() -> DTDataCallbacks:
    callbacks: DTDataCallbacks = DTDataCallbacks()
    callbacks.set_row_id_getter(lambda row: f'row_{row["id"]}')  # noqa: Q001
    callbacks.set_row_class_getter(lambda row: str(row['color']))
    callbacks.set_row_attr_getter(lambda row: {'attribute': row['username'], 'attribute2': row['color']})
    callbacks.set_row_data_getter(
        lambda row: {'username': {'url': f'/actions/user/details/{row["username"]}'}}
    )  # noqa: Q001
    return callbacks


def test_datatable_callbacks(
    engine: Engine, column_names: list[str], table: FromClause, callbacks: DTDataCallbacks
) -> None:
    query_params: dict[str, Any] = create_query_params(column_names=column_names, start=0, length=1)
    datatable: DataTable = DataTable(
        request_params=query_params, engine=engine, column_names=column_names, table=table, callbacks=callbacks
    )
    output: dict[str, Any] | None = datatable.output_result()
    assert output is not None
    # test output params correspond to query params
    assert output['draw'] == int(query_params['draw'])
    assert output['start'] == int(query_params['start'])
    assert output['length'] == int(query_params['length'])
    # test that we get all results from the unfiltered query
    assert output['recordsTotal'] == 20
    assert output['recordsFiltered'] == 20

    data: list[dict[str, Any]] | None = output['data']
    assert data is not None
    assert len(data) == 1
    row: dict[str, Any] = data[0]
    assert row['id'] == 1
    assert row['username'] == 'spongebob'
    assert DTKey.ROW_ID in row
    assert DTKey.ROW_CLASS in row
    assert DTKey.ROW_ATTR in row
    assert DTKey.ROW_DATA in row
    assert row[DTKey.ROW_ID] == 'row_1'
    assert row[DTKey.ROW_CLASS] == row['color']
    assert row[DTKey.ROW_ATTR] == {'attribute': row['username'], 'attribute2': row['color']}
    assert row[DTKey.ROW_DATA] == {'username': {'url': f'/actions/user/details/{row["username"]}'}}  # noqa: Q001


if __name__ == '__main__':
    pytest.main()
