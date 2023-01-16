import pytest

from datatables.base import DTColumn


def test_dt_column_new() -> None:
    column: DTColumn = DTColumn(
        index=0, data='pk', name='pk', searchable=True, orderable=True, search_value='', search_regex=False
    )

    assert column is not None
    assert isinstance(column, DTColumn)
    assert column.index == 0
    assert column.data == 'pk'
    assert column.name == 'pk'
    assert column.searchable is True
    assert column.orderable is True
    assert column.search_value == ''
    assert column.search_regex is False


def test_dt_column_no_param() -> None:
    column: DTColumn = DTColumn()
    assert column.index == -1
    assert column.data == ''
    assert column.name == ''
    assert column.searchable is True
    assert column.orderable is True
    assert column.search_value == ''
    assert column.search_regex is False


def test_dt_column_string_args() -> None:
    column: DTColumn = DTColumn(index='5', searchable='false', orderable='false', search_regex='true')
    assert column.index == 5
    assert column.searchable is False
    assert column.orderable is False
    assert column.search_regex is True


if __name__ == '__main__':
    pytest.main()
