import pytest

from datatables.base import DTParams


def test_dt_params_new() -> None:
    dt_params: DTParams = DTParams(
        draw=333, start=25, length=50, search_value='foo', search_regex=True, columns=[], order=[]
    )
    assert dt_params is not None
    assert isinstance(dt_params, DTParams)
    assert dt_params.draw == 333
    assert dt_params.start == 25
    assert dt_params.length == 50
    assert dt_params.search_value == 'foo'
    assert dt_params.search_regex is True
    assert not dt_params.columns
    assert not dt_params.order


def test_dt_params_no_params() -> None:
    dt_params: DTParams = DTParams()
    assert dt_params.draw == 0
    assert dt_params.start == 0
    assert dt_params.length == 10
    assert dt_params.search_value == ''
    assert dt_params.search_regex is False
    assert not dt_params.columns
    assert not dt_params.order


if __name__ == '__main__':
    pytest.main()
