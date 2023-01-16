import pytest

from datatables.base import DTColumnOrder


def test_dt_column_order_new() -> None:
    order: DTColumnOrder = DTColumnOrder(column_index=0, is_asc=False)
    assert order is not None
    assert isinstance(order, DTColumnOrder)
    assert order.column_index == 0
    assert order.is_asc is False


def test_dt_column_order_no_param() -> None:
    with pytest.raises(ValueError):
        DTColumnOrder()


def test_dt_column_order_default_order() -> None:
    order: DTColumnOrder = DTColumnOrder(column_index=0)
    assert order.is_asc is True


if __name__ == '__main__':
    pytest.main()
