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


def test_datatable_global_search(engine: Engine, column_names: list[str], table: FromClause) -> None:
    query_params: dict[str, Any] = create_query_params(column_names=column_names, search='bikinibottom.org')
    datatable: DataTable = DataTable(
        request_params=query_params, engine=engine, column_names=column_names, table=table, callbacks=None
    )
    output: dict[str, Any] = datatable.output_result()
    # test that we get all results from the filtered query
    assert output['recordsTotal'] == 20
    assert output['recordsFiltered'] == 8
    data: list[dict[str, Any]] | None = output['data']
    assert data is not None
    # test that the number of records to reported number of filtered records
    matching_row_count: int = 0
    search_value = 'bikinibottom.org'
    assert len(data) == output['recordsFiltered']
    for row in data:
        for value in row.values():
            try:
                # default search is contains (like) not exact match
                str(value).index(search_value)
                matching_row_count += 1
                continue
            except ValueError:
                pass
    assert matching_row_count == output['recordsFiltered']


def test_datatable_column_search(engine: Engine, column_names: list[str], table: FromClause) -> None:
    query_params: dict[str, Any] = create_query_params(column_names=column_names)
    col_index: int = column_names.index('color')
    email_index: int = column_names.index('email_address')
    query_params[f'columns[{col_index}][search][value]'] = 'red'
    query_params[f'columns[{email_index}][search][value]'] = 'org'
    datatable: DataTable = DataTable(
        request_params=query_params, engine=engine, column_names=column_names, table=table, callbacks=None
    )
    output: dict[str, Any] | None = datatable.output_result()
    assert output is not None
    assert output['recordsTotal'] == 20
    assert output['recordsFiltered'] == 2
    data: list[dict[str, Any]] | None = output.get('data')
    assert data is not None
    for row in data:
        color: str = str(row.get('color'))
        email: str = str(row.get('email_address'))
        assert color.find('red') > -1
        assert email.find('org') > -1


# TODO implement user function for sqlite to enable REGEXP operator
# TODO Test REGEX True in global and column search

if __name__ == '__main__':
    pytest.main()
