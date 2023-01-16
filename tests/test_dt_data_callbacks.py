from typing import Any, Callable

import pytest

from datatables.base import DTDataCallbacks, DTKey


@pytest.fixture(scope='function')
def table_row() -> dict[str, Any]:
    return {'pk': 1, 'code': '8000.1', 'parent_code': '8000', 'name': 'foo'}


def test_dt_data_callbacks_no_params(table_row: dict[str, Any]) -> None:
    callbacks: DTDataCallbacks = DTDataCallbacks()
    assert callbacks is not None
    assert isinstance(callbacks, DTDataCallbacks)
    assert callbacks.get_row_id is None
    assert callbacks.get_row_class is None
    assert callbacks.get_row_data is None
    assert callbacks.get_row_attr is None
    callbacks.run(table_row)
    assert DTKey.ROW_ID not in table_row
    assert DTKey.ROW_CLASS not in table_row
    assert DTKey.ROW_DATA not in table_row
    assert DTKey.ROW_ATTR not in table_row


def test_dt_data_callbacks_set_row_id_getter(table_row: dict[str, Any]) -> None:
    getter = lambda row: row['pk']  # noqa: E731
    callbacks: DTDataCallbacks = DTDataCallbacks()
    callbacks.set_row_id_getter(getter=getter)
    assert callbacks.get_row_id is getter
    callbacks.run(table_row)
    assert DTKey.ROW_ID in table_row
    assert table_row.get(DTKey.ROW_ID) == table_row.get('pk')
    assert DTKey.ROW_CLASS not in table_row
    assert DTKey.ROW_DATA not in table_row
    assert DTKey.ROW_ATTR not in table_row


def test_dt_data_callbacks_set_row_class_getter(table_row: dict[str, Any]) -> None:
    row_class: str = 'dt_row_class'
    callbacks: DTDataCallbacks = DTDataCallbacks()
    getter = lambda row: row_class  # noqa: E731

    callbacks.set_row_class_getter(getter=getter)
    assert callbacks.get_row_class is getter
    callbacks.run(table_row)
    assert DTKey.ROW_ID not in table_row
    assert table_row.get(DTKey.ROW_CLASS) == row_class
    assert DTKey.ROW_DATA not in table_row
    assert DTKey.ROW_ATTR not in table_row


def test_dt_data_callbacks_set_row_attr_getter(table_row: dict[str, Any]) -> None:
    row_attrs: dict[str, Any] = {'attr_1': 'value_1', 'attr_2': 'value_2'}
    callbacks: DTDataCallbacks = DTDataCallbacks()
    getter: Callable[[dict[str, Any]], dict[str, Any]] = lambda row: row_attrs  # noqa: E731
    callbacks.set_row_attr_getter(getter=getter)
    assert callbacks.get_row_attr is getter
    callbacks.run(table_row)
    assert DTKey.ROW_ID not in table_row
    assert DTKey.ROW_CLASS not in table_row
    assert table_row.get(DTKey.ROW_ATTR) == row_attrs
    assert DTKey.ROW_DATA not in table_row


def test_dt_data_callbacks_set_row_data_getter(table_row: dict[str, Any]) -> None:
    row_data: dict[str, Any] = {
        'attr_1': {'links': {'url': 'foo/bar'}, 'name': 'bar', 'icon': 'fa-solid fa-page'},
        'attr_2': {'links': {'url': 'foo/elvis'}, 'name': 'rock', 'icon': 'fa-solid fa-star'},
    }
    callbacks: DTDataCallbacks = DTDataCallbacks()
    getter: Callable[[dict[str, Any]], dict[str, Any]] = lambda row: row_data  # noqa: E731
    callbacks.set_row_data_getter(getter=getter)
    assert callbacks.get_row_data is getter
    callbacks.run(table_row)
    assert DTKey.ROW_ID not in table_row
    assert DTKey.ROW_CLASS not in table_row
    assert DTKey.ROW_ATTR not in table_row
    assert table_row.get(DTKey.ROW_DATA) == row_data


def test_dt_data_callbacks_set_2_getters(table_row: dict[str, Any]) -> None:
    row_data: dict[str, Any] = {
        'attr_1': {'links': {'url': 'foo/bar'}, 'name': 'bar', 'icon': 'fa-solid fa-page'},
        'attr_2': {'links': {'url': 'foo/elvis'}, 'name': 'rock', 'icon': 'fa-solid fa-star'},
    }
    callbacks: DTDataCallbacks = DTDataCallbacks()
    id_getter: Callable[[dict[str, Any]], Any] = lambda row: row['pk']  # noqa: E731
    data_getter: Callable[[dict[str, Any]], dict[str, Any]] = lambda row: row_data  # noqa: E731

    callbacks.set_row_id_getter(id_getter)
    callbacks.set_row_data_getter(data_getter)
    callbacks.run(table_row)
    assert table_row.get(DTKey.ROW_ID) == table_row.get('pk')
    assert table_row.get(DTKey.ROW_DATA) == row_data


if __name__ == '__main__':
    pytest.main()
