from typing import Any

import pytest
from sqlalchemy import Engine, FromClause

from datatables.datatable import DataTable

from .fixtures import column_names, create_query_params, engine, setup_db, table


@pytest.fixture(scope='function', autouse=True)
def setup() -> None:
    assert setup_db is not None
    assert column_names is not None
    assert table is not None
    assert engine is not None


def test_datatable_columns(engine: Engine, column_names: list[str], table: FromClause) -> None:
    some_columns: list[str] = column_names[0:2]
    query_params: dict[str, Any] = create_query_params(column_names=some_columns, start=0, length=1)
    datatable: DataTable = DataTable(
        request_params=query_params, engine=engine, column_names=some_columns, table=table, callbacks=None
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
    assert data is not None
    assert len(data) == 1
    row: dict[str, Any] = data[0]
    assert len(some_columns) == len(row)
    for col in some_columns:
        assert col in row


def test_datatable_columns_error(engine: Engine, column_names: list[str], table: FromClause) -> None:
    some_columns: list[str] = column_names[0:2]
    some_columns.append('non_exisiting_column')
    query_params: dict[str, Any] = create_query_params(column_names=some_columns, start=0, length=1)
    datatable: DataTable = DataTable(
        request_params=query_params, engine=engine, column_names=some_columns, table=table, callbacks=None
    )
    output: dict[str, Any] | None = datatable.output_result()
    assert output is not None
    assert 'error' in output


if __name__ == '__main__':
    pytest.main()
