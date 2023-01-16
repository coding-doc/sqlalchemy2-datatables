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


def test_datatable_single_column_order_desc(engine: Engine, column_names: list[str], table: FromClause) -> None:
    column_orders = [{'column': '0', 'dir': 'desc'}]
    query_params = create_query_params(column_names=column_names, order=column_orders)
    datatable: DataTable = DataTable(
        request_params=query_params, engine=engine, column_names=column_names, table=table, callbacks=None
    )
    output: dict[str, Any] | None = datatable.output_result()
    assert output is not None
    data: list[dict[str, Any]] | None = output.get('data')
    assert data is not None
    # test that the default sort order is ascending on the first columns
    for i in range(10, 1):
        assert i == data[i - 1].get('id')


def test_datatable_multi_column_orders(engine: Engine, column_names: list[str], table: FromClause) -> None:
    column_orders = [{'column': '4', 'dir': 'desc'}, {'column': '1', 'dir': 'desc'}]
    query_params = create_query_params(column_names=column_names, order=column_orders)
    datatable: DataTable = DataTable(
        request_params=query_params, engine=engine, column_names=column_names, table=table, callbacks=None
    )
    output: dict[str, Any] | None = datatable.output_result()
    assert output is not None
    data: list[dict[str, Any]] | None = output.get('data')
    assert data is not None
    # test that the 4th column (color) sort order is descending
    colors: list[str] | None = [row['color'] for row in data]
    assert colors is not None
    assert colors == sorted(colors, reverse=True)
    results: dict[str, list[str]] = {}
    for row in data:
        if row.get('color') in results:
            results[row['color']].append(row['username'])
        else:
            results[row['color']] = [row['username']]
    for username_list in results.values():
        assert username_list == sorted(username_list, reverse=True)


if __name__ == '__main__':
    pytest.main()
