# sqlalchemy2-datatables

[![versions](https://img.shields.io/pypi/pyversions/sqlalchemy2-datatables.svg)](https://github.com/hniedner/sqlalchemy2-datatables)
[![license](https://img.shields.io/github/license/pydantic/pydantic.svg)](https://github.com/pydantic/pydantic/blob/main/LICENSE)
[![Python package](https://github.com/coding-doc/sqlalchemy2-datatables/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/coding-doc/sqlalchemy2-datatables/actions/workflows/python-package.yml)
---

**Source Code**: [https://github.com/coding-doc/sqlalchemy2-datatables](https://github.com/coding-doc/sqlalchemy2-datatables)

---
### Summary
sqlalchemy2-datatables is a framework agnostic library providing an SQLAlchemy integration of
jQuery DataTables >= 1.10, and helping you manage server side requests in your application.

### Inspiration
This project was inspired by [sqlalchemy-datatables](https://github.com/Pegase745/sqlalchemy-datatables)
developed by Michel Nemnom aka [Pegase745](https://github.com/Pegase745).

### Motivation
Given the sunstantial changes with SQLAlchemy 2.0 most of not all of the SQLAlchemy based datatables serverside
 solution will be outdated soon (labeit currently still supported in SQLAlchemy 1.4). Specifically deprecation of
 sqlalchemy.orm.Query will render those packages obsolete.
[SQLAlchemy2.0](https://docs.sqlalchemy.org/en/20/).

### Installation
```shell
pip install sqlalchemy2-datatables
```

### Examples
Generic CRUD style function:
```python
from typing import Any
from sqlalchemy import Engine
from sqlalchemy import FromClause

from datatables import DataTable
from datatables.base import DTDataCallbacks

def get_datatable_result(
    params: dict[str, Any],
    table: FromClause,
    column_names: list[str],
    engine: Engine,
    callbacks: DTDataCallbacks | None,
) -> dict[str, Any]:
    """
    Get database results specifically formatted for a display via jQuery datatables.
    :param params: dict - request parameters
    :param table: FromClause - the sqlalchemy from clause
    :param column_names - List of column names reflecting the table columns in the desired order
    :param engine: Engine -  the sqlalchemy engine
    :param callbacks - datatables callbacks to populate jQuery datatables DT_* attributes
    :return dict with DataTable output for the jQuery datatables in the frontend view
    """
    datatable: DataTable = DataTable(
        request_params=params,
        table=table,
        column_names=column_names,
        engine=engine,
        callbacks=callbacks
    )
    return datatable.output_result()
```
The output dictionary that can be serialized and returned to jQuery datatables.
```python
{
    "start": 0,
    "length": 5,
    "draw": 1,
    "recordsTotal": 1000,
    "recordsFiltered": 1000,
    "data": [
        {
            "id": 1,
            "col1": "value",
            "col2": "value",
            "col3": "value",
            "col4": "value",
        },
        {
            "id": 2,
            "col1": "value",
            "col2": "value",
            "col3": "value",
            "col4": "value",
        },
        {
            "id": 3,
            "col1": "value",
            "col2": "value",
            "col3": "value",
            "col4": "value",
        },
        {
            "id": 4,
            "col1": "value",
            "col2": "value",
            "col3": "value",
            "col4": "value",
        },
        {
            "id": 5,
            "col1": "value",
            "col2": "value",
            "col3": "value",
            "col4": "value",
        },
    ],
}
```
