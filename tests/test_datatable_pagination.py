from typing import Any

import pytest
from sqlalchemy import Engine, FromClause

from datatables.datatable import DataTable

from .fixtures import column_names, create_query_params, engine, setup_db, table, users


@pytest.fixture(scope='function', autouse=True)
def setup() -> None:
    assert setup_db is not None
    assert column_names is not None
    assert table is not None
    assert engine is not None


def test_datatable(engine: Engine, column_names: list[str], table: FromClause) -> None:
    query_params: dict[str, Any] = create_query_params(column_names=column_names)
    datatable: DataTable = DataTable(
        request_params=query_params, engine=engine, column_names=column_names, table=table, callbacks=None
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
    # test that the number of records corresponds to requested length
    assert len(data) == int(query_params['length'])
    # test that the correct page is returned
    assert data[0]['id'] == 1 + int(query_params['start'])
    # test that the columns returned correspond to the requested columns
    assert list(data[0].keys()) == column_names
    # test that the values are keyd to the correct column name
    test_user: dict[str, Any] = data[0]
    control_user: dict[str, Any] = users[test_user['username']]
    for col in column_names:
        if col == 'id':  # user dictionary has no id before being save int the database
            continue
        assert test_user.get(col) == control_user.get(col)
    # test that the default sort order is ascending on the first columns
    for i in range(1, 10):
        assert i == data[i - 1].get('id')


def test_datatable_second_page(engine: Engine, column_names: list[str], table: FromClause) -> None:
    query_params: dict[str, Any] = create_query_params(column_names=column_names, start=10)
    datatable: DataTable = DataTable(
        request_params=query_params, engine=engine, column_names=column_names, table=table, callbacks=None
    )
    output: dict[str, Any] = datatable.output_result()
    # test that we get all results from the filtered query
    assert output['start'] == 10
    assert output['length'] == 10
    assert output['recordsTotal'] == 20
    assert output['recordsFiltered'] == 20
    data: list[dict[str, Any]] = output['data']
    # test that the number of records corresponds to requested length
    assert len(data) == int(query_params['length'])
    # test that the correct page is returned
    assert data[0]['id'] == 1 + int(query_params['start'])


def test_datatable_page_size(engine: Engine, column_names: list[str], table: FromClause) -> None:
    query_params: dict[str, Any] = create_query_params(column_names=column_names, start=15, length=5)
    datatable: DataTable = DataTable(
        request_params=query_params, engine=engine, column_names=column_names, table=table, callbacks=None
    )
    output: dict[str, Any] = datatable.output_result()
    # test that we get all results from the filtered query
    assert output['start'] == 15
    assert output['length'] == 5
    assert output['recordsTotal'] == 20
    assert output['recordsFiltered'] == 20
    data: list[dict[str, Any]] = output['data']
    # test that the number of records corresponds to requested length
    assert len(data) == int(query_params['length'])
    # test that the correct page is returned
    assert data[0]['id'] == 1 + int(query_params['start'])


if __name__ == '__main__':
    pytest.main()
